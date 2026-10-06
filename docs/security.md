# Security Controls & Prompt Injection Defense

## 1. Prompt Injection Defenses
- Strict boundary separation between System instructions, User tasks, Context, and Untrusted tool outputs.
- Outer wrapping and sanitization of tags in `PromptBuilder.wrap_untrusted_data`.

## 2. Tool Permission & Sandboxing
- Workspace root boundary checks preventing path traversal (`../` escapes).
- SSRF protection blocking local metadata IPs (`169.254.169.254`, `metadata.google.internal`).
- Command allow/deny policies blocking destructive shell execution (`rm -rf /`, `mkfs`, `dd`).
