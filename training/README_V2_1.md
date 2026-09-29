# v2.1 Qwen3.5 9B QLoRA 实验

## 数据与目标

- 输入：`data/canonical/training_candidates_v2_1.jsonl`，共 328 条。旧 248 条经项目所有者单人整批接受；新增政治类 80 条仍为 `draft`。详见 `docs/review_attestation_v2.md` 和 `evaluation/data_quality_v2_1.md`。
- 固定切分：`data/splits/v2_1_seed42/`；train 202、dev 64、test 62。按语义组和字符近似泄漏簇切分，测试集不参与调参。
- 两条路线：`labels` 只学习 topic、intent，再用固定政策映射动作；`direct` 直接学习 topic、intent 和六动作。两者使用同一批样本、同一个 4-bit Qwen3.5 9B 基座及同样的 QLoRA 参数。
- 这是量化基座上的 LoRA 适配器训练，不是全量参数微调。`--num-layers 4`、`batch-size 1`、202 步、学习率 `5e-5`、梯度检查点、`--mask-prompt`；一次遍历训练集。

训练前先用直接输出任务跑了 10 步速度测试，稳定段约 0.155 次迭代/秒、峰值内存 18.588 GB；见 `training/v2_1_direct_bench.log`。该短跑 adapter 不用于最终比较。

## 监控正在运行的训练

在项目根目录另开终端：

```bash
tail -f training/v2_1_direct_qlora.log
tail -f training/v2_1_labels_qlora.log
```

只查看关键行：

```bash
rg 'Iter [0-9]+: (Train loss|Val loss|Saved adapter)' training/v2_1_direct_qlora.log
rg 'Iter [0-9]+: (Train loss|Val loss|Saved adapter)' training/v2_1_labels_qlora.log
```

`Iter x` 是当前步数，目标 202；`Train loss` 与 `Val loss` 是优化诊断，不能单独证明测试质量。`It/sec` 用于估计剩余时间，`Peak mem` 是 MLX 报告的峰值内存。每 25 步保存一次 adapter；训练结束检查 `adapters/v2_1_direct_qlora/adapters.safetensors` 和 `adapters/v2_1_labels_qlora/adapters.safetensors`。adapter 保存在本机，受 `.gitignore` 排除。

直接输出路线已完成 202 步，最终训练损失 0.008、最后一次开发集抽样损失 0.013、峰值内存 18.612 GB。最终 adapter 的 SHA-256 为 `b3f52ce54a4b08d39e9e9383cc7c6d8667c925cb83be9690c55d1d7531f835a3`。这些损失不是测试集指标。

标签路线也已完成 202 步，最终训练损失 0.000（日志三位小数精度）、最后一次开发集抽样损失 0.013、峰值内存 9.715 GB。最终 adapter 的 SHA-256 为 `7a1401a87640106cb562af584b55c96f386d9cf06a2d1e0046f837d957c0d718`。

## 复现

模型权重：`~/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit`。本次本机环境：Apple M1 Max、64 GB 统一内存、`mlx-lm 0.31.3`、`mlx 0.32.2`。完整运行参数及每步损失见 `training/v2_1_*_qlora.log`。

```bash
python3 scripts/prepare_training_corpus_v2.py
python3 scripts/validate_dataset_v2.py data/canonical/training_candidates_v2_1.jsonl
# 已冻结的切分目录不会被脚本覆盖；复现时请使用已有文件。
python3 scripts/convert_to_mlx_v2.py data/splits/v2_1_seed42 data/mlx_v2_1_labels --task labels
python3 scripts/convert_to_mlx_v2.py data/splits/v2_1_seed42 data/mlx_v2_1_direct --task direct
```

以上两个转换命令也拒绝覆盖现有输出目录；重跑时先在新目录生成。以下是训练命令模板，`TASK` 分别取 `labels`、`direct`：

```bash
.venv/bin/mlx_lm.lora \
  --model ~/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit \
  --train --data data/mlx_v2_1_TASK \
  --adapter-path adapters/v2_1_TASK_qlora \
  --fine-tune-type lora --mask-prompt --grad-checkpoint \
  --num-layers 4 --batch-size 1 --iters 202 --learning-rate 0.00005 \
  --max-seq-length 1024 --steps-per-report 10 --steps-per-eval 25 \
  --val-batches 16 --save-every 25 --seed 42
```

训练后对同一个冻结测试集分别运行基础模型和两种 adapter；原始文本、预测和 Prompt 哈希保存在 `evaluation/v2_1_*_raw.jsonl` 与 `evaluation/v2_1_*_predictions.jsonl`，汇总见 `evaluation/training_comparison_v2_1.md`。

## 解释边界

`approved` 表示所有者单人接受，来源仍为合成数据。新增 80 条 `draft` 已按用户要求纳入训练和内部量化评估，政治类数值须单列并在复核后重做。六动作由同一假设规则生成，标签路线加规则的表现不能当作独立发现政策。`filter`、`downrank` 是建议启用的条件性规则，不能推断真实搜索结果已经被处理。
