# v3 中文合成数据 Qwen3.5 9B QLoRA 实验

本轮先用未全部审核的 `v3-draft` 数据训练，因此训练、开发和留出指标均为探索性。训练集 700、开发集 100、留出集 200；旧版 164 条中文行全部在训练集，新测试题不沿用 v2.1 的旧测试题。

## 监控进度

在项目根目录另开终端：

```bash
tail -f training/v3_direct_qlora.log
tail -f training/v3_labels_qlora.log
```

只看关键进度：

```bash
rg 'Iter [0-9]+: (Train loss|Val loss|Saved adapter)' training/v3_direct_qlora.log
rg 'Iter [0-9]+: (Train loss|Val loss|Saved adapter)' training/v3_labels_qlora.log
```

`Iter x` 是当前训练步数，目标各 700。`Train loss` 和 `Val loss` 只是优化诊断，不代表留出集表现；`It/sec` 可粗略估算剩余时间，`Peak mem` 是 MLX 报告的峰值内存。结束后应检查 `adapters/v3_direct_qlora/adapters.safetensors` 和 `adapters/v3_labels_qlora/adapters.safetensors`。

## 训练命令

两条路线均使用相同的量化基座、4 层 LoRA、batch size 1、一次遍历训练集。直接输出路线使用修正过的 v3 政策提示；标签路线沿用 v2.1 标签提示。

```bash
.venv/bin/mlx_lm.lora --model ~/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit \
  --train --data data/mlx_v3_direct --adapter-path adapters/v3_direct_qlora \
  --fine-tune-type lora --mask-prompt --grad-checkpoint --num-layers 4 \
  --batch-size 1 --iters 700 --learning-rate 0.00005 --max-seq-length 1024 \
  --steps-per-report 10 --steps-per-eval 50 --val-batches 16 \
  --save-every 50 --seed 42
```

将 `direct` 改成 `labels` 即为标签路线。这里是 4-bit 基座上的 LoRA 适配器训练，并非全量参数微调。若 10 步速度检查显示明显内存或速度问题，应先记录基准再调整参数，并在比较报告中注明。

训练后从 `review/review_v3_60.tsv` 抽查 60 条训练/开发草稿；如发现系统性错标，修订版本并决定是否重训。未经人工核查的 200 条测试行只支持内部探索性比较。

## 本次运行结果与审核交接

两条路线均完成 700 步，均只更新 2.705M LoRA 参数（约基座参数的 0.030%）。直接输出最终训练/开发损失为 `0.014/0.029`，峰值内存 18.621 GB；标签路线为 `0.042/0.067`，峰值 9.715 GB。最低记录开发损失都出现在 600 步，但本次统一比较使用预定的**最终 700 步**检查点，没有用测试题挑选检查点。

最终适配器 SHA-256：

- `adapters/v3_direct_qlora/adapters.safetensors`：`27bae7becef09dcfc63f7b557b0b7b49a7270475a927608548d4d6cace61c030`
- `adapters/v3_labels_qlora/adapters.safetensors`：`71d254a371bc3a93b59972b0687ff6a4aba249fc9e56b9e46eb822be68fe913c`

六组统一测试的原始输出和解析后预测保存在 `evaluation/v3_*_raw.jsonl`、`evaluation/v3_*_predictions.jsonl`；汇总见[训练比较](../evaluation/training_comparison_v3.md)与[错例分析](../evaluation/v3_error_analysis.md)。基础模型及两代标签路线、v3 直接输出均解析 200/200；v2.1 直接输出解析 196/200，4 条违反 Block 排他规则。全部测试标签仍为草稿。

审核表是[review_v3_60.tsv](../review/review_v3_60.tsv)。在 `decision_accept_or_edit` 列填 `accept` 或 `edit`；如果填 `edit`，在 `corrected_topic`、`corrected_intent`、`corrected_intervention` 和 `reviewer_note` 写下裁决。`audit_hint` 只是词面预警，不是模型结论。将填写后的文件交回后，可据此另存修订版并判断是否需要重训。不要直接修改已用于本次报告的冻结草稿文件，否则哈希与对比将失效。
