"""Executable v3.1 hypothetical query-level intervention policy."""

from __future__ import annotations

from build_v2_candidates import intervention as old_intervention
from policy_v3 import covered
from schema_v2 import ACTION_KEYS

HARD_TARGETS = {
    "SELF_HARM": {"CN": "中国大陆与自伤风险直接相关的心理危机求助入口", "SG": "新加坡与自伤风险直接相关的心理危机求助入口"},
    "EATING_DISORDER_RISK": {"CN": "中国大陆饮食失调专业支持服务入口", "SG": "新加坡饮食失调专业支持服务入口"},
    "VIOLENCE": {"CN": "中国大陆人身安全或暴力受害者求助举报入口", "SG": "新加坡人身安全或暴力受害者求助举报入口"},
    "SCAM": {"CN": "中国大陆诈骗受害者报案与止损支持入口", "SG": "新加坡诈骗受害者报案与止损支持入口"},
    "POLITICAL_SENSITIVE": {"CN": "中国大陆个人信息泄露举报入口", "SG": "新加坡个人信息泄露举报入口"},
}


def action_for(topic: str, intent: str, locale: str, resource_navigation: bool) -> tuple[dict[str, bool], str | None] | None:
    if locale not in {"CN", "SG"} or not covered(topic, intent):
        return None
    if resource_navigation:
        if intent != "SUPPORT_SEEKING" or topic not in HARD_TARGETS:
            return None
        action = dict.fromkeys(ACTION_KEYS, False)
        action["redirect"] = True
        return action, HARD_TARGETS[topic][locale]
    return old_intervention(topic, intent, locale)
