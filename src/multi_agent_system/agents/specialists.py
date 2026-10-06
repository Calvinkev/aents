from __future__ import annotations

import asyncio
from .base import AgentResult, BaseAgent
from ..models import CandidateResult, Subtask


class ResearchAgent(BaseAgent):
    name = "research_specialist"
    description = "Specialist in factual research and document analysis."
    capabilities = ["research", "document_analysis", "evidence_summarization"]


class CodingAgent(BaseAgent):
    name = "coding_specialist"
    description = "Specialist in source code inspection, refactoring, and bug fixes."
    capabilities = ["code_analysis", "refactoring", "bug_fix", "test_execution", "coding"]


class DebuggingAgent(BaseAgent):
    name = "debugging_specialist"
    description = "Specialist in root cause analysis and reproduction."
    capabilities = ["root_cause_analysis", "log_inspection", "debugging"]


class SecurityAgent(BaseAgent):
    name = "security_specialist"
    description = "Specialist in security auditing and secret detection."
    capabilities = ["vulnerability_scan", "auth_audit", "security"]


class DataAgent(BaseAgent):
    name = "data_specialist"
    description = "Specialist in structured data analysis."
    capabilities = ["data_analysis", "anomaly_detection"]


class GeneralAgent(BaseAgent):
    name = "general_specialist"
    description = "Generalist agent for broad subtasks."
    capabilities = ["general_reasoning", "summarization"]


class LegacySpecialistAdapter:
    def __init__(self, real_agent: BaseAgent):
        self.real_agent = real_agent
        self.name = real_agent.name

    def execute(self, subtask: Subtask, guidance: str = "") -> CandidateResult:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        res = loop.run_until_complete(self.real_agent.run("legacy-task", subtask.id, subtask.objective, guidance=guidance))
        return CandidateResult(
            subtask_id=subtask.id,
            content=res.output,
            evidence=res.evidence,
            confidence=res.confidence,
            estimated_cost=res.estimated_cost,
            estimated_latency_ms=res.latency_ms,
            metadata={"agent_id": res.agent_id, "tokens_used": res.tokens_used},
        )


ResearchSpecialist = lambda: ResearchAgent()
CodingSpecialist = lambda: CodingAgent()
DebuggingSpecialist = lambda: DebuggingAgent()
SecuritySpecialist = lambda: SecurityAgent()
DataSpecialist = lambda: DataAgent()
GeneralSpecialist = lambda: GeneralAgent()
AnalysisSpecialist = lambda: ResearchAgent()
SynthesisSpecialist = lambda: GeneralAgent()
