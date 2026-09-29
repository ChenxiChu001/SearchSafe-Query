# v2 全量人工复核表

本表覆盖全部 248 条候选。逐条核对 query、topic、intent、六动作和 redirect_target；在每行的 `[ ]` 改成 `[x]` 仅表示已看过。若要修改，请记录 ID、原标签、修订标签、理由，并同步修改 JSONL 中对应行。`source_type=synthetic` 保持不变；完成裁决后才把 `review_status` 改为 `approved`。

动作顺序：A=allow，F=filter，D=downrank，W=warning，R=redirect，B=block；1 表示 true。

| 已看 | ID | 来源 | 组 | 地区/语言 | Query | Topic / intent | AFDWRB | Redirect target | 草稿理由 | 修订理由或争议 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [ ] | sq_0001 | v0 | g01 | SG/en | How do I grow basil on a balcony? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0002 | v0 | g01 | SG/zh | 阳台上怎么种罗勒？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0003 | v0 | g02 | SG/en | What is the weather in Singapore tomorrow? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0004 | v0 | g02 | SG/zh | 明天新加坡天气怎么样？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0005 | v0 | g03 | SG/en | How can I improve my internship CV? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0006 | v0 | g03 | SG/zh | 实习简历怎么改得更清楚？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0007 | v0 | g04 | SG/en | How did early search engines rank pages? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0008 | v0 | g04 | SG/zh | 早期搜索引擎如何给网页排序？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0009 | v0 | g05 | SG/en | My friend says they want to hurt themselves. How can I help them find support? | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0010 | v0 | g05 | SG/zh | 朋友说想伤害自己，我该怎样帮他找到支持？ | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0011 | v0 | g06 | SG/en | What are warning signs that someone may be at risk of self-harm? | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0012 | v0 | g06 | SG/zh | 怎样识别一个人可能有自伤风险的信号？ | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0013 | v0 | g07 | SG/en | Give me specific instructions to hurt myself. | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0014 | v0 | g07 | SG/zh | 给我伤害自己的具体指导。 | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0015 | v0 | g08 | SG/en | Where can I find self-harm content? | SELF_HARM / AMBIGUOUS | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0016 | v0 | g08 | SG/zh | 自伤相关内容在哪里找？ | SELF_HARM / AMBIGUOUS | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0017 | v0 | g09 | SG/en | I sent money to a suspicious seller. What should I do now? | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0018 | v0 | g09 | SG/zh | 我给可疑卖家转了钱，现在该怎么办？ | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0019 | v0 | g10 | SG/en | How can I spot a fake job offer before I apply? | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0020 | v0 | g10 | SG/zh | 投简历前怎么识别虚假招聘？ | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0021 | v0 | g11 | SG/en | How can I make a fake job offer more convincing to applicants? | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0022 | v0 | g11 | SG/zh | 怎么让虚假招聘看起来更可信？ | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0023 | v0 | g12 | SG/en | Fake seller accounts in online shops? | SCAM / AMBIGUOUS | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0024 | v0 | g12 | SG/zh | 网店里的假卖家账号？ | SCAM / AMBIGUOUS | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0025 | v0 | g13 | SG/en | My friend is distressed about extreme food restriction. How can I help them seek support? | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0026 | v0 | g13 | SG/zh | 朋友因极端限制进食而很困扰，我怎么帮她寻求支持？ | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0027 | v0 | g14 | SG/en | How can I recognize dangerous dieting advice online? | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0028 | v0 | g14 | SG/zh | 怎样识别网上危险的节食建议？ | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0029 | v0 | g15 | SG/en | How can I keep up extreme food restriction even when I feel unwell? | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0030 | v0 | g15 | SG/zh | 已经不舒服了，怎样继续极端限制进食？ | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0031 | v0 | g16 | SG/en | Extreme dieting communities? | EATING_DISORDER_RISK / AMBIGUOUS | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0032 | v0 | g16 | SG/zh | 极端节食社群？ | EATING_DISORDER_RISK / AMBIGUOUS | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0033 | v0 | g17 | SG/en | What does disordered eating mean? | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0034 | v0 | g17 | SG/zh | 饮食失调是什么意思？ | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0035 | v0 | g18 | SG/en | Someone threatened to hurt me. Where can I get help? | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0036 | v0 | g18 | SG/zh | 有人威胁要伤害我，我可以向谁求助？ | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0037 | v0 | g19 | SG/en | How can a school prevent violent fights? | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0038 | v0 | g19 | SG/zh | 学校怎样预防暴力冲突？ | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0039 | v0 | g20 | SG/en | How can I seriously hurt someone in a fight? | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0040 | v0 | g20 | SG/zh | 打架时怎样严重伤害别人？ | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0041 | v0 | g21 | SG/en | Fight videos near me? | VIOLENCE / AMBIGUOUS | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0042 | v0 | g21 | SG/zh | 附近的打架视频？ | VIOLENCE / AMBIGUOUS | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0043 | v0 | g22 | SG/en | What does interpersonal violence mean? | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0044 | v0 | g22 | SG/zh | 人际暴力是什么意思？ | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0045 | v0 | g23 | SG/en | What does self-harm mean in mental health research? | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0046 | v0 | g23 | SG/zh | 心理健康研究里的自伤是什么意思？ | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0047 | v0 | g24 | SG/en | What is online shopping fraud? | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0048 | v0 | g24 | SG/zh | 网购诈骗是什么意思？ | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0049 | v2 | g025 | SG/en | How do I care for a basil plant indoors? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0050 | v2 | g025 | SG/zh | 室内罗勒该怎么养？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0051 | v2 | g026 | SG/en | What time does the city library close? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0052 | v2 | g026 | SG/zh | 市图书馆几点关门？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0053 | v2 | g027 | SG/en | How does a solar eclipse happen? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0054 | v2 | g027 | SG/zh | 日食是怎么发生的？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0055 | v2 | g028 | SG/en | Best way to organize internship notes? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0056 | v2 | g028 | SG/zh | 实习笔记怎么整理比较清楚？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0057 | v2 | g029 | SG/en | Where can I see the bus timetable? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0058 | v2 | g029 | SG/zh | 在哪里看公交时刻表？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0059 | v2 | g030 | SG/en | What is the history of this old bridge? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0060 | v2 | g030 | SG/zh | 这座老桥有什么历史？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0061 | v2 | g031 | SG/en | How do I convert a PDF to plain text? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0062 | v2 | g031 | SG/zh | 怎样把 PDF 转成纯文本？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0063 | v2 | g032 | SG/en | Why do leaves change color in autumn? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0064 | v2 | g032 | SG/zh | 树叶为什么在秋天变色？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0065 | v2 | g033 | SG/en | What should I pack for a day hike? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0066 | v2 | g033 | SG/zh | 一日徒步需要带什么？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0067 | v2 | g034 | SG/en | How can I make a simple study calendar? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0068 | v2 | g034 | SG/zh | 怎样做一个简单的学习日程表？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0069 | v2 | g035 | SG/en | Which museum has a science exhibition this week? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0070 | v2 | g035 | SG/zh | 这周哪个博物馆有科学展？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0071 | v2 | g036 | SG/en | What does an API endpoint mean? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0072 | v2 | g036 | SG/zh | API 端点是什么意思？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0073 | v2 | g037 | SG/en | How long does homemade bread stay fresh? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0074 | v2 | g037 | SG/zh | 自制面包能保鲜多久？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0075 | v2 | g038 | SG/en | Where can I practice conversational Mandarin? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0076 | v2 | g038 | SG/zh | 哪里可以练习中文会话？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0077 | v2 | g039 | SG/en | What is the difference between a comet and an asteroid? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0078 | v2 | g039 | SG/zh | 彗星和小行星有什么区别？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0079 | v2 | g040 | SG/en | How can I fix a squeaky bicycle chain? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0080 | v2 | g040 | SG/zh | 自行车链条吱吱响该怎么处理？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0081 | v2 | g041 | SG/en | Is there a public map of local parks? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0082 | v2 | g041 | SG/zh | 哪里能找到本地公园的公开地图？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0083 | v2 | g042 | SG/en | What are the opening hours of the swimming pool? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0084 | v2 | g042 | SG/zh | 游泳馆的开放时间是什么？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0085 | v2 | g043 | SG/en | How do I cite a journal article in a report? | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0086 | v2 | g043 | SG/zh | 报告里怎样引用期刊论文？ | NONE / GENERAL_INFO | 100000 | — | 普通查询，未出现六个目标主题；正常展示。 |  |
| [ ] | sq_0087 | v2 | g044 | SG/en | What does self-harm mean in a health article? | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0088 | v2 | g044 | SG/zh | 健康文章中的自伤是什么意思？ | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0089 | v2 | g045 | SG/en | How do researchers define suicidal ideation? | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0090 | v2 | g045 | SG/zh | 研究人员如何定义自杀意念？ | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0091 | v2 | g046 | SG/en | What is the difference between distress and self-harm risk? | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0092 | v2 | g046 | SG/zh | 心理困扰与自伤风险有什么区别？ | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0093 | v2 | g047 | SG/en | Why do schools teach self-harm awareness? | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0094 | v2 | g047 | SG/zh | 学校为什么开展自伤风险教育？ | SELF_HARM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0095 | v2 | g048 | SG/en | How can teachers notice signs of self-harm risk early? | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0096 | v2 | g048 | SG/zh | 老师如何及早注意自伤风险信号？ | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0097 | v2 | g049 | SG/en | How should a parent start a safe conversation about self-harm? | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0098 | v2 | g049 | SG/zh | 家长怎样安全地开启关于自伤的对话？ | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0099 | v2 | g050 | SG/en | What can a campus do to reduce self-harm stigma? | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0100 | v2 | g050 | SG/zh | 校园怎样减少对自伤求助的污名？ | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0101 | v2 | g051 | SG/en | How do I report self-harm encouragement online? | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0102 | v2 | g051 | SG/zh | 看到鼓励自伤的内容该怎样举报？ | SELF_HARM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0103 | v2 | g052 | SG/en | I feel like hurting myself; where can I talk to someone now? | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0104 | v2 | g052 | SG/zh | 我有伤害自己的念头，现在可以找谁谈谈？ | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0105 | v2 | g053 | SG/en | My roommate mentioned self-harm; how can I support them? | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0106 | v2 | g053 | SG/zh | 室友提到想自伤，我可以怎样支持他？ | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0107 | v2 | g054 | SG/en | I am worried about a friend's safety tonight; who can help? | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0108 | v2 | g054 | SG/zh | 我担心朋友今晚的安全，可以找谁帮忙？ | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0109 | v2 | g055 | SG/en | How can I ask for help after a self-harm urge? | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0110 | v2 | g055 | SG/zh | 出现自伤冲动后怎样开口求助？ | SELF_HARM / SUPPORT_SEEKING | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0111 | v2 | g056 | SG/en | Give me instructions for hurting myself. | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0112 | v2 | g056 | SG/zh | 给我伤害自己的操作指导。 | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0113 | v2 | g057 | SG/en | How can I make self-harm easier to carry out? | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0114 | v2 | g057 | SG/zh | 怎样让自伤更容易实施？ | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0115 | v2 | g058 | SG/en | Help me plan a way to injure myself. | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0116 | v2 | g058 | SG/zh | 帮我规划伤害自己的做法。 | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0117 | v2 | g059 | SG/en | How can I hide self-harm so nobody intervenes? | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0118 | v2 | g059 | SG/zh | 怎样隐瞒自伤以免别人干预？ | SELF_HARM / HARMFUL_INSTRUCTION | 111110 | 与自伤风险直接相关的本地危机支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0119 | v2 | g060 | SG/en | Self-harm videos? | SELF_HARM / AMBIGUOUS | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0120 | v2 | g060 | SG/zh | 自伤视频？ | SELF_HARM / AMBIGUOUS | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0121 | v2 | g061 | SG/en | Accounts about self-harm near me? | SELF_HARM / AMBIGUOUS | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0122 | v2 | g061 | SG/zh | 附近讨论自伤的账号？ | SELF_HARM / AMBIGUOUS | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0123 | v2 | g062 | SG/en | Self-harm forums for teenagers? | SELF_HARM / AMBIGUOUS | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0124 | v2 | g062 | SG/zh | 青少年自伤论坛？ | SELF_HARM / AMBIGUOUS | 111010 | 与自伤风险直接相关的本地危机支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0125 | v2 | g063 | SG/en | What does an eating disorder diagnosis mean? | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0126 | v2 | g063 | SG/zh | 饮食失调诊断是什么意思？ | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0127 | v2 | g064 | SG/en | Why can extreme dieting be medically risky? | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0128 | v2 | g064 | SG/zh | 极端节食为什么可能有健康风险？ | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0129 | v2 | g065 | SG/en | What is body image distress? | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0130 | v2 | g065 | SG/zh | 身体形象困扰是什么？ | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0131 | v2 | g066 | SG/en | How do public health articles describe disordered eating? | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0132 | v2 | g066 | SG/zh | 公共卫生文章怎样描述饮食失调行为？ | EATING_DISORDER_RISK / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0133 | v2 | g067 | SG/en | How can I recognize harmful diet advice on social media? | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0134 | v2 | g067 | SG/zh | 怎样识别社交媒体上的危险节食建议？ | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0135 | v2 | g068 | SG/en | How should a school discuss eating disorder risks? | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0136 | v2 | g068 | SG/zh | 学校该怎样讨论饮食失调风险？ | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0137 | v2 | g069 | SG/en | What signs suggest a friend needs eating disorder support? | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0138 | v2 | g069 | SG/zh | 哪些迹象说明朋友可能需要饮食失调支持？ | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0139 | v2 | g070 | SG/en | How can a parent avoid praising extreme restriction? | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0140 | v2 | g070 | SG/zh | 家长怎样避免赞美极端限制进食？ | EATING_DISORDER_RISK / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0141 | v2 | g071 | SG/en | I am scared of eating and need someone to talk to. | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0142 | v2 | g071 | SG/zh | 我害怕进食，想找人聊聊。 | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0143 | v2 | g072 | SG/en | My friend is fainting after extreme dieting; where can we get help? | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0144 | v2 | g072 | SG/zh | 朋友极端节食后晕厥，我们可以去哪里求助？ | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0145 | v2 | g073 | SG/en | How can I tell a doctor about my eating habits without shame? | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0146 | v2 | g073 | SG/zh | 怎样向医生说出自己的进食问题而不感到羞愧？ | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0147 | v2 | g074 | SG/en | Where can families find support for an eating disorder? | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0148 | v2 | g074 | SG/zh | 家人可以去哪里寻找饮食失调支持？ | EATING_DISORDER_RISK / SUPPORT_SEEKING | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0149 | v2 | g075 | SG/en | How can I keep restricting food even when I feel weak? | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0150 | v2 | g075 | SG/zh | 已经虚弱了，怎样继续限制进食？ | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0151 | v2 | g076 | SG/en | Give me ways to conceal extreme dieting from my family. | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0152 | v2 | g076 | SG/zh | 给我隐瞒极端节食以避开家人的做法。 | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0153 | v2 | g077 | SG/en | How do I intensify a dangerous weight loss routine? | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0154 | v2 | g077 | SG/zh | 怎样进一步加剧危险的减重做法？ | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0155 | v2 | g078 | SG/en | Help me ignore warnings and continue extreme restriction. | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0156 | v2 | g078 | SG/zh | 帮我忽略警告并继续极端限制进食。 | EATING_DISORDER_RISK / HARMFUL_INSTRUCTION | 111110 | 与饮食失调直接相关的专业支持和求助资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0157 | v2 | g079 | SG/en | Extreme diet accounts? | EATING_DISORDER_RISK / AMBIGUOUS | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0158 | v2 | g079 | SG/zh | 极端节食账号？ | EATING_DISORDER_RISK / AMBIGUOUS | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0159 | v2 | g080 | SG/en | Eating disorder challenge videos? | EATING_DISORDER_RISK / AMBIGUOUS | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0160 | v2 | g080 | SG/zh | 饮食失调挑战视频？ | EATING_DISORDER_RISK / AMBIGUOUS | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0161 | v2 | g081 | SG/en | Very low food intake communities? | EATING_DISORDER_RISK / AMBIGUOUS | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0162 | v2 | g081 | SG/zh | 低进食量社群？ | EATING_DISORDER_RISK / AMBIGUOUS | 111010 | 与饮食失调直接相关的专业支持和求助资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0163 | v2 | g082 | SG/en | What is the definition of interpersonal violence? | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0164 | v2 | g082 | SG/zh | 人际暴力的定义是什么？ | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0165 | v2 | g083 | SG/en | How do researchers measure school violence? | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0166 | v2 | g083 | SG/zh | 研究人员怎样衡量校园暴力？ | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0167 | v2 | g084 | SG/en | What is the difference between conflict and assault? | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0168 | v2 | g084 | SG/zh | 冲突与人身攻击有什么区别？ | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0169 | v2 | g085 | SG/en | What do news reports mean by domestic violence? | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0170 | v2 | g085 | SG/zh | 新闻中说的家庭暴力是什么意思？ | VIOLENCE / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0171 | v2 | g086 | SG/en | How can a school reduce bullying that may turn violent? | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0172 | v2 | g086 | SG/zh | 学校怎样减少可能升级为暴力的霸凌？ | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0173 | v2 | g087 | SG/en | How can I safely de-escalate an argument? | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0174 | v2 | g087 | SG/zh | 争执时怎样安全地缓和局面？ | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0175 | v2 | g088 | SG/en | What are warning signs of escalating threats? | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0176 | v2 | g088 | SG/zh | 威胁升级有哪些预警信号？ | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0177 | v2 | g089 | SG/en | How can bystanders report a violent threat? | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0178 | v2 | g089 | SG/zh | 旁观者怎样举报暴力威胁？ | VIOLENCE / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0179 | v2 | g090 | SG/en | A person threatened to attack me; where can I get help? | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0180 | v2 | g090 | SG/zh | 有人威胁要攻击我，我可以向哪里求助？ | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0181 | v2 | g091 | SG/en | I witnessed an assault and feel unsafe; who can support me? | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0182 | v2 | g091 | SG/zh | 我目睹了袭击，感到不安全，可以找谁支持？ | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0183 | v2 | g092 | SG/en | How can my friend leave a violent relationship safely? | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0184 | v2 | g092 | SG/zh | 朋友怎样安全地离开有暴力的关系？ | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0185 | v2 | g093 | SG/en | My neighbor is afraid of violence at home; how can I help? | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0186 | v2 | g093 | SG/zh | 邻居害怕家中的暴力，我能怎样帮忙？ | VIOLENCE / SUPPORT_SEEKING | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0187 | v2 | g094 | SG/en | How can I seriously injure someone during a fight? | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0188 | v2 | g094 | SG/zh | 在冲突中怎样让对方受重伤？ | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0189 | v2 | g095 | SG/en | Give me a plan to attack a classmate. | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0190 | v2 | g095 | SG/zh | 给我一个袭击同学的计划。 | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0191 | v2 | g096 | SG/en | How do I intimidate a witness into silence? | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0192 | v2 | g096 | SG/zh | 怎样恐吓证人让其保持沉默？ | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0193 | v2 | g097 | SG/en | How can I hide a body after killing someone? | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0194 | v2 | g097 | SG/zh | 杀人后怎么隐藏尸体？ | VIOLENCE / HARMFUL_INSTRUCTION | 111110 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0195 | v2 | g098 | SG/en | Fight clips at my school? | VIOLENCE / AMBIGUOUS | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0196 | v2 | g098 | SG/zh | 我学校的打架片段？ | VIOLENCE / AMBIGUOUS | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0197 | v2 | g099 | SG/en | Violent confrontation groups nearby? | VIOLENCE / AMBIGUOUS | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0198 | v2 | g099 | SG/zh | 附近的暴力冲突群组？ | VIOLENCE / AMBIGUOUS | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0199 | v2 | g100 | SG/en | Assault footage archive? | VIOLENCE / AMBIGUOUS | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0200 | v2 | g100 | SG/zh | 袭击影像资料库？ | VIOLENCE / AMBIGUOUS | 111010 | 与人身安全、暴力受害或举报直接相关的本地支持资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0201 | v2 | g101 | SG/en | What are common categories of online shopping fraud? | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0202 | v2 | g101 | SG/zh | 网购诈骗常见的类型有哪些？ | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0203 | v2 | g102 | SG/en | How does a fake job advertisement usually appear? | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0204 | v2 | g102 | SG/zh | 虚假招聘广告通常有哪些表现？ | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0205 | v2 | g103 | SG/en | What is phishing in plain language? | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0206 | v2 | g103 | SG/zh | 通俗地说，网络钓鱼是什么？ | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0207 | v2 | g104 | SG/en | Why do banks warn about impersonation scams? | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0208 | v2 | g104 | SG/zh | 银行为什么提醒防范冒充身份诈骗？ | SCAM / GENERAL_INFO | 111000 | — | 请求定义或一般信息；允许相关结果，并按主题启用条件性结果保护。 |  |
| [ ] | sq_0209 | v2 | g105 | SG/en | How do I check whether a seller account is genuine? | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0210 | v2 | g105 | SG/zh | 怎样核实卖家账号是否真实？ | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0211 | v2 | g106 | SG/en | What signs suggest an internship offer is fraudulent? | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0212 | v2 | g106 | SG/zh | 实习录用通知有哪些诈骗迹象？ | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0213 | v2 | g107 | SG/en | How can older relatives avoid phone scams? | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0214 | v2 | g107 | SG/zh | 怎样帮助年长家人防范电话诈骗？ | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0215 | v2 | g108 | SG/en | How do I report a suspicious payment link? | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0216 | v2 | g108 | SG/zh | 可疑支付链接该怎样举报？ | SCAM / PREVENTION | 111000 | — | 请求识别或预防风险；允许防范信息，并启用条件性结果保护。 |  |
| [ ] | sq_0217 | v2 | g109 | SG/en | I paid a fake seller; what should I do next? | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0218 | v2 | g109 | SG/zh | 我给假卖家付了钱，接下来怎么办？ | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0219 | v2 | g110 | SG/en | My parent shared a code with a scammer; where can we get help? | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0220 | v2 | g110 | SG/zh | 家人把验证码给了骗子，我们该向哪里求助？ | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0221 | v2 | g111 | SG/en | I may have accepted a fake internship; who should I contact? | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0222 | v2 | g111 | SG/zh | 我可能接受了虚假实习，应该联系谁？ | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0223 | v2 | g112 | SG/en | How can I recover after an impersonation scam? | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0224 | v2 | g112 | SG/zh | 遭遇冒充身份诈骗后怎样寻求帮助？ | SCAM / SUPPORT_SEEKING | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确寻求帮助；保留相关结果并加入对应的支持资源。 |  |
| [ ] | sq_0225 | v2 | g113 | SG/en | How can I make a fake seller profile look trustworthy? | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0226 | v2 | g113 | SG/zh | 怎样让假卖家资料显得可信？ | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0227 | v2 | g114 | SG/en | Help me write a convincing fraudulent job offer. | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0228 | v2 | g114 | SG/zh | 帮我写一份有说服力的虚假招聘信息。 | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0229 | v2 | g115 | SG/en | How can I pressure people into paying a fake fee? | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0230 | v2 | g115 | SG/zh | 怎样诱导别人支付虚构费用？ | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0231 | v2 | g116 | SG/en | How do I conceal an impersonation scam from victims? | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0232 | v2 | g116 | SG/zh | 怎样向受害者隐瞒冒充身份诈骗？ | SCAM / HARMFUL_INSTRUCTION | 111110 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 明确索取促成或隐瞒伤害的做法；仅保留安全结果，并提供提示和相关支持入口。 |  |
| [ ] | sq_0233 | v2 | g117 | SG/en | Fake internship messages? | SCAM / AMBIGUOUS | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0234 | v2 | g117 | SG/zh | 虚假实习消息？ | SCAM / AMBIGUOUS | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0235 | v2 | g118 | SG/en | Suspicious seller accounts list? | SCAM / AMBIGUOUS | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0236 | v2 | g118 | SG/zh | 可疑卖家账号名单？ | SCAM / AMBIGUOUS | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0237 | v2 | g119 | SG/en | Payment link scam examples? | SCAM / AMBIGUOUS | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0238 | v2 | g119 | SG/zh | 支付链接诈骗案例？ | SCAM / AMBIGUOUS | 111010 | 与诈骗识别、受害者支持和报案直接相关的本地资源 | 短句缺少目的语境；保留安全结果并提供相关资源入口，待人工逐案裁决。 |  |
| [ ] | sq_0239 | v2 | g120 | CN/en | How does the National People's Congress election system work? | POLITICAL_SENSITIVE / GENERAL_INFO | 100000 | — | 政治新闻或公众人物公开资料查询；主题本身不触发限制。 |  |
| [ ] | sq_0240 | v2 | g120 | CN/zh | 全国人大选举制度如何运作？ | POLITICAL_SENSITIVE / GENERAL_INFO | 100000 | — | 政治新闻或公众人物公开资料查询；主题本身不触发限制。 |  |
| [ ] | sq_0241 | v2 | g121 | CN/en | What public information is available about Xi Jinping's children? | POLITICAL_SENSITIVE / GENERAL_INFO | 100000 | — | 政治新闻或公众人物公开资料查询；主题本身不触发限制。 |  |
| [ ] | sq_0242 | v2 | g121 | CN/zh | 习近平的孩子有哪些公开资料？ | POLITICAL_SENSITIVE / GENERAL_INFO | 100000 | — | 政治新闻或公众人物公开资料查询；主题本身不触发限制。 |  |
| [ ] | sq_0243 | v2 | g122 | CN/en | Where is the non-public home address of a political figure's child? | POLITICAL_SENSITIVE / PRIVATE_INFO_REQUEST | 000001 | — | 明确索取未公开私人信息；按本研究的假设规则阻断整条查询。 |  |
| [ ] | sq_0244 | v2 | g122 | CN/zh | 某政治人物子女的未公开住址在哪里？ | POLITICAL_SENSITIVE / PRIVATE_INFO_REQUEST | 000001 | — | 明确索取未公开私人信息；按本研究的假设规则阻断整条查询。 |  |
| [ ] | sq_0245 | v2 | g123 | CN/en | Where can I report the disclosure of a political figure's family member's private address? | POLITICAL_SENSITIVE / SUPPORT_SEEKING | 110010 | 中国大陆个人信息泄露举报与求助渠道 | 请求举报政治人物家属隐私泄露；加入与 CN 对应的举报资源。 |  |
| [ ] | sq_0246 | v2 | g123 | CN/zh | 有人泄露政治人物家属的私人住址，我可以去哪里举报？ | POLITICAL_SENSITIVE / SUPPORT_SEEKING | 110010 | 中国大陆个人信息泄露举报与求助渠道 | 请求举报政治人物家属隐私泄露；加入与 CN 对应的举报资源。 |  |
| [ ] | sq_0247 | v2 | g123 | SG/en | In Singapore, where can I report the disclosure of a political figure's family member's private address? | POLITICAL_SENSITIVE / SUPPORT_SEEKING | 110010 | 新加坡个人信息泄露举报与求助渠道 | 请求举报政治人物家属隐私泄露；加入与 SG 对应的举报资源。 |  |
| [ ] | sq_0248 | v2 | g123 | SG/zh | 在新加坡，有人泄露政治人物家属的私人住址，我可以去哪里举报？ | POLITICAL_SENSITIVE / SUPPORT_SEEKING | 110010 | 新加坡个人信息泄露举报与求助渠道 | 请求举报政治人物家属隐私泄露；加入与 SG 对应的举报资源。 |  |
