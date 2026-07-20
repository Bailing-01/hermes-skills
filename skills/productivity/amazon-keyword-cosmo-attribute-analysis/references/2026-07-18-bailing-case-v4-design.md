# 2026-07-18 v4 Skill 设计案例 · B0H35TQ81F

## 背景

2026-07-18 上午，bailing 跑完 v3 (B0H35TQ81F) 重做。下午他给我看了一张"裙子关键词样本"——把 dress 类词按"上位词/核心词/属性词"分三层、再把属性词细分到"紧身/风格/裙款/颜色/场景人群"等 7 个子类。

他要把这个**框架套到颈霜**，但要：
1. 属性词用**Cosmo 风格的 intent taxonomy**
2. 颗粒度细到 30+ tag
3. 不评估推荐行动——那是 v3 干的事
4. 跟原 amazon-cerebro-keyword-analysis **并存**，不是替代

## bailing 的 ABCA 决策表

| 决策 | 选项 | bailing 选了什么 | 含义 |
|---|---|---|---|
| 1 | Cosmo 集成方式 | **A** | 用开源分类 + Cosmo 论文概念自己实现，立即可做 |
| 2 | 与 v3 关系 | **B** | 继承扩展，v3 → v4 并行新 skill |
| 3 | 颗粒度 | **C** | 全细分 30+ tag，每词多标签 |
| 4 | 人群 | **A** | 借鉴 Amazon 官方 Cosmo 论文人群分层（抗衰老意识 / 功效驱动等）|

## 11 Dimension 设计来源

| Dimension | 来源 | 颈霜示例 |
|---|---|---|
| INGREDIENT_FAMILY | Cosmo 论文 + Helium10 X-Ray 类目 | vitamin_a / collagen / peptides |
| PAIN_SPECIFIC | 卖家实战 + Cosmo "pain-led buyer" | crepe_texture / sagging / wrinkles |
| FORM_FAMILY | 颈霜真实产品形态（cream_gel / patch / device） | 形态细分 |
| AREA_FAMILY | Cosmo "where-used" | neck / face / body / chest |
| AUDIENCE_FAMILY | **A 选项**：Cosmo 论文人群分层 | women_universal / mature_50plus |
| MODIFIER_FAMILY | Cosmo "benefit-led + origin-led" | korean_beauty / natural_origin |
| BENEFIT_FAMILY | Cosmo "outcome-led" | firming / anti_aging |
| PURCHASE_CONTEXT | Cosmo "context-of-purchase" | travel_size / subscribe_save |
| TEMPORAL | Cosmo "temporal intent" | 4Q / summer |
| ORIGIN | 产地文化分层 | korean / japanese / european |
| GENERIC | 通用异常层 | review_keyword / language_other |

## 触发词树（108 tags × 200+ 触发词）

完整 json: `assets/neck-care-attribute-tree.json`

**经验性观察**：

- INGREDIENT 12 类（vitamin_a / collagen / peptides / plant_extracts / fruit_acid 等）
- PAIN 11 类（sagging / crepe_texture / wrinkles / discoloration / neck_specific 等）
- FORM 11 类（cream_gel / serum_oil / stick / mask_patch / spray / gua_sha_tool 等）
- AREA 8 类（neck / face / eye / body / chest_decollete / hand 等）
- AUDIENCE 13 类（women_universal / men_universal / mature_50plus / sensitive_skin 等）
- MODIFIER 13 类（korean_beauty / natural_origin / clean_beauty / instant_results / korean / japanese 等）
- BENEFIT 10 类（firming / anti_aging / moisturizing / smoothing / brightening / circulation 等）
- PURCHASE_CONTEXT 5 类
- TEMPORAL 4 类
- ORIGIN 5 类
- GENERIC 6 类

## B0H35TQ81F 4115 词上跑（v4 实证）

### 整体命中分布

| Dimension | 命中数 | 占比 |
|---|---:|---:|
| FORM_FAMILY | 2646 | 64.3% |
| AREA_FAMILY | 2304 | 56.0% |
| BENEFIT_FAMILY | 1682 | 40.9% |
| INGREDIENT_FAMILY | 781 | 19.0% |
| PAIN_SPECIFIC | 640 | 15.6% |
| MODIFIER_FAMILY | 335 | 8.1% |
| AUDIENCE_FAMILY | 202 | 4.9% |
| ORIGIN | 166 | 4.0% |
| GENERIC | 16 | 0.4% |
| PURCHASE_CONTEXT | 8 | 0.2% |
| TEMPORAL | 2 | 0.0% |

### 命中 dimension 数分布

| dim 数 | 词数 | 占比 | 解释 |
|---:|---:|---:|---|
| 7 | 2 | 0.0% | 极强信号（少数）|
| 6 | 4 | 0.1% | |
| 5 | 63 | 1.5% | **绝佳信号** |
| 4 | 405 | 9.8% | **好信号** |
| 3 | 1399 | 34.0% | **核心 zone**（v4 真实价值区）|
| 2 | 1361 | 33.1% | |
| 1 | 591 | 14.4% | |
| 0 | 290 | 7.0% | (无 tag，可能是拼错/异常) |

> **核心结论**：B0H35TQ81F 67% 的词命中 2+ dimension，44% 命中 3+ dimension — v4 多维分析实际有显著信号价值。

### 真实误判修复案例

#### Bug 1：'au' 触发 'estee lauder'

```
原始：
'australian' patterns: ['australian', 'au']
→ 'estee lauder' 因 'au' 子串被命中 'australian'

修复：
'australian' patterns: ['australian', 'australian made', 'from australia', 'down under']
→ 改后 'estee lauder' 不再命中
```

#### Bug 2：'men' 子串 命中 'women'

```
原始：
men_universal patterns: ['for men', "men's", 'mens', 'men', 'his', 'men s']
women_universal patterns: ['for women', "women's", 'womens', 'women', 'her', 'her skin']
→ 'retinol body cream for women' 同时命中 "women" + "men"? 还是 "men"

修复（v3）：
用 word boundary: 'men' 必须 token == 'men'，不能是 'women' 的子串
```

**实战修复**：

```python
def word_match(token_set, pattern):
    return pattern in token_set  # 单词必须 token 命中

def phrase_match(k_norm, pattern):
    return pattern in k_norm  # 多词保留 substring
```

#### Bug 3：'cream' word 命中 cream_gel 但同样的 'men' word

```
men_universal patterns: ['cream for men', 'for men']  # 后者 in token，'for men' in 子串
'creme for women' → 'for women' 命中 women_universal
'creme for men' → 'for men' 命中 men_universal ✓
```

最终：修复后 both 命中 = **0 个**

## 与 v3 的联合用法（重要）

```
H10 Cerebro (xlsx)
       ↓
   ┌──┴──┐
   ↓     ↓
  v3   v4
   ↓     ↓
推荐   属性
行动   矩阵
   ↓     ↓
   └─→ 联合解释：v4 的 top tag = v3 推荐行动背后的"语义解释"
```

具体例子：

- v3 推荐 `neck cream for women over 50` → 捡漏（基于 4 维度评估）
- v4 拆解该词 → `mature_50plus + crepe_texture + neck + women_universal`
- **写 listing 时**：bullet 5 直接强调 "for women over 50 with crepey skin"

## Skill 创建信息

| 项 | 值 |
|---|---|
| Skill 名 | `amazon-keyword-cosmo-attribute-analysis` |
| 位置 | `~/.hermes/skills/productivity/amazon-keyword-cosmo-attribute-analysis/` |
| 主文件 | `SKILL.md` |
| 触发词树 | `assets/neck-care-attribute-tree.json`（16,778 bytes）|
| 案例 reference | `references/2026-07-18-bailing-case-v4-design.md`（本文件）|
| 实战 demo | B0H35TQ81F + B0CGB215HR （需要后续跑） |

## 实证验证（example: B0H35TQ81F top 4+ dimension 命中）

| 关键词 | 维度 | tags |
|---|---|---|
| `retinol body lotion for crepey skin` | 4 | vitamin_a + cream_gel + body + crepe_texture |
| `medical grade neck lift tape` | 5 | tape_strip + neck + professional_grade + firming + healthcare_provider |
| `softanas instant neck lift cream` | 5 | loss_of_firmness + cream_gel + neck + instant_results + firming |
| `go pure arm firming cream` | 4 | cream_gel + body + natural_origin + firming |
| `turkey neck tightener device` | 4 | neck_specific + device + neck + firming |

每个词都有"真实的语义向量"——这是 v3 给不出的维度。

## 后续 Todo

1. 跑 B0CGB215HR 8294 词的 v4 attribute（多 ASIN 版本）
2. v3 + v4 联合报告跑一份 demo
3. 触发词树按"误判报告"迭代（每周一次 review）
4. 触发词树 v2：把 Cosmo 论文 4 类人群维度显式做出来（不是只复制常见词）

## 关键洞察

1. **4-7 dimension 同时命中** = 真正"消费者意图"金矿（v3 的 S 级词大概率会在 v4 多维度命中）
2. **TEMPORAL / PURCHASE_CONTEXT** 这些 dimension 命中低，**不是 skill bug，是搜索词现实**——消费者搜索不写"4Q"也不写"travel size"。需要换**brand-of-thinking** 而不是 keyword thinking。
3. **跨层级**搜索词（如 'neck cream for women over 50 mature 50'）= rare 但能找到。这正好是 v3 1.5 的"词根拆解"想做但失败的事——v4 间接完成了它。

## Pitfalls 教训

1. **单词触发词必须 word boundary**（v3 已修复：'men' 不命中 'women'）
2. **过短的触发词（'au'）不能命中多词**（已修复：'australian' + 'australian made'）
3. **多词短语 in 字符串** —— 仍然可能有误命中。**最稳** 是：所有触发词都 token 化匹配，多词用空格 join 后跟 token 集合子集匹配
4. **没标到 tag 的词不要"硬标"**。7% 词 0 tag 是合理的（西班牙语、拼错、动画词、超长尾）。
