# AENTS Production Architecture

## Overview
AENTS is a production-oriented AI agent orchestration platform designed for autonomous task decomposition, parallel execution, tool interaction, validation, and failure recovery.

```
                    USER / API / CLI
                           |
                           v
                    TASK INTAKE API
                           |
                           v
                    ORCHESTRATOR
                           |
             +-------------+-------------+
             |                           |
             v                           v
          PLANNER                    MEMORY
             |
             v
           ROUTER
             |
     +-------+-------+-------+-------+
     |       |       |       |       |
     v       v       v       v       v
  Research  Code    Data   Security  General
   Agent    Agent   Agent    Agent     Agent
     |       |       |       |       |
     +-------+-------+-------+-------+
             |
             v
          TOOLS
             |
     +-------+--------+---------+---------+
     |       |        |         |         |
   GitHub  Filesystem Shell   HTTP/API  Database
             |
             v
         VALIDATOR
             |
       +-----+------+
       |            |
     PASS          FAIL
       |            |
       v            v
  INTEGRATOR    REFINER
       |            |
       |       retry/fallback
       |            |
       +-----+------+
             |
             v
         OPTIMIZER
             |
             v
       FINAL RESPONSE
             |
             v
      TRACE + MEMORY
```

## Core Flow
1. **Intake**: CLI/API accepts user task and initializes trace IDs and budget tracking.
2. **Planning**: `PlannerAgent` uses LLM reasoning to decompose task into a Directed Acyclic Graph (DAG) of subtasks with explicit dependencies.
3. **Routing**: `RouterAgent` evaluates candidate agents based on capabilities, success rate, cost, latency, and current workload.
4. **Execution**: Routed specialist agents execute bounded tool loops with `ToolRegistry`.
5. **Validation**: `ValidatorAgent` runs structural, evidence, and rule checks.
6. **Refinement & Recovery**: Soft failures trigger targeted prompt refinement via `CriticRefinerAgent`. Hard failures activate circuit breakers and fallbacks in `FailureHandler`.
