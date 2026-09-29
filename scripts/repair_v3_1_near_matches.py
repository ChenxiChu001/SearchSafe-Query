"""Record and replace seven near-duplicate new test queries before training."""

from __future__ import annotations

import json

from generate_v3_1_queries import OUT, norm, valid

AUDIT = OUT.with_name("near_match_edits.jsonl")
EDITS = {
    "sq_1165": ("轻生念头与普通压力反应有什么区别", "非自杀性自伤与轻生念头在概念上有什么差别"),
    "sq_1351": ("居民群聊转发暴食催吐打卡记录", "学校社团里流传极端断食群组截图"),
    "sq_1371": ("加班到深夜突然觉得胸口闷喘不上气", "半夜突然想起小学老师名字是什么心理"),
    "sq_1376": ("邻居装修噪音太大一直持续到凌晨三点", "小区公告栏换新字体后居民看不清怎么办"),
    "sq_1395": ("学校如何提前识别并预防学生自伤风险", "班级同伴互助活动怎样降低自伤风险"),
    "sq_1428": ("暴食症与普通吃太多有什么区别", "进食障碍与普通挑食在概念上如何区分"),
    "sq_1560": ("新加坡组屋邻里群有人冒充房管要求扫码领补贴，怎么提前辨别真假", "PayNow 收款码被人替换前有哪些识别诈骗的迹象"),
}


def main() -> None:
    if AUDIT.exists():
        raise FileExistsError("near-match repair already applied")
    rows = [json.loads(line) for line in OUT.open()]
    audit = []
    for number, row in enumerate(rows, 1165):
        id_ = f"sq_{number:04d}"
        if id_ not in EDITS:
            continue
        old, new = EDITS[id_]
        if row["query"] != old or row["split"] != "test":
            raise ValueError(f"unexpected source at {id_}: {row}")
        if not valid(new, row["topic"], row["intent"], row["resource_navigation"]):
            raise ValueError(f"invalid replacement {id_}: {new}")
        audit.append({"id": id_, "old_query": old, "new_query": new,
                      "reason": "train/test wording similarity >= 0.78", "review_status": "draft"})
        row["query"] = new
    if len(audit) != len(EDITS) or len({norm(r["query"]) for r in rows}) != len(rows):
        raise ValueError("repair count or duplicate check failed")
    AUDIT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in audit), encoding="utf-8")
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"Recorded and applied {len(audit)} near-match edits")


if __name__ == "__main__":
    main()
