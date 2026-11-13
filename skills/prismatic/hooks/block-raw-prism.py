#!/usr/bin/env python3
"""Catch literal Prism CLI calls in Claude Code and Codex PreToolUse events.

This checks common shell command positions, not arbitrary programs or expansions.
No command text or credentials are logged, and inspected input is never executed.
"""

import json
import re
import shlex
import sys


ASSIGNMENT = re.compile(r"[a-zA-Z_][a-zA-Z_0-9]*=")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}


def without_heredoc_bodies(command):
    """Leave heredoc data out of command inspection, including quoted delimiters."""
    output, pending = [], []
    for line in command.splitlines(keepends=True):
        if pending:
            delimiter, strip_tabs = pending[0]
            candidate = line.rstrip("\r\n")
            if (candidate.lstrip("\t") if strip_tabs else candidate) == delimiter:
                pending.pop(0)
            output.append("\n")
            continue
        output.append(line)
        try:
            lexer = shlex.shlex(line, posix=False, punctuation_chars="<>")
            lexer.whitespace_split = True
            words = list(lexer)
            for index, word in enumerate(words[:-1]):
                if word == "<<":
                    delimiter = words[index + 1]
                    strip_tabs = delimiter.startswith("-")
                    if strip_tabs:
                        delimiter = delimiter[1:] or words[index + 2]
                    pending.append((shlex.split(delimiter)[0], strip_tabs))
        except (ValueError, IndexError):
            # An incomplete line can be part of a multiline quoted argument.
            continue
    return "".join(output)


def invokes_prism(words, depth):
    """Inspect executable positions and explicit shell -c bodies, not prose args."""
    while words:
        name = words[0].rsplit("/", 1)[-1]
        if ASSIGNMENT.match(words[0]):
            words = words[1:]
            continue
        if name in {"prism", "prism.cmd", "prism.exe"}:
            return True
        if name in {"command", "builtin", "exec", "env", "sudo", "nohup"}:
            words = words[1:]
            if name == "command" and any(w in {"-v", "-V"} for w in words):
                return False  # Executable lookup does not run the CLI.
            while words and words[0].startswith("-"):
                option = words.pop(0)
                if option in {"-u", "--unset", "--user", "-g", "--group", "-a"} and words:
                    words.pop(0)
            continue
        if name in SHELLS:
            for index, word in enumerate(words[1:], 1):
                if word.startswith("-") and "c" in word and index + 1 < len(words):
                    return contains_prism(words[index + 1], depth + 1)
                if not word.startswith("-"):
                    break  # A script path is not a shell -c command string.
        if name in {"npx", "pnpm", "npm", "yarn"}:
            args = words[1:]
            if name != "npx":
                if not args or args[0] not in {"exec", "dlx"}:
                    return False
                args = args[1:]
            while args and args[0].startswith("-"):
                option = args.pop(0)
                if option in {"-p", "--package", "-c", "--call"} and args:
                    args.pop(0)
            return bool(args and (args[0].rsplit("/", 1)[-1] == "prism" or
                                  re.fullmatch(r"@prismatic-io/prism(?:@[^\s]+)?", args[0])))
        if name in {"node", "nodejs"}:
            for word in words[1:]:
                if word in {"-e", "--eval", "-p", "--print"}:
                    return False
                if not word.startswith("-"):
                    return "@prismatic-io/prism/" in word
        return False
    return False


def contains_prism(command, depth=0):
    if depth > 8:
        return False
    lexer = shlex.shlex(without_heredoc_bodies(command), posix=True,
                        punctuation_chars="();&|<>\n")
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    words, skip_redirect = [], False
    for token in lexer:
        if token and all(c in ";&|()\n" for c in token):
            if invokes_prism(words, depth):
                return True
            words, skip_redirect = [], False
        elif token and all(c in "<>" for c in token):
            skip_redirect = True
        elif skip_redirect:
            skip_redirect = False
        elif not words and token in {"if", "then", "else", "elif", "while", "until", "do", "!", "{"}:
            continue
        else:
            words.append(token)
    return invokes_prism(words, depth)


def deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}))


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("Expected a hook event object")
        if event.get("hook_event_name") != "PreToolUse":
            return
        if event.get("tool_name") not in {"Bash", "exec_command", "shell_command", "shell"}:
            return
        tool_input = event.get("tool_input")
        if not isinstance(tool_input, dict):
            raise ValueError("Expected shell tool input")
        command = tool_input.get("command", tool_input.get("cmd"))
        if isinstance(command, list) and all(isinstance(arg, str) for arg in command):
            command = shlex.join(command)
        if not isinstance(command, str):
            raise ValueError("Expected shell command text")
        if contains_prism(command):
            deny("Direct Prism CLI use is blocked. Read the prismatic skill and use "
                 "bash <skill-directory>/scripts/prism-read-only.sh for every call. "
                 "Do not bypass the wrapper with npx, a package entry point, or raw HTTP.")
    except (ValueError, TypeError, RecursionError):
        # This is a convenience guard. Unrecognized syntax must not block
        # unrelated work or approve it; leave the normal permission flow intact.
        return


if __name__ == "__main__":
    main()
