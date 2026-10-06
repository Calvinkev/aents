# Tool Ecosystem & Permission Control

AENTS tools are registered in `ToolRegistry` with strict permission hierarchy:

| Permission Level | Description | Example Tools |
|---|---|---|
| `READ_ONLY` | Read-only inspection operations | `list_files`, `read_file`, `git_status`, `query_database` (read-only) |
| `SAFE_WRITE` | Safe modification operations | `write_file`, `execute_command` (sandboxed), `http_request` |
| `DANGEROUS_WRITE` | Destructive or impactful operations | `commit_changes`, `delete_file` (Requires HITL approval) |
| `ADMIN` | Administrative system commands | `deploy` (Requires HITL approval) |
