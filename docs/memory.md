# Memory System & Persistence

AENTS implements a dual memory model:
- **Short-Term Execution Memory**: Maintains active subtask states, intermediate tool outputs, and validation reports during task execution.
- **Long-Term Memory**: Persists routing metrics, success rates, failure signatures, and audit logs to SQLAlchemy (SQLite/PostgreSQL).
