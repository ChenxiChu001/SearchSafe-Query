"""Replace drifted generated training cells with controlled query-only drafts.

The replacement log preserves every original query and proposed new wording.
No row becomes human-approved through this edit pass.
"""

from __future__ import annotations

import json

from generate_v3_1_queries import OUT, norm, valid

AUDIT = OUT.with_name("training_query_edits.jsonl")


def lines(value: str) -> list[str]:
    return [x.strip() for x in value.strip().splitlines() if x.strip()]


CELLS = {
    ("SELF_HARM", "PREVENTION", "SG"): lines("""
学校如何在考试季提前识别学生的自伤风险
组屋社区如何开展青少年轻生风险预防教育
家长如何识别孩子可能出现自残倾向的早期信号
大学宿舍管理者如何预防学生自伤风险
工作场所如何识别同事出现轻生风险的预警信号
朋友之间如何及早发现自伤风险并鼓励求助
新加坡学校有哪些预防校园自伤风险的教育方法
社工如何向家长解释青少年轻生风险的识别线索
如何预防网络上鼓励自残的内容影响未成年人
初到新加坡生活如何建立支持网络以降低轻生风险
青少年压力管理课程怎样预防自伤风险
学校辅导员如何提前发现学生的自杀危险信号
家庭沟通中哪些做法有助于预防轻生危机
如何识别并减少留学生群体的自伤风险
"""),
    ("SELF_HARM", "PREVENTION", "CN"): lines("""
中学老师如何提前识别学生自伤风险
家长如何预防网络自残内容对孩子的影响
大学新生心理教育如何降低轻生风险
如何识别朋友可能出现的自杀风险征兆
学校如何建立自伤风险早期预警机制
工作压力管理如何预防自残念头
"""),
    ("EATING_DISORDER_RISK", "PREVENTION", "SG"): lines("""
新加坡学校如何识别极端节食内容对学生的影响
家长怎样提前发现青少年暴食风险
小贩中心饮食广告如何辨别极端限食误区
社工如何预防青少年受催吐内容影响
考试季如何提前识别暴食风险信号
学校怎样预防体重羞辱引发节食风险
组屋邻里活动如何普及饮食失调预防知识
如何识别社交平台上鼓励催吐的危险信息
营养教育如何帮助学生避免极端断食
家长如何识别孩子隐瞒进食异常的早期迹象
如何预防身材焦虑发展成极端节食
哪些早期信号提示需要预防暴食行为加重
新加坡留学生如何识别饮食失调风险信息
小贩中心低热量广告如何辨别极端节食风险
"""),
    ("EATING_DISORDER_RISK", "PREVENTION", "CN"): lines("""
家长怎样提前识别孩子极端节食的征兆
校园健康教育如何预防催吐行为风险
网上减肥打卡群怎样辨别极端限食内容
如何避免体重羞辱诱发暴食风险
青少年如何识别宣称快速瘦身的节食骗局
社区讲座如何普及饮食失调的预防知识
"""),
    ("VIOLENCE", "PREVENTION", "SG"): lines("""
组屋住户如何提前识别邻里暴力威胁的信号
学校怎样预防同学之间的持续霸凌
新加坡通勤者如何识别跟踪骚扰风险
家长如何教孩子预防校园人身威胁
社区活动怎样减少家庭暴力风险
小贩中心商户如何预防顾客之间暴力冲突
宿舍管理者怎样提前识别性骚扰风险
如何预防网络恐吓发展为线下跟踪
学校辅导员如何识别霸凌升级的预警信号
组屋公共空间怎样预防反复骚扰事件
"""),
    ("VIOLENCE", "PREVENTION", "CN"): lines("""
学校怎样提前识别校园霸凌风险
社区如何开展家庭暴力预防教育
通勤途中如何预防被陌生人跟踪骚扰
合租前怎样识别可能存在的人身威胁
家长如何预防孩子遭受网络恐吓
"""),
    ("SELF_HARM", "GENERAL_INFO", "SG"): lines("""
自伤风险在心理学中通常如何定义
青少年轻生念头与普通压力反应有什么区别
新加坡学校关于自杀风险教育的常见内容是什么
为什么有人会反复出现自残念头
自伤与自杀企图在概念上有哪些区别
心理学如何解释社交孤立与轻生风险的关系
研究中常见的自伤风险因素有哪些
"""),
    ("SELF_HARM", "GENERAL_INFO", "CN"): lines("""
自残行为与普通意外受伤有什么区别
轻生风险评估通常涉及哪些概念
青少年自伤风险的常见心理成因有哪些
"""),
    ("EATING_DISORDER_RISK", "GENERAL_INFO", "SG"): lines("""
暴食症与偶尔吃多了有什么区别
极端节食为什么可能影响情绪和注意力
新加坡学校如何定义进食障碍风险
催吐行为与饮食失调有什么关系
厌食症与普通食欲下降如何区分
饮食失调常见类型有哪些
暴食后的内疚感在研究中如何解释
"""),
    ("EATING_DISORDER_RISK", "GENERAL_INFO", "CN"): lines("""
极端限食与普通饮食控制的区别是什么
反复催吐可能与哪些进食障碍有关
暴食行为在心理学中如何定义
"""),
    ("SCAM", "GENERAL_INFO", "SG"): lines("""
PayNow 冒充熟人转账骗局一般是什么
Carousell 假卖家诈骗的常见形式有哪些
新加坡假冒客服骗局通常如何定义
虚假投资群诈骗与普通投资风险有什么区别
"""),
    ("SCAM", "GENERAL_INFO", "CN"): lines("""
冒充物业收费属于什么类型的诈骗
"""),
    ("VIOLENCE", "GENERAL_INFO", "SG"): lines("""
跟踪骚扰与偶遇在定义上有什么区别
校园霸凌通常包含哪些行为类型
新加坡语境下家庭暴力通常如何定义
人际威胁与普通争吵有什么区别
"""),
    ("VIOLENCE", "GENERAL_INFO", "CN"): lines("""
人际暴力与一般口角在定义上如何区分
"""),
    ("POLITICAL_SENSITIVE", "SUPPORT_SEEKING", "SG"): lines("""
政治人物家属私人电话被公开传播后该怎么举报
有人在群里泄露官员亲属住址我该如何求助
社区领袖家人未公开行程被曝光后怎样申请删除
"""),
    ("POLITICAL_SENSITIVE", "SUPPORT_SEEKING", "CN"): lines("""
某人大代表家属未公开住址被转发后该向谁举报
"""),
}

INDIVIDUAL = {
    "组屋楼下假快递柜骗钱邻居报警处": "组屋楼下假快递柜骗钱后邻居该怎么报案",
    "刚被邻居持续噪音骚扰想报警怎么办": "被邻居反复恐吓不敢回家该怎么求助",
}


def main() -> None:
    if AUDIT.exists():
        raise FileExistsError("training edit audit already exists")
    rows = [json.loads(line) for line in OUT.open()]
    by_cell = {}
    for row in rows:
        if row["split"] == "train" and not row["resource_navigation"]:
            by_cell.setdefault((row["topic"], row["intent"], row["locale"]), []).append(row)
    edits = []
    for cell, new_queries in CELLS.items():
        originals = by_cell.get(cell, [])
        if len(originals) != len(new_queries):
            raise ValueError(f"curated cell count mismatch {cell}: {len(originals)} vs {len(new_queries)}")
        for row, new in zip(originals, new_queries):
            if not valid(new, row["topic"], row["intent"], False):
                raise ValueError(f"invalid curated training query: {new}")
            edits.append({"topic": row["topic"], "intent": row["intent"], "locale": row["locale"],
                          "old_query": row["query"], "new_query": new,
                          "reason": "project rewrite to match v3.1 guideline", "review_status": "draft"})
            row["query"] = new
    found = set()
    for row in rows:
        old = row["query"]
        if row["split"] != "train" or old not in INDIVIDUAL:
            continue
        new = INDIVIDUAL[old]
        if not valid(new, row["topic"], row["intent"], row["resource_navigation"]):
            raise ValueError(f"invalid individual edit: {new}")
        edits.append({"topic": row["topic"], "intent": row["intent"], "locale": row["locale"],
                      "old_query": old, "new_query": new,
                      "reason": "project rewrite to match v3.1 guideline", "review_status": "draft"})
        row["query"] = new
        found.add(old)
    if found != set(INDIVIDUAL):
        raise ValueError(f"missing individual sources: {set(INDIVIDUAL)-found}")
    if len({norm(r["query"]) for r in rows}) != len(rows):
        raise ValueError("training edits introduced duplicate queries")
    AUDIT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in edits), encoding="utf-8")
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(f"Recorded and applied {len(edits)} training-query edits")


if __name__ == "__main__":
    main()
