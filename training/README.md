# Qwen3.5 9B 本机训练记录

## 已完成的技术验证

使用 `mlx-community/Qwen3.5-9B-4bit` 本机权重、`mlx-lm 0.31.3` 和 48 条 `synthetic/draft` 样例，完成两步量化权重上的 LoRA（即 QLoRA）冒烟测试。adapter 已成功保存并重新加载，首条查询返回可解析 JSON。训练日志见 `qlora_smoke.log`。

本次只训练了 52 个目标 token，没有验证集和盲测集。日志中的训练 loss 和 adapter 输出仅用于证明技术链路正常，不能说明模型质量、泛化或安全性改善。`adapters/smoke_qwen9b` 是本地临时产物，不提交到版本库。

## 复现命令

```bash
python3 scripts/convert_to_mlx.py data/canonical/candidates_v0.jsonl data/mlx_smoke --allow-draft

.venv/bin/mlx_lm.lora \
  --model ~/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit \
  --train --data data/mlx_smoke \
  --adapter-path adapters/smoke_qwen9b \
  --fine-tune-type lora --mask-prompt --grad-checkpoint \
  --num-layers 4 --batch-size 1 --iters 2 \
  --max-seq-length 1024 --steps-per-report 1 \
  --steps-per-eval 1000 --save-every 2 --seed 42
```

MLX-LM 对已量化模型执行 LoRA 时使用量化基座上的 LoRA 路线。正式训练前，必须先完成人工复核、按语义组切分、冻结评测集，并单独记录模型与数据版本。
