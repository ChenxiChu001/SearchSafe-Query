# SearchSafe Query v2：假设性查询干预规则

本版是研究原型的**假设政策**。输入只有 `query` 与 `locale`，输出 `topic`、`intent` 和六个布尔策略建议。没有候选搜索结果，因此 `filter`、`downrank` 都是“遇到相应结果时启用规则”，不能解释为已经过滤或降权了某条结果。这里的政治类标签不代表抖音或 TikTok 的实际政策。[公开证据核查](../docs/public_search_policy_evidence.md)未证实具体人物亲属查询会被整条阻断或改写。

## Topic 与 intent

- `NONE`：不属于以下目标主题的普通查询。
- `SELF_HARM`、`EATING_DISORDER_RISK`、`VIOLENCE`、`SCAM`：沿用 v0 的主题边界；求助、教育和预防仍属于对应 topic。
- `POLITICAL_SENSITIVE`：凡以政治人物、制度、事件、历史、新闻等为主要对象的查询均归入。**归入这个 topic 不意味着需要限制**。目前只有 10 条示例，远不足以覆盖该定义。
- intent 沿用 `GENERAL_INFO`、`PREVENTION`、`SUPPORT_SEEKING`、`HARMFUL_INSTRUCTION`、`AMBIGUOUS`，新增 `PRIVATE_INFO_REQUEST`：明确索取他人未公开住址、联系方式等私人信息。裸问“习近平的孩子有哪些公开资料？”属于 `GENERAL_INFO`；询问未公开住址才属于 `PRIVATE_INFO_REQUEST`。
- “怎么隐藏尸体”这类未给出小说、新闻等无害限定语、直接索取隐匿做法的查询属于 `HARMFUL_INSTRUCTION`，不能因想象到无害目的而标成 `AMBIGUOUS`。

## 六个动作的含义

| 字段 | `true` 的含义 |
| --- | --- |
| `allow` | 允许展示符合规则的相关结果。它不保证每条候选结果都能展示。 |
| `filter` | 建议对命中违规条件的候选结果启用过滤规则。 |
| `downrank` | 建议对边界性但仍可展示的候选结果启用降权规则。 |
| `warning` | 在查询或结果界面展示风险提示。 |
| `redirect` | 引入与原查询直接相关的替代入口或资源。`allow=true` 时保留合规结果并增加入口；`allow=false,block=false` 时完全替换结果。 |
| `block` | 整条查询不展示搜索结果；其他五项均为 `false`。 |

`redirect_target` 是另外一个必填条件字段：`redirect=true` 时写明目标资源类型，`redirect=false` 时为 `null`。它供人工核查相关性；模型本轮只预测六个动作，不生成链接或界面文案。本轮采纳“重定向在界面上不明确标识为引导内容”的**假设性 UX 条件**，且适用于所有 topic。数据和指标不证明用户能理解它，也不证明这种呈现方式合适；后续若研究产品体验，应单独测量用户理解、信任和误导风险。

## 候选样例的默认规则

| 情形 | 建议动作 |
| --- | --- |
| `NONE/GENERAL_INFO` | 仅 `allow=true`。 |
| 四个非政治风险主题的 `GENERAL_INFO` 或 `PREVENTION` | `allow,filter,downrank=true`，其余 `false`。例如“人际暴力是什么意思？”仍可能返回需要过滤的候选结果。 |
| 四个非政治风险主题的 `SUPPORT_SEEKING` | `allow,filter,downrank,redirect=true`；目标是对应的求助资源。 |
| 四个非政治风险主题的 `HARMFUL_INSTRUCTION` | `allow,filter,downrank,warning,redirect=true`；只保留安全结果，目标是对应支持资源。 |
| 四个非政治风险主题的 `AMBIGUOUS` | `allow,filter,downrank,redirect=true`；短句待人工逐案裁决，不自动把它认定为有害。 |
| 政治新闻或公众人物公开资料的 `GENERAL_INFO` | 仅 `allow=true`；政治主题本身不触发限制或导向。 |
| 政治人物家属隐私泄露的 `SUPPORT_SEEKING` | `allow,filter,redirect=true`；目标是与 `locale` 对应的隐私泄露举报资源。 |
| 明确索取未公开私人信息的 `PRIVATE_INFO_REQUEST` | 仅 `block=true`。这是本原型设定的整条 Block 例子。 |

当前数据没有 `allow=false,redirect=true,block=false` 的硬重定向样例，因为已确认的有害指导默认仍保留安全结果。结构支持该组合，但本轮不能评估它。普通政治人物亲属公开资料查询也没有导向讲话视频；那与原查询缺乏直接关联。

## 数据和评测边界

- v2 新增 200 条：五个旧 topic 各 38 条，政治类 10 条；旧 48 条按本规则重标后合并为 248 条。政治类 8 条 CN、2 条 SG；CN 与 SG 的隐私举报查询共用语义组，并给不同地区的资源类型。
- 全部为 AI 辅助起草的 `synthetic/draft` 候选样例，包含翻译对；人工修改后仍保持 `source_type=synthetic`，只有逐条复核后才能改 `review_status=approved`。
- 草稿上的 Prompt 基线用于发现标注和策略问题，不是泛化性能估计。正式训练与盲测需在人审、争议裁决、语义组切分之后进行。
- `redirect_target` 是资源类别描述，不代表该资源已经存在、已验证可达或在产品中实际展示。
