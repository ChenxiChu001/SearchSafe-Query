# SearchSafe Query

A portfolio research prototype for search query safety data and evaluation. It defines **hypothetical** labels and intervention recommendations; it is not affiliated with TikTok and does not reproduce a platform's internal policy.

## Project at a glance

| Version | Candidate queries | Main change |
| --- | ---: | --- |
| v0 | 48 | Topic, intent, and three-way triage |
| v2 / v2.1 | 248 / 328 | Six combinable intervention actions; grouped evaluation and QLoRA |
| v3 | 1,000 | Chinese-only scenarios, CN/SG coverage, stronger negative examples |
| v3.1 | 1,400 | Refined guidelines, 300 more training cases, 100 new holdout cases, and resource navigation |

The v3.1 corpus has six topics, six intents, and six intervention booleans. It contains **synthetic queries** with per-row review status; the whole corpus is not a human-verified gold standard. [Annotation guidelines](policy/annotation_guideline_v3_1.md) and [iteration history](docs/project_iteration_retrospective.md) explain the boundaries and changes.

## Training and evaluation

The project uses Qwen3.5 9B 4-bit with QLoRA on Apple Silicon. The v3.1 run fine-tuned the **direct-output** route; an earlier version also tested a label-to-rule route. Weights and adapters are not included.

On the same 100 synthetic, draft-labeled holdout queries with the same v3.1 prompt, the v3 to v3.1 adapters changed as follows:

| Metric | v3 adapter | v3.1 adapter |
| --- | ---: | ---: |
| Intent macro precision | 79.1% | 88.0% |
| Intent macro recall | 78.8% | 86.8% |
| Exact match on all six intervention booleans | 64/100 | 78/100 |

These are **exploratory internal comparisons**, not production performance estimates. A regression test on the old 200 queries found weaker Block behavior despite a higher overall action score. See the [new holdout report](evaluation/training_comparison_v3_1.md), [legacy regression report](evaluation/v3_1_on_v3_test_comparison.md), and [data-quality profile](evaluation/data_quality_v3_1.md).

## Repository layout

- `data/canonical/`: versioned synthetic candidate corpora.
- `data/splits/`: frozen train, development, and test splits with manifests.
- `data/mlx_*/`: chat-formatted training files and hashes.
- `policy/` and `prompts/`: annotation standards, proposed intervention rules, and model prompts.
- `scripts/`: generation, validation, training-data conversion, inference, and evaluation code.
- `evaluation/`: reports, per-case predictions, and raw inference audits.
- `review/`: review sheets and proposed corrections, including unresolved cases.
- `training/`: run commands, notes, and logs.

## Reproduce

Python 3.11 is used for data and evaluation scripts. QLoRA and inference require an Apple Silicon setup with `mlx-lm[train]` and a locally downloaded `mlx-community/Qwen3.5-9B-4bit` model. The training scripts expect the model under `~/.lmstudio/models/mlx-community/Qwen3.5-9B-4bit`; edit `MODEL_PATH` if yours is elsewhere.

```bash
python3 scripts/validate_dataset.py data/canonical/candidates_v0.jsonl
python3 scripts/convert_to_mlx_v3_1.py data/splits/v3_1_seed42 /tmp/searchsafe-mlx-direct --task direct
```

The frozen v3.1 MLX files are already in `data/mlx_v3_1_direct/`. For the original QLoRA command and checkpoint choice, see [training notes](training/README_V3_1.md). Original model weights and third-party reference datasets are excluded. Source notes for external datasets appear in [SHIELD and VEILED-SH](docs/SHIELD_VEILED_SH.md).
