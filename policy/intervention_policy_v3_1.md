# 查询干预规则 v3.1（假设研究原型）

沿用 [v2 六动作定义](intervention_policy_v2.md)和 v3 的 topic/intent 范围。CN 与 SG 的动作政策相同；`redirect_target` 必须匹配查询目的和地区。`filter/downrank` 仍只是针对未来候选结果的条件性建议。政治主题本身不触发限制，明确索取未公开私人信息才按本原型 Block。

v3.1 新增 `resource_navigation`，仅允许 `SUPPORT_SEEKING` 取 `true`。明确搜索求助/举报/报案**入口本身**时完全用相关资源入口替换普通结果，即 `allow=false,filter=false,downrank=false,warning=false,redirect=true,block=false`；这是硬重定向。一般求助保持 `allow=true` 的软引导。真实产品对硬转的呈现方式、用户理解与资源可达性尚未验证；本研究沿用此前“界面不明确标识引导”的假设，不将它说成实际平台行为。

| Topic / intent | `resource_navigation` | 动作与目标 |
| --- | --- | --- |
| `NONE / GENERAL_INFO` | false | 仅 allow。 |
| 四个风险主题 / `GENERAL_INFO` 或 `PREVENTION` | false | allow、filter、downrank。 |
| 四个风险主题 / `SUPPORT_SEEKING` | false | allow、filter、downrank、redirect；相关支持资源。 |
| 四个风险主题 / `SUPPORT_SEEKING` | true | 仅 redirect；匹配 topic、locale 的求助/举报入口。 |
| 四个风险主题 / `HARMFUL_INSTRUCTION` | false | allow、filter、downrank、warning、redirect。 |
| 四个风险主题 / `AMBIGUOUS` | false | allow、filter、downrank、redirect。 |
| 政治类 / `GENERAL_INFO` | false | 仅 allow。 |
| 政治类 / `SUPPORT_SEEKING` | false | allow、filter、redirect；本版仅采样隐私泄露举报求助。 |
| 政治类 / `SUPPORT_SEEKING` | true | 仅 redirect；与地区匹配的隐私泄露举报入口。 |
| 政治类 / `PRIVATE_INFO_REQUEST` | false | 仅 block。 |

未定义组合进入政策复核，不猜测六动作。`redirect_target` 不属于模型本轮直接预测的六动作，而是数据中供资源相关性核查的目标类别。硬转在查询级可标注，但没有候选结果和产品界面，不能评价真实结果质量或用户感受。
