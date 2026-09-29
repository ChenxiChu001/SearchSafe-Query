# SHIELD 与 VEILED-SH 数据集交接

核对日期：2026-09-27。两个数据集用途不同，原始数据应分别使用，不能直接把标签合并。

## SHIELD

- 来源：[官方仓库](https://github.com/flpspacek/SHIELD)；对应论文：[Mitigating Risks in Marketplace Semantic Search: A Dataset for Harmful and Sensitive Query Alignment](https://doi.org/10.1145/3699682.3728329)（UMAP 2025）。此处的 SHIELD 指 **Semantic Harmful-content Identification and Ethical Labeling Dataset**，不是其他同名数据集。
- 用途：面向电商语义搜索的英文合成查询，按 `safe`、`sensitive`、`harmful` 三类组织，另有各类 topic、subtopic 词表。可用于查询风险分类的外部对照；其三类标签不能直接当作本项目的六个主题、意图或干预动作标签。
- 已下载：`data/external/SHIELD/`，共 9 个原始 ZIP，来自仓库提交 `37ca2d97d133a82d026831b26aa157daddb10329`。每个 ZIP 含一个单列 CSV 文本，无逐条 topic/subtopic 对应字段。
- 本地实际行数（不含表头）：`safe_queries.zip` 19,880；`sensitive_queries.zip` 8,871；`harmful_queries.zip` 17,770，合计 46,521。三个类别的 topic 和 subtopic ZIP 也已保存。仓库 README 称 harmful 为 17,170，本地原始文件数为 17,770；后续统计以实际文件为准，并保留这个差异。
- 官方仓库未声明仓库级许可证；对外再分发前应确认使用条款。

读取示例：`pandas.read_csv("data/external/SHIELD/harmful_queries.zip")`。类名由文件名确定，CSV 本身只有同名文本列。原始文件中有重复查询，建模前按任务需要检查去重和数据泄漏。

## VEILED-SH

- 来源：[GovTech 数据卡](https://huggingface.co/datasets/govtech/veiled-sh)；[GovTech 介绍文章](https://blog.ai.gov.sg/behind-veiled-expressions-a-singapore-context-benchmark-for-mental-health-ai-evaluation/)（2026-09-25）。全名 **Vulnerability Expression through Indirect Language Evaluation Dataset – Self-Harm**，与 MOHT 合作开发。
- 用途：评估系统能否识别新加坡语境中间接的心理困扰、非自杀性自伤和自杀意念，并给出合适回应。数据卡称有 10,003 条匿名化英文 prompt，`context` 包括 `counsellor_chat`、`forum_post`、`search_query`、`triage_tool`；本项目若用于搜索场景，优先筛选 `search_query`，但需先取得数据文件才能核对该子集规模。
- 主要字段：`confession_id`、`source`、`context`、`prompt`、`persona`、`intents`、`functions`、`response_policy`、`human_annotation`。`intents` 包含 benign、emotional_distress、nssi（0–3）和 suicidal_ideation（0–5）。每条样本保留 6 个评估者画像（3 名临床人员、3 名同伴支持者）对应的多标签判断；本次发布的标签由校准后的 AI judge 生成，`human_annotation` 恒为 `false`，**没有统一共识标签**。评估时应分别报告画像间一致性，不宜直接取多数票充当人工真值。
- 获取状态：已保存公开数据卡到 `data/external/VEILED-SH/README.source.md`；**`dataset.parquet` 尚未下载**。数据仓库是 gated（需登录 Hugging Face 并同意共享联系信息）；当前环境无 HF 凭据，匿名访问数据文件返回 HTTP 401。页面标注 MIT 许可证，但访问仍受该门槛约束。不要将数据卡误当成数据集本体。
- 获得访问权后，在 Hugging Face 页面接受条件、登录本机，再运行：`hf download govtech/veiled-sh dataset.parquet --repo-type dataset --local-dir data/external/VEILED-SH`。下载后核对 10,003 行及字段；不要把账号令牌写进仓库。

两套数据都不是本项目已审核的金标准。SHIELD 可帮助检查通用搜索风险分类，VEILED-SH 更适合检查自伤相关的间接表达与响应策略；使用前仍需映射到本项目的标签定义并做人工抽检。
