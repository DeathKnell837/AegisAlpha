# src/models.py
import os
import re
from typing import Any, List, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_openai import ChatOpenAI
from src.config import get_config

DEFAULT_PLANNER_MODEL = "Qwen/Qwen2.5-32B-Instruct"
DEFAULT_EXECUTOR_MODEL = "Qwen/Qwen2.5-32B-Instruct"
DEFAULT_REVIEWER_MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

class MockChatModel(BaseChatModel):
    role: str
    model_name: str

    @property
    def _llm_type(self) -> str:
        return f"mock-chat-model-{self.role}"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        content = self._get_mock_response(messages)
        gen = ChatGeneration(message=AIMessage(content=content))
        return ChatResult(generations=[gen])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        content = self._get_mock_response(messages)
        gen = ChatGeneration(message=AIMessage(content=content))
        return ChatResult(generations=[gen])

    def _get_mock_response(self, messages: List[BaseMessage]) -> str:
        if self.role == "planner":
            contract_name = "Mutual NDA"
            frameworks_str = "GDPR, CCPA/CPRA, HIPAA, SOC 2, SOX, AML/KYC"
            for m in reversed(messages):
                c_text = getattr(m, "content", "") or ""
                if not isinstance(c_text, str):
                    continue
                if "CONTRACT NAME:" in c_text:
                    m_name = re.search(r"CONTRACT NAME:\s*(.*)", c_text, re.IGNORECASE)
                    if m_name:
                        contract_name = m_name.group(1).strip()
                if "compliance against" in c_text:
                    m_fw = re.search(r"compliance against\s+([^.\n]+)", c_text, re.IGNORECASE)
                    if m_fw:
                        frameworks_str = m_fw.group(1).strip()

            fws = [f.strip() for f in frameworks_str.split(",")]
            return f"""@rogiebacanto2002/executor-agent Compliance plan created

**AUDIT SCOPE**
- Contract: {contract_name}
- Type: NDA
- Jurisdiction(s): North Korea
- Frameworks: {", ".join(fws)}
- Risk tolerance: High

**COMPLIANCE AUDIT PLAN**
CP-01 — Clause 1 | Rule: GDPR Article 10 | PASS if: The agreement clearly defines the purpose and scope of the disclosure of confidential information. | FLAG if: The agreement lacks clarity on the purpose and scope.
CP-02 — Clause 3 | Rule: GDPR Article 10 | PASS if: Confidential Information is clearly defined and includes both oral and written disclosures. | FLAG if: Confidential Information is not adequately defined.
CP-03 — Clause 5 | Rule: GDPR Article 10 | PASS if: The Receiving Party is obligated to hold Confidential Information in strict confidence and not disclose it without prior written consent. | FLAG if: The Receiving Party is not obligated to hold Confidential Information in strict confidence.
CP-04 — Clause 6 | Rule: GDPR Article 10 | PASS if: The Receiving Party agrees to take reasonable steps to protect the confidentiality of the Confidential Information. | FLAG if: The Receiving Party does not agree to take reasonable steps to protect the confidentiality of the Confidential Information.
CP-05 — Clause 7 | Rule: GDPR Article 10 | PASS if: The Receiving Party is permitted to disclose Confidential Information to its employees and agents who need to know such information for the purposes of this Agreement. | FLAG if: The Receiving Party is not permitted to disclose Confidential Information to its employees and agents.
CP-06 — Clause 8 | Rule: GDPR Article 10 | PASS if: The Receiving Party agrees to return or destroy all Confidential Information upon termination of this Agreement. | FLAG if: The Receiving Party does not agree to return or destroy all Confidential Information upon termination of this Agreement.
CP-07 — Clause 9 | Rule: GDPR Article 10 | PASS if: The Receiving Party acknowledges that the Confidential Information is proprietary and valuable. | FLAG if: The Receiving Party does not acknowledge that the Confidential Information is proprietary and valuable.
CP-08 — Clause 10 | Rule: GDPR Article 10 | PASS if: The Receiving Party agrees to notify the Disclosing Party immediately upon discovery of any unauthorized use or disclosure of Confidential Information. | FLAG if: The Receiving Party does not agree to notify the Disclosing Party immediately upon discovery of any unauthorized use or disclosure of Confidential Information.
CP-09 — Clause 11 | Rule: GDPR Article 10 | PASS if: The Receiving Party agrees to cooperate with the Disclosing Party in any investigation of unauthorized use or disclosure of Confidential Information. | FLAG if: The Receiving Party does not agree to cooperate with the Disclosing Party in any investigation of unauthorized use or disclosure of Confidential Information.
CP-10 — Clause 12 | Rule: GDPR Article 10 | PASS if: The Receiving Party agrees to indemnify and hold harmless the Disclosing Party from any claims arising out of the Receiving Party's breach of this Agreement. | FLAG if: The Receiving Party does not agree to indemnify and hold harmless the Disclosing Party from any claims arising out of the Receiving Party's breach of this Agreement.
CP-11 — Clause 13 | Rule: GDPR Article 10 | PASS if: The Receiving Party agrees to comply with all applicable laws and regulations related to the protection of Confidential Information. | FLAG if: The Receiving Party does not agree to comply with all applicable laws and regulations related to the protection of Confidential Information.
CP-12 — Clause 14 | Rule: GDPR Article 10 | PASS if: The Receiving Party agrees to limit the use of Confidential Information solely for the purposes set forth in this Agreement. | FLAG if: The Receiving Party does not agree to limit the use of Confidential Information solely for the purposes set forth in this Agreement.
CP-13 — Clause 15 | Rule: GDPR Article 10 | PASS if: The Receiving Party agrees that monetary damages may be insufficient and that the Disclosing Party shall be entitled to seek injunctive relief in the event of a breach. | FLAG if: The Receiving Party does not agree that monetary damages may be insufficient and that the Disclosing Party shall be entitled to seek injunctive relief in the event of a breach.
CP-14 — Clause 16 | Rule: GDPR Article 10 | PASS if: This Agreement shall be governed by and construed in accordance with the Laws of North Korea, without regard to its conflict of laws principles. | FLAG if: This Agreement is not governed by and construed in accordance with the Laws of North Korea.
CP-15 — Clause 17 | Rule: GDPR Article 10 | PASS if: This Agreement constitutes the entire understanding between the Parties and supersedes all prior agreements relating to the subject matter herein. | FLAG if: This Agreement does not constitute the entire understanding between the Parties and does not supersede all prior agreements relating to the subject matter herein.
CP-16 — Clause 18 | Rule: GDPR Article 10 | PASS if: No modification of this Agreement shall be effective unless made in writing and signed by both Parties. | FLAG if: Modifications can be made without written consent.
CP-17 — Clause 19 | Rule: GDPR Article 10 | PASS if: If any provision of this Agreement is held invalid, the remaining provisions shall continue in full force and effect. | FLAG if: The remaining provisions do not continue in full force and effect.
CP-18 — Clause 20 | Rule: GDPR Article 10 | PASS if: This Agreement may be executed in counterparts, each of which shall be deemed an original and all of which together shall constitute one instrument. | FLAG if: This Agreement cannot be executed in counterparts.

**HANDOFF NOTES**
Please review the full contract text and ensure all clauses are thoroughly examined against the specified compliance rules and regulations. Pay special attention to the jurisdictional implications and the risk tolerance level provided.

@rogiebacanto2002/executor-agent Please execute the COMPLIANCE AUDIT PLAN above with line-by-line analysis and return your findings."""

        elif self.role == "executor":
            contract_name = "Mutual NDA"
            for m in reversed(messages):
                c_text = getattr(m, "content", "") or ""
                if not isinstance(c_text, str):
                    continue
                if "Contract:" in c_text:
                    m_name = re.search(r"Contract:\s*(.*)", c_text, re.IGNORECASE)
                    if m_name:
                        contract_name = m_name.group(1).strip()
                        break

            return f"""**ANALYSIS SUMMARY**
- Contract: {contract_name}
- Checkpoints evaluated: 18 / 18
- Severity counts: CRITICAL 0 · HIGH 1 · MEDIUM 1 · LOW 0 · COMPLIANT 16

**FINDINGS**
F-01 | CP-01 | §1 | Severity: COMPLIANT
   Text: "This Mutual Non-Disclosure Agreement (\\"Agreement\\") is entered into as of January 15, 2025"
   Confidence: 100%
   Rationale: Defines the parties and date clearly.
F-02 | CP-02 | §3 | Severity: COMPLIANT
   Text: "\\"Confidential Information\\" means any non-public information disclosed by one Party to the other"
   Confidence: 95%
   Rationale: Adequately defines confidential information.
F-03 | CP-03 | §5 | Severity: COMPLIANT
   Text: "The Receiving Party shall hold the Confidential Information in strict confidence"
   Confidence: 100%
   Rationale: Properly holds information in confidence.
F-04 | CP-04 | §6 | Severity: COMPLIANT
   Text: "The Receiving Party shall use the same degree of care to protect the Confidential Information as it uses to protect its own"
   Confidence: 100%
   Rationale: Standard of care meets reasonable requirement.
F-05 | CP-05 | §7 | Severity: COMPLIANT
   Text: "The Receiving Party may disclose Confidential Information to its employees and agents who have a need to know"
   Confidence: 95%
   Rationale: Permitted disclosures are restricted.
F-06 | CP-06 | §11 | Severity: COMPLIANT
   Text: "Upon termination or upon request, the Receiving Party shall promptly return or destroy all Confidential Information"
   Confidence: 95%
   Rationale: Disposal/destruction obligation is clear.
F-07 | CP-07 | §2 | Severity: COMPLIANT
   Text: "The Parties wish to explore a potential business relationship"
   Confidence: 90%
   Rationale: Acknowledges the value and purpose.
F-08 | CP-08 | §8 | Severity: COMPLIANT
   Text: "If the Receiving Party is required by law to disclose Confidential Information, it shall provide prompt written notice"
   Confidence: 90%
   Rationale: Requires notice of compelled disclosure.
F-09 | CP-09 | §8 | Severity: COMPLIANT
   Text: "allow the Disclosing Party to seek a protective order."
   Confidence: 85%
   Rationale: Cooperates in seeking protection.
F-10 | CP-10 | §14 | Severity: COMPLIANT
   Text: "Neither Party limits its liability for any indirect damages under this Agreement"
   Confidence: 90%
   Rationale: Indemnity is present via broad liability clause.
F-11 | CP-11 | §14 | Severity: HIGH
   Text: "Neither Party limits its liability for any indirect damages under this Agreement, and each Party shall remain fully responsible for all consequential, incidental, and special damages of any kind."
   Confidence: 90%
   Rationale: Total absence of a liability cap is a high risk.
F-12 | CP-12 | §5 | Severity: COMPLIANT
   Text: "shall hold the Confidential Information in strict confidence and shall not disclose it to any third party"
   Confidence: 100%
   Rationale: Limits use solely to the purpose.
F-13 | CP-13 | §15 | Severity: COMPLIANT
   Text: "the Disclosing Party shall be entitled to seek injunctive relief in the event of a breach"
   Confidence: 100%
   Rationale: Acknowledges that monetary damages are insufficient.
F-14 | CP-14 | §16 | Severity: MEDIUM
   Text: "This Agreement shall be governed by and construed in accordance with the Laws of North Korea"
   Confidence: 95%
   Rationale: Governing law set to North Korea introduces substantial enforcement risks.
F-15 | CP-15 | §17 | Severity: COMPLIANT
   Text: "This Agreement constitutes the entire understanding between the Parties"
   Confidence: 100%
   Rationale: Entire agreement clause is standard.
F-16 | CP-16 | §18 | Severity: COMPLIANT
   Text: "No modification of this Agreement shall be effective unless made in writing"
   Confidence: 100%
   Rationale: Modifications require written consent.
F-17 | CP-17 | §19 | Severity: COMPLIANT
   Text: "If any provision of this Agreement is held invalid, the remaining provisions shall continue in full force"
   Confidence: 100%
   Rationale: Severability clause is standard.
F-18 | CP-18 | §20 | Severity: COMPLIANT
   Text: "This Agreement may be executed in counterparts"
   Confidence: 100%
   Rationale: Counterparts execution is allowed.

**HANDOFF NOTES**
Reviewed Mutual NDA. Missing liability cap is HIGH risk. Governing law of North Korea is MEDIUM risk.

@rogiebacanto2002/reviewer-agent Please review the FINDINGS above, validate severities, and issue the final compliance verdict."""

        elif self.role == "reviewer":
            contract_name = "Mutual NDA"
            for m in reversed(messages):
                c_text = getattr(m, "content", "") or ""
                if not isinstance(c_text, str):
                    continue
                if "Contract:" in c_text:
                    m_name = re.search(r"Contract:\s*(.*)", c_text, re.IGNORECASE)
                    if m_name:
                        contract_name = m_name.group(1).strip()
                        break

            return f"""**COMPLIANCE VERDICT**
- Contract: {contract_name}
- Overall Status: Approved with Conditions
- Risk Score: 75 / 100
- Risk Band: HIGH

**EXECUTIVE SUMMARY**
LexAudit completed the compliance audit for {contract_name}. The audit revealed a high risk due to the total lack of a liability cap, exposing both parties to unlimited consequential damages. Additionally, a medium risk was flagged regarding the choice of North Korean law as the governing jurisdiction, which poses significant enforcement and regulatory challenges. The agreement is Approved with Conditions, requiring the incorporation of a standard mutual liability limitation and a transition to a standard jurisdiction.

**FINALIZED FINDINGS**
F-11 | §14 | Verdict: CHALLENGED | Severity: HIGH
   Confidence: 90% | Executor Confidence: 90%
   Rationale: The total absence of a liability cap is confirmed as a major exposure.
   Devil's Advocate: While unlimited liability holds both parties responsible, it creates asymmetric risk for the party sharing more info.
   Estimated Exposure: $100,000–$500,000
   Recommendation: Negotiate a mutual cap on liability, e.g., $1,000,000 or 12 months fees.
F-14 | §16 | Verdict: CONFIRMED | Severity: MEDIUM
   Confidence: 95% | Executor Confidence: 95%
   Rationale: Governing law of North Korea is highly irregular and problematic.
   Devil's Advocate: Enforcement in North Korean courts is practically impossible for foreign entities.
   Recommendation: Change governing law to a neutral, standard jurisdiction like New York, Delaware, or England & Wales.

**AUDIT TRACE LOG**
- 2026-06-18T23:42:00.000000 | validate | F-11 confirmed with Devil's Advocate challenge
- 2026-06-18T23:42:01.000000 | validate | F-14 confirmed
- 2026-06-18T23:42:02.000000 | finalize | Verdict issued: APPROVED_WITH_CONDITIONS

@Rogie FINAL COMPLIANCE VERDICT logged above. No further agent action required."""

        return "Unknown role mock response"

def get_model_for_role(role: str) -> Any:
    """
    Returns a configured model mapping to the specified role.
    If USE_MOCK_LLM=true, returns a MockChatModel.
    Otherwise, routes through Featherless.ai.
    """
    if os.getenv("USE_MOCK_LLM", "false").lower() == "true":
        return MockChatModel(role=role, model_name="Mock-Qwen-2.5-32B")

    cfg = get_config()
    if role == "reviewer":
        model_name = os.getenv("REVIEWER_MODEL", DEFAULT_REVIEWER_MODEL)
        return ChatOpenAI(
            model=model_name,
            base_url="https://api.aimlapi.com/v1",
            api_key=cfg.aimlapi_key,
            temperature=0.1,
            disable_streaming=True,
            max_retries=5,
            timeout=120,
        )
    elif role == "planner":
        model_name = os.getenv("PLANNER_MODEL", DEFAULT_PLANNER_MODEL)
    elif role == "executor":
        model_name = os.getenv("EXECUTOR_MODEL", DEFAULT_EXECUTOR_MODEL)
    else:
        raise ValueError(f"Unknown role for model mapping: {role}")

    return ChatOpenAI(
        model=model_name,
        base_url="https://api.featherless.ai/v1",
        api_key=cfg.featherless_api_key,
        temperature=0.1,
        disable_streaming=True,
        max_retries=5,
        timeout=120,
    )
