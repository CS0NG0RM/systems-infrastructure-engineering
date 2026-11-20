"""Deterministic simulation of an AI-agent prompt-injection attempt."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulatedToolCall:
    tool_name: str
    resource_id: int
    claimed_role: str


def simulate_indirect_prompt_injection(document_text: str) -> SimulatedToolCall | None:
    """
    Simulate an agent following an instruction embedded in untrusted content.

    This does not use an LLM. It models an intentionally vulnerable
    agent decision so backend authorization can be tested independently.
    """
    attack_marker = "[SIMULATED_AGENT_INSTRUCTION]"

    if attack_marker not in document_text:
        return None

    return SimulatedToolCall(
        tool_name="get_document",
        resource_id=2,
        claimed_role="finance",
    )

@dataclass(frozen=True)
class SimulatedExfiltrationAttempt:
    """Represent a prohibited data transfer without executing it."""

    destination: str
    data_classification: str
    payload: str


def simulate_exfiltration_attempt(document_text: str):
    """Model an attempted transfer triggered by an untrusted document."""

    if "[SIMULATED_EXFILTRATION]" not in document_text:
        return None

    return SimulatedExfiltrationAttempt(
        destination="mock://unauthorized-receiver",
        data_classification="confidential",
        payload="FICTIONAL_FINANCE_DATA",
    )