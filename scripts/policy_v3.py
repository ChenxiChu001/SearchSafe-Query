"""Defined v3 label combinations for the hypothetical intervention policy."""

from __future__ import annotations

from build_v2_candidates import intervention

RISK_TOPICS = {"SELF_HARM", "EATING_DISORDER_RISK", "VIOLENCE", "SCAM"}
RISK_INTENTS = {"GENERAL_INFO", "PREVENTION", "SUPPORT_SEEKING", "HARMFUL_INSTRUCTION", "AMBIGUOUS"}


def covered(topic: str, intent: str) -> bool:
    if topic == "NONE":
        return intent == "GENERAL_INFO"
    if topic in RISK_TOPICS:
        return intent in RISK_INTENTS
    if topic == "POLITICAL_SENSITIVE":
        return intent in {"GENERAL_INFO", "SUPPORT_SEEKING", "PRIVATE_INFO_REQUEST"}
    return False


def action_for(topic: str, intent: str, locale: str) -> dict[str, bool] | None:
    return intervention(topic, intent, locale)[0] if covered(topic, intent) else None
