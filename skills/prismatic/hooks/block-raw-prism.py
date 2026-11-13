#!/usr/bin/env python3
"""Catch literal Prism CLI calls in Claude Code and Codex PreToolUse events.

This is conservative command-text inspection, not a shell interpreter or sandbox.
No command text or credentials are logged, and inspected input is never executed.
"""

import json
import re
import shlex
import sys


def contains_prism(command, depth=0):
    if depth > 8:
        raise ValueError("Shell nesting exceeds the hook's inspection limit")
    lexer = shlex.shlex(command, posix=True, punctuation_chars="();&|<>`{}")
    lexer.whitespace_split = True
    for token in lexer:
        # Quoting and escapes are normalized by shlex. Inspect each token,
        # rather than exempting a whole command that also mentions the wrapper.
        name = token.rsplit("/", 1)[-1]
        if name in {"prism", "prism.cmd", "prism.exe"}:
            return True
        if re.fullmatch(r"@prismatic-io/prism(?:@[^\s]+)?", token):
            return True
        if "@prismatic-io/prism/" in token:
            return True
        # Shell -c strings and command substitutions can hide another command
        # inside a token. This can also reject quoted examples of raw commands.
        if (not all(char in "();&|<>`{}" for char in token)
                and any(char.isspace() or char in "();&|<>`{}" for char in token)):
            if contains_prism(token, depth + 1):
                return True
    return False


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
        deny("The Prism guard could not inspect this shell call. Split it into "
             "simple commands and use the prismatic skill's read-only wrapper.")


if __name__ == "__main__":
    main()
