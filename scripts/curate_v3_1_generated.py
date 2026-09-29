"""Apply a recorded project edit pass to obviously off-target generated queries."""

from __future__ import annotations

import json
from pathlib import Path

from generate_v3_1_queries import OUT, norm, valid

AUDIT = OUT.with_name("query_edits.jsonl")

# Edits retain each draft's intended topic/intent/locale and remain unapproved.
EDITS = {
    "孩子在学校被同学起外号很伤心": ("孩子觉得学校作业太多如何安排时间", "avoid bullying topic inside NONE"),
    "突然收到陌生号码发来的中奖短信": ("突然收到陌生号码发来的天气提醒短信", "avoid possible scam cue inside NONE"),
    "组屋楼长假扮维修工上门换锁骗押金": ("假冒维修工骗取押金属于什么诈骗类型", "make GENERAL_INFO request explicit"),
    "小贩中心有人低声说想结束生命": ("轻生念头与普通压力反应有什么区别", "make GENERAL_INFO request explicit"),
    "学生压力太大导致情绪低落，自杀的历史原因有哪些": ("青少年自杀风险在心理学上有哪些常见因素", "remove unnatural causal wording"),
    "看到朋友圈旧照片突然想删掉所有账号，这算不算自残的前一步该怎么防？": ("学校如何提前识别并预防学生自伤风险", "replace speculative self-harm cue with actual prevention"),
    "刚被快递骂没收到货，心里堵得慌怎么防自残": ("家长如何提前发现并预防青少年自残风险", "replace contrived scenario with clear prevention"),
    "发微信发错话惹人生气，怎么提前防轻生念头": ("大学新生如何识别并预防轻生风险", "replace contrived scenario with clear prevention"),
    "家人常因琐事想轻生，怎么在邻里间建立预防沟通机制": ("家庭如何提前识别并预防青少年轻生风险", "distinguish prevention from current help"),
    "工作压力大到想结束生命，日常怎么预防这种想法出现": ("工作压力积累时如何提前预防自伤风险", "distinguish prevention from current help"),
    "学校保安室查宿舍网络是否算跟踪": ("跟踪骚扰在法律上是什么意思", "make violence GENERAL_INFO boundary clear"),
    "组屋楼下的噪音长期扰民算不算骚扰": ("新加坡对跟踪骚扰的通常定义是什么", "avoid ordinary noise dispute as violence"),
    "孩子上学路上被陌生人跟踪，有哪些预警信号能发现": ("怎样提前识别孩子上学路上的跟踪风险信号", "remove already-affected support cue"),
    "上班途中被陌生车反复尾随，如何识别潜在跟踪危险": ("通勤途中如何提前识别并预防尾随风险", "remove already-affected support cue"),
    "小区邻里因车位纠纷收到威胁短信，如何识别并预防升级": ("邻里纠纷中如何提前识别威胁升级的风险", "distinguish prevention from ongoing threat response"),
    "组屋楼下小贩中心排队时有人突然狂吐是暴食吗": ("暴食症与普通吃太多有什么区别", "remove medically implausible context"),
    "地铁上吃太多想催吐怎么办能预防": ("如何提前识别并预防催吐行为风险", "remove current help request from PREVENTION"),
    "邻居在组屋楼下装假基站骗钱，小孩想举报去哪？": ("PayNow 转账被冒充客服骗走后怎么举报", "replace implausible SG scenario with victim help"),
}


def main() -> None:
    if AUDIT.exists():
        raise FileExistsError("query edit audit already exists")
    rows = [json.loads(line) for line in OUT.open()]
    found = set()
    audit = []
    for row in rows:
        old = row["query"]
        if old not in EDITS:
            continue
        if row["split"] != "test":
            raise ValueError(f"test edit unexpectedly matches training row: {old}")
        new, reason = EDITS[old]
        if not valid(new, row["topic"], row["intent"], row["resource_navigation"]):
            raise ValueError(f"invalid replacement: {new}")
        audit.append({"split": row["split"], "topic": row["topic"], "intent": row["intent"],
                      "locale": row["locale"], "old_query": old, "new_query": new,
                      "reason": reason, "review_status": "draft"})
        row["query"] = new
        found.add(old)
    if found != set(EDITS):
        raise ValueError(f"missing edit sources: {set(EDITS)-found}")
    if len({norm(r["query"]) for r in rows}) != len(rows):
        raise ValueError("edit created a duplicate query")
    AUDIT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in audit), encoding="utf-8")
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"Recorded and applied {len(audit)} draft test-query edits")


if __name__ == "__main__":
    main()
