"""Run with python3 -m unittest discover -s eval/prismatic."""

import json
from pathlib import Path
import subprocess
import sys
import unittest


HOOK = Path(__file__).resolve().parents[2] / "skills/prismatic/hooks/block-raw-prism.py"


def run_hook(command, tool="Bash", event_name="PreToolUse"):
    event = {"hook_event_name": event_name, "tool_name": tool,
             "tool_input": {"command": command}}
    result = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(event),
                            text=True, capture_output=True, check=True)
    return json.loads(result.stdout) if result.stdout else None


class PrismGuardTest(unittest.TestCase):
    def test_blocks_raw_calls_in_both_agents(self):
        commands = [
            "prism integrations list",
            "prism integrations list --read-only",
            "/opt/homebrew/bin/prism integrations delete id --yes",
            "command prism me",
            "env PRISM_READ_ONLY=false prism me",
            "echo ready && prism me",
            "echo ready\nprism me",
            "bash wrapper/prism-read-only.sh me; prism me",
            "bash -lc 'prism me'",
            "echo $(prism me)",
            'echo "$(prism me)"',
            '"pri"sm me',
            r"p\rism me",
            "npx --yes @prismatic-io/prism@11 me",
            "pnpm exec prism me",
            "node /some/node_modules/@prismatic-io/prism/lib/run.js me",
            ["zsh", "-lc", "prism me"],
        ]
        for tool in ["Bash", "exec_command"]:
            for command in commands:
                with self.subTest(tool=tool, command=command):
                    result = run_hook(command, tool)
                    self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_preserves_normal_approval_flow(self):
        commands = [
            "git status --short",
            'bash "$PRISM_AGENT_CLI" me --agent --format json',
            "bash /skills/prismatic/scripts/prism-read-only.sh me",
            "bash /skills/prismatic/scripts/prism-read-only.sh graphql query "
            "'query { customers { nodes { id name } } }'",
            "echo ready # prism me",
            'printf "%s\\n" "hello world"',
            "if true; then echo fine; fi",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNone(run_hook(command))

    def test_uninspectable_shell_input_is_denied(self):
        for command in [None, 7, "bash 'unfinished"]:
            with self.subTest(command=command):
                result = run_hook(command)
                self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_does_not_interfere_with_other_tools_or_events(self):
        self.assertIsNone(run_hook("prism me", tool="Read"))
        self.assertIsNone(run_hook("prism me", event_name="PostToolUse"))

    def test_conservative_inspection_rejects_quoted_raw_examples(self):
        result = run_hook("echo 'prism me'")
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
