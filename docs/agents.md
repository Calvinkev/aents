# Specialist Agents Specification

AENTS includes six production specialist agents extending `BaseAgent`:

| Agent ID | Capabilities | Key Responsibilities |
|---|---|---|
| `research_specialist` | `research`, `document_analysis`, `fact_checking` | Document inspection, evidence collection, factual summaries |
| `coding_specialist` | `code_analysis`, `refactoring`, `bug_fix`, `patch_application` | Source code reasoning, bug fixes, test execution, patch writing |
| `debugging_specialist` | `root_cause_analysis`, `log_inspection`, `reproduction` | Failure reproduction, log inspection, root cause identification |
| `security_specialist` | `vulnerability_scan`, `auth_audit`, `secret_detection` | Security auditing, authentication review, secret scanner |
| `data_specialist` | `data_analysis`, `anomaly_detection`, `metrics_computation` | Structured dataset analysis, metrics calculation, anomaly reports |
| `general_specialist` | `general_reasoning`, `summarization`, `task_coordination` | Fallback agent for unclassified tasks |
