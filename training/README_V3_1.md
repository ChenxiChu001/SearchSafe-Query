# v3.1 Qwen3.5 9B QLoRA

本轮延续同一 Qwen3.5 9B 4-bit 基座和 4 层 LoRA、batch size 1、学习率 5e-5。旧 v3 冻结文件和适配器不覆盖。新版本先训练 1000 条 train（旧 700＋新增 300），dev 保留旧 100，另新增 100 条测试题；旧 200 条测试题仅用于历史诊断。旧版逐条修订和新增查询为 `draft`，新测试题未做人审前指标只属探索性。用户因时间约束将本轮缩为**直接输出路线**；标签→规则路线的数据和定义已准备，但本轮不训练或评价它。

## 查看进度

另开终端在项目根目录运行：

```bash
tail -f training/v3_1_direct_qlora.log
```

每 50 步打印一次 `Iter N: Train loss`，每 50 步评估并保存一次；直接输出路线原定目标 1000 步，本次按预设早停规则在 600 步结束。`Train loss`、`Val loss` 是优化诊断，不等于测试指标。若要看训练记录：

```bash
rg 'Iter [0-9]+: (Train loss|Val loss|Saved adapter)' training/v3_1_direct_qlora.log
```

运行命令：`bash training/run_v3_1_qlora.sh`。本轮已完成训练，所有 50 步检查点保存在 `adapters/v3_1_direct_qlora/`。主评估使用 `adapters/v3_1_direct_selected_qlora/`，它是第 400 步检查点的副本（SHA256 `3aaa9f43941d7c754d0c926b72019322f517c8b7379e44f08ce2d7a0a315ec5f`）。实验使用 4-bit 量化基座上的 LoRA 参数更新，不是全量微调。

## 本次开发集早停规则与执行结果

训练到 500 步时，已记录的最低开发损失为 400 步的 `0.022`；450/500 步均回升。为回应时间约束，在查看任何新测试预测之前固定以下规则：如果 550 和 600 步的开发损失也都**没有低于** 400 步，训练在 600 步停止，并使用开发损失最低的 400 步检查点作主评估；若任一步出现新低，则继续原定 1000 步。实际 550 步为 `0.036`、600 步为 `0.025`，因此 600 步保存后停止，选择 400 步。该选择只用旧开发集；它不含硬重定向题，故早停结果仍需按新测试的探索性边界解释。

## 本轮结果

运行 `bash training/run_v3_1_inference.sh` 后，三组同题预测与逐题原始输出保存在 `evaluation/v3_1_*_direct_{predictions,raw}.jsonl`，汇总见 [直接输出路线报告](../evaluation/training_comparison_v3_1.md) 和同名 JSON。另用旧 200 题做了[同 Prompt 回归检查](../evaluation/v3_1_on_v3_test_comparison.md)。标签→规则路线本轮未训练。新测试题全部为草稿，报告只作探索性内部比较。
