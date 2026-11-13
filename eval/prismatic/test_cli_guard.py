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
            '"pri"sm me',
            r"p\rism me",
            "npx --yes @prismatic-io/prism@11 me",
            "pnpm exec prism me",
            "node /some/node_modules/@prismatic-io/prism/lib/run.js me",
            ["zsh", "-lc", "prism me"],
            "if true; then prism me; fi",
            "cat <<'EOF'\njust text\nEOF\nprism me",
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
            "echo prism",
            "echo 'prism me'",
            "cat notes/prismatic.md",
            "rg prism worklog.md",
            "command -v prism",
            'worklog edit entry-id --headline "I investigated Prismatic\'s inventory sync (prism CLI)."',
            "pbcopy <<'EOF'\nworklog edit entry-id --headline \"Prismatic's CLI (prism)\"\nEOF\n",
            "pbcopy <<-'EOF'\n\tprism me\n\tEOF\n",
            "cat <<'FIRST' <<'SECOND'\nprism me\nFIRST\nprism me\nSECOND\n",
            "npm install --global @prismatic-io/prism@11",
            "npx prettier --write notes/prismatic.md",
            "npx some-tool 'prism me'",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNone(run_hook(command))

    def test_uninspectable_shell_input_preserves_normal_permissions(self):
        for command in [None, 7, "bash 'unfinished"]:
            with self.subTest(command=command):
                self.assertIsNone(run_hook(command))

    def test_does_not_interfere_with_other_tools_or_events(self):
        self.assertIsNone(run_hook("prism me", tool="Read"))
        self.assertIsNone(run_hook("prism me", event_name="PostToolUse"))

    def test_clipboard_and_worklog_regression(self):
        command = '''pbcopy <<'EOF'
worklog edit 3f4945cf-04d5-4892-9e61-3a64ccb846dc --headline "I directed a high-effort AI investigation into how channel inventory syncs read Prismatic's configuration."
EOF
'''
        self.assertIsNone(run_hook(command))

    def test_only_shell_execution_arguments_are_recursively_inspected(self):
        self.assertIsNone(run_hook("worklog entry 'bash -lc prism me'"))
        self.assertIsNone(run_hook("node -e 'console.log(\"prism me\")'"))


if __name__ == "__main__":
    unittest.main()
