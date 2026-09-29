# v2 单人复核记录

2026-09-27，项目所有者在本会话中确认：已逐条查看现有 248 条 v2 候选，对当前查询文本和标签**全部接受、没有修订**。复核由一人完成；此前的 `REVIEW_SHEET_V2.md` 未保存逐条勾选或裁决，因此本记录仅能证明一次明确的整批接受声明，不能证明独立双人标注、一致性系数或每条的审阅过程。

`data/canonical/reviewed_v2.jsonl` 是对 `candidates_v2.jsonl` 的内容副本，只把 `review_status` 设为 `approved`、`dataset_version` 设为 `v2`。原始草稿和 v0 归档保持不变；来源字段继续为 `synthetic`。

随后新增的 80 条政治类查询尚未经项目所有者审核，单独保存在 `political_expansion_v2_1_draft.jsonl`，状态继续为 `draft`。包含它们的训练和内部评估均为开发性实验，政治类指标不能称为已审核 Gold 性能。
