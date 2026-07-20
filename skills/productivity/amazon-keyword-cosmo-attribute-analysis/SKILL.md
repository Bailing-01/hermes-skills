---
name: amazon-keyword-cosmo-attribute-analysis
description: 对 H10 反查报表（Cerebro/Magnet/BlackBox 输出）做 **Cosmo-aware 多维属性词分析**。不是分类、不评估推荐行动，专门把每个词拆成「主词-属性-人群场景」的细颗粒度。灵感来源：bailing 2026-07-18 看到的裙子关键词样本 + Amazon Cosmo 论文的"consumer intent taxonomy"。与 `amazon-cerebro-keyword-analysis` (v3) 是兄弟 skill，本 skill 专注 v3 没细的"属性深度"。
trigger:
  - "cosmo 分析"
  - "多维属性词"
  - "Cosmo-aware"
  - "成分党意图"
  - "人群标签"
  - "属性词树"
  - "属性词 vs 上位词"
platforms: [macos, linux]
---

# Amazon Keyword Cosmo-Aware Attribute Analysis Skill（v4）

## 触发场景

- "把这份 H10 报表拆成 cosmo-aware 的属性维度"
- "把词拆成主词 / 成分 / 痛点 / 形态 / 人群场景"
- "对标 Amazon Cosmo 的 intent 分层"
- "看到裙子的属性词拆解法，想应用到颈霜"

**不触发的场景**：
- 想要 4 维度评估推荐行动 → 用 `amazon-cerebro-keyword-analysis` v3
- 想要关键词相关性打分 → v3
- 想要流量分级 → v3

## 目标

把 H10 任意关键词报表（Cerebro / Magnet / BlackBox 导出 CSV 或 xlsx）中的**每个关键词**打上 **11 个属性 dimension 的多 tag 标签**，输出**细颗粒度的属性词矩阵**。

### 11 个属性 dimension（Cosmo consumer intent taxonomy 对齐）

| Dim | 含义 | Cosmo intent | 颈霜示例 |
|---|---|---|---|
| **INGREDIENT_FAMILY** | 成分家族 | science-led | collagen / retinol / peptides |
| **PAIN_SPECIFIC** | 具体痛点 | pain-led | crepe_texture / sagging / wrinkles |
| **FORM_FAMILY** | 产品形态 | format-led | cream_gel / stick / patch / device |
| **AREA_FAMILY** | 使用部位 | where-used | neck / face / body / chest |
| **AUDIENCE_FAMILY** | 人群细分 | audience-led | women_universal / mature_50plus |
| **MODIFIER_FAMILY** | 修饰/价值主张 | benefit-led + origin-led | korean_beauty / natural_origin |
| **BENEFIT_FAMILY** | 功效 | outcome-led | firming / anti_aging / hydration |
| **PURCHASE_CONTEXT** | 购买场景 | context-of-purchase | travel_size / subscribe_save |
| **TEMPORAL** | 季节/事件 | temporal | 4th_quarter / summer |
| **ORIGIN** | 产地/文化 | culture-led | korean / japanese / european |
| **GENERIC** | 通用异常 | meta | review_keyword / language_other |

**总数：108 个细分 tag，200+ 触发词**。

详细属性树 JSON：`assets/neck-care-attribute-tree.json`

## 与 v3 的关系（重要）

| 维度 | v3 (现) | v4 (本 skill) |
|---|---|---|
| 颗粒度 | 6 子类 | 11 dimension × 108 tag |
| 主词 vs 属性 | 全归 5 大类 | 分开：主词 vs 11 dimension 属性 |
| Cosmo 集成 | ❌ | ✅ 按 Cosmo consumer intent 对齐 |
| 输出 | 4 维度评估 | 纯属性矩阵（无数值评估） |
| 数据源 | 单 ASIN Cerebro | 任意 H10 输出 |

**v4 不评估是否值得打，v3 评估是否值得打** —— 两个 skill 共生，不是替代。

## 工作流

### Step 1：加载词表

输入支持格式：

```python
# 1. Cerebro xlsx（35 列模式 A 或 34 列模式 B）
# 2. Cerebro CSV（已导出，UTF-8）
# 3. Magnet CSV（关键词挖掘结果）
# 4. BlackBox CSV（选品关键词输出）
# 5. 关键词列表（直接传 list[str]）
```

每行取出"关键词"列（自动识别，常见列名：`关键词词组`, `Phrase`, `Keyword`, `keyword`）。

### Step 2：属性词打标（多 tag 多维）

```python
from collections import defaultdict

def tag_keyword(kw: str) -> dict:
    """返回 {dim_name: [tag1, tag2, ...], ...}"""
    k_tokens, k_norm = tokenize_for_match(kw)
    out = {}
    for dim_name, dim_dict in tree.items():
        if dim_name == 'CORE': continue
        tag_set = set()
        for tag_name, patterns in dim_dict.items():
            for p in patterns:
                if ' ' in p:
                    # 多词 pattern: 字符串 in
                    if p in k_norm:
                        tag_set.add(tag_name)
                        break
                else:
                    # 单词 pattern: token boundary 匹配
                    if p in k_tokens:
                        tag_set.add(tag_name)
                        break
        if tag_set:
            out[dim_name] = list(tag_set)
    return out
```

**匹配规则**（重要）：
- **多词 pattern** → 字符串 `in` 匹配
- **单词 pattern** → 必须 word boundary（防止 'men' 命中 'women'）

### Step 3：属性矩阵输出

#### 输出 1：CSV（每行 1 词 + 11 维标签）

```
序号, 关键词,
主词(CORE),
INGREDIENT_FAMILY,
PAIN_SPECIFIC,
FORM_FAMILY,
AREA_FAMILY,
AUDIENCE_FAMILY,
MODIFIER_FAMILY,
BENEFIT_FAMILY,
PURCHASE_CONTEXT,
TEMPORAL,
ORIGIN,
GENERIC
```

每条 tag 行：`vitamin_a|peptides` 形式（多个 tag 共享 dim）。

#### 输出 2：属性词矩阵分析（Opt 2）

| 维度 | tag | 命中词数 | TOP 5 示例 |
|---|---|---|---|

输出"哪个维度哪个 tag 出现最多"——大盘观察。

### Step 4：Ceremo-aware 多维观察模板

调用本 skill 后，**你应该用以下 4 步判断词的价值**：

#### 4.1 主词稳定性
- 看 `CORE = 'neck'` 这类主词占了多少？—— 新词比老词多说明品类在演化

#### 4.2 成分党信号
- INGREDIENT_FAMILY 里**新出现的 tag** = 新成分趋势（如 2026 年 `'pdrn'` / `'nad'` 这种）
- 同比上周比 → 是真趋势还是噪音

#### 4.3 痛点 + 形态 cross-tab
- 哪些痛点用哪些形态被搜索？ → 给 listing 提供 "X 痛点 → 推荐形态" 的决策

#### 4.4 人群 + 场景交叉
- 人群分类对场景是不是有交叉？ → 给广告系列"按客群 → 按场景"分层

## 验证清单

跑完报告后**必须自查**：

- [ ] `dimension 命中数` 列加总 = 总词数（不是重复加，应少于总词数因一词多维）
- [ ] 命中最多 dim 的词**是符合语义的**（不应是误判）
- [ ] 'men_universal' 和 'women_universal' both 命中 < 5 个（防止子串污染）
- [ ] ORIGIN `australian` 不应命中'estee lauder'这种纯属巧合词
- [ ] CSV 11 维标签列都有数据（少数 0 命中可以）

## 输出

| 维度 | 路径 |
|---|---|
| CSV 主文件 | `~/Documents/keyword-cosmo-attribute-{input_name}.csv` |
| Obsidian 报告 | `~/Documents/ObsidianVault/01_有道原貌/Ⅳ输出/知识星球/yyyy-mm-dd-keyword-cosmo-attribute-{input_name}.md` |
| 双路径同步 | 同 v3 规则：obsidian + `~/` 家目录 |

## Pitfalls（已知坑）

1. **单词触发词必须 word boundary**（已修复：见上面匹配规则）
2. **多词触发词 in 字符串会误命中**（例如 `'australian'` 命中 `'estee lauder'` 因 'au' 在名字里）—— **解法**：把单词触发词拆出来用 token 匹配；只在多词 phrase 才 in 字符串
3. **'for women' 和 'cream' 同时出现在 'cream for women'** → 'women' 单字会被 'cream' 触发混 → **解法**：用精确 phrase 'for women'
4. **'cream' 自身是 FORM_FAMILY 词，不会被任何 tag 单独占**——'col' token 不会误触发
5. **4200 行 Cerebro → 大约 30% 是 multi-tag（命中 3+ dimension）**（实测 B0H35TQ81F）
6. **TEMPORAL 和 PURCHASE_CONTEXT 维度大部分词命中 0** —— 这是合理的（搜索词 99% 不带季节/购买场景词）
7. **触发词树需要迭代**：每次跑完后看 TOP 误判，补触发词或加排除词
8. **没有真实 Cosmo API**：本 skill 是 "Cosmo 风格的属性树" 实现，不是真接 Cosmo 接口。要接 Cosmo 等亚马逊对外开放。
9. **🚨 CSV 含逗号/特殊字符会整行列错位（2026-07-19 BUG）**——见下面强制约束
10. **🚨 v4.1 数值口径必须沿用 v3，不要自创（2026-07-19 教训）**——见下面

### 🚨 Pitfall #9:CSV 关键词含特殊字符整行列错位

**真实事故**：B0H35TQ81F V4.1 CSV 生成时，43 行关键词里有英文逗号 `,` 或 `&` / 撇号 `/` 等特殊字符：

```
anua collagen retinol refining gua sha cream, neck cream for lifting & firming, jawline to décolleté
```

**Bug 现象**：用 `csv.DictWriter` + 手写拼字符串（或任何不强制引号包裹的写入方式），Excel/Numbers 打开后把这 1 个关键词识别成 3 列，导致**后续 16 个数据列整体右移 1-2 列**（搜索量/竞品/蓝海度全错位到错误的关键词下）。

**为什么 V4.1 的 v41-zh.csv 中招**：第一次写中文版 CSV 时为图省事用了手动字符串拼接 `f.write(','.join(...))`，完全没加引号包裹。

### ⚠️ 强制约束（跑任何 CSV 输出必须遵守）

```python
# ✅ 正确写法：用 csv.writer + QUOTE_MINIMAL（默认）
import csv

with open(path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(header)
    for row in data:
        writer.writerow(row)

# ❌ 错误写法 1：手写 f.write(','.join(row))
with open(path, 'w', encoding='utf-8') as f:
    f.write(','.join(header) + '\n')
    for row in data:
        f.write(','.join(str(c) for c in row) + '\n')  # 含逗号的 cell 必然炸

# ❌ 错误写法 2：用 DictWriter 但忘记加 quoting 参数
writer = csv.DictWriter(f, fieldnames=...)  # 默认有 quoting=QUOTE_MINIMAL ✓，但不显式
writer.writerow(row)
# 这个其实 OK，但建议显式写出更安全

# ❌ 错误写法 3：把 dataframe 直接 to_csv 但用单引号
df.to_csv(path, quotechar="'", quoting=csv.QUOTE_NONE)  # 完全不加引号，必炸
```

### 自验证脚本（每次跑完必跑）

```python
import csv

def verify_csv(path):
    """跑完 CSV 必须验证：每行列数必须等于表头列数"""
    with open(path) as f:
        rows = list(csv.reader(f))
    header_ncols = len(rows[0])
    broken = [(i, len(r), r[:3]) for i, r in enumerate(rows) if len(r) != header_ncols]
    if broken:
        print(f"❌ {path} 列数不一致 {len(broken)} 行")
        for b in broken[:5]:
            print(f"   行 {b[0]}: 列数 {b[1]}, 内容: {b[2]}")
        return False
    print(f"✅ {path} 列数一致 ({len(rows)-1} 行 × {header_ncols} 列)")
    return True

# 跑完任意 csv 后调用
verify_csv('/Users/bailing/Documents/keyword-cosmo-attribute-{input}.csv')
verify_csv('/Users/bailing/Documents/keyword-cosmo-attribute-{input}-zh.csv')
```

### 出错时的排错步骤

1. **打开 Excel 看**：错位行通常表现是「某个词的关键词列突然出现一些短语片段」—— 这些就是被截断的部分
2. **用 csv.reader 验证列数**：`list(csv.reader(open(path)))` 看哪行列数 ≠ 表头列数
3. **找含特殊字符的关键词**：`grep "[,&;]"` 或 Python `if ',' in keyword`
4. **修**：用 `csv.writer(quoting=csv.QUOTE_MINIMAL)` 重写

### 即用工具：`scripts/safe_csv.py`（跨 skill 共享，**canonical 在 v3**）

直接 import，避免重新发明轮子：

```python
import sys
sys.path.insert(0, '/Users/bailing/.hermes/skills/productivity/amazon-cerebro-keyword-analysis/scripts')
from safe_csv import write_csv_safe, verify_csv_safe, must_verify

# 写
write_csv_safe('/tmp/out.csv', ['关键词', '搜索量'], [['anua, neck cream', 648]])

# 验证（建议每次写完都跑）
verify_csv_safe('/tmp/out.csv')

# 强制验证（CI 用，错位直接 raise）
must_verify('/tmp/out.csv')
```

**Canonical 位置**：`amazon-cerebro-keyword-analysis/scripts/safe_csv.py`（已升级为跨 skill 共享工具——v3 Pitfall #13 / v4.1 Pitfall #9 都引用同一份）
**为什么共享**：amazon-* 任何 skill 写 CSV 都可能含逗号关键词/ASIN/品牌名。集中维护一份，避免每个 skill 各自维护一份副本漂移。

**实战案例**：B0H35TQ81F 颈霜 22 列全集（11 属性 + V3 4 维度）的完整 session 记录见 `references/2026-07-19-v41-bailing-22col-case.md`——包含 3 个真实坑（Pitfall #9/#10/#14）、4 维度实测分布、跨 skill 协作模板。

提供 4 个函数：
- `write_csv_safe(path, header, data)` — 安全写入，自动转义
- `verify_csv_safe(path)` — 验证列数一致性（每行列数 = 表头列数）
- `find_broken_rows(path)` — 列出所有错位行的行号/列数/内容
- `must_verify(path)` — 强制验证，错位直接 raise

### ⚠️ Pitfall #17: 表头列名-数据对应必须额外验证（2026-07-20）

`safe_csv.verify_csv_safe` 只验证"列数一致"，**不验证"表头列名 = 数据列语义"**。手写 `data.append([...])` 时多/少一列照样能写出来，列数检查通过但内容全错位。

**修复**：本 skill 额外提供 `scripts/verify_csv_columns.py`：
- `verify_csv_columns(path, expected=None, show_samples=False)` — 验证表头列名 == 预期（如果指定）+ 列名非空 + 数据列至少有非空值
- `must_verify_columns(path, expected=None)` — 强制验证，错位 raise

```python
import sys
sys.path.insert(0, '/Users/bailing/.hermes/skills/productivity/amazon-keyword-cosmo-attribute-analysis/scripts')
from safe_csv import write_csv_safe, verify_csv_safe, must_verify
from verify_csv_columns import must_verify_columns

# 写 listing 种子词 / 主推池 等按列名索引拼数据的 CSV 后必跑
write_csv_safe(path, HEADER, data)
must_verify(path)                          # 验列数
must_verify_columns(path, expected=HEADER)  # 验列名-数据对应（新加）
```

### 推广到所有亚马逊/H10/listing 类 CSV 输出

任何把亚马逊词条、ASIN、标题、变体名、评论摘录、产品描述写 CSV 都会遇到这个问题——这些字段**几乎都含逗号**。统一约定：

- ✅ 写 csv **强制** `csv.writer(quoting=csv.QUOTE_MINIMAL)` 或 `DictWriter` 默认模式
- ❌ 永远不要 `f.write(','.join(row))` 手工拼
- ✅ 写完 **强制** 跑 `verify_csv(path)` 自检
- ✅ Excel 打开前用 `pandas.read_csv(path)` 在 Python 里先验证一轮

### 🚨 Pitfall #10: v4.1 数值口径必须沿用 v3，不要自创（2026-07-19 教训）

**真实事故**：跑 v4.1 时，我自创了「搜索量/竞品数 比值 5 档定性」（偏冷/温和/中等/偏激烈/激烈）和「log 数学分 0-100」，**未先加载 `amazon-cerebro-keyword-analysis`（v3）查已有的 4 维度定义**。

用户看到 PDF 后立刻指出：
- "第一个竞品=0 怎么还红海" → 旧公式硬判 0 分，竞品=0 被错判红海
- "先去看一下我们 V3 版本是怎么去通过竞品，然后判断蓝海程度的" → 直接要求对回 v3 口径

**正确做法**：跑 v4.1 前**必须**先 skill_view('amazon-cerebro-keyword-analysis') 拉 v3 的 4 维度定义（Step 3 维度 1-4）。v4.1 的数值列 = 直接 copy v3 定义，不要创新。

**为什么不能创新**：用户跑亚马逊分析时，会同时跑 v3 CSV 和 v4.1 CSV。两份报告列名/口径不一致 → 用户必须做 mental mapping 才能对照。这是用户立即会发现的体验问题。

**已落地修复**：v4.1 现在沿用 v3 全部定义。v3 改了 v4.1 也要同步改（两个 skill 的"蓝海度"列名 + 5 档名称必须永远同步）。

**推广**：v4.1 → v5、v5 → v6 时，每次扩展数值列都要重新检查 v3 是否有对应定义。

### 🚨 Pitfall #16: brand-as-blue-ocean（继承 V3 Pitfall #16 / 2026-07-20 B0CGB215HR 案例）

V3/V4.1 的蓝海度公式只看 `comp < 500`，但**不区分"竞品少是因为没人打"和"竞品少是因为巨头独占"**。B0CGB215HR 实测：

| 词 | vol | comp | 系统判 | 实际 |
|---|---:|---:|---|---|
| dr melaxin | 369,351 | 157 | 蓝海 | 品牌护城河，应判"否定" |
| cerave | 151,215 | 438 | 蓝海 | 品牌护城河，应判"否定" |

**修复**：V4.1 输出 CSV 后，必须**遍历"蓝海"档词，凡是 token 命中 BRAND_LIBRARY 的 → override 为"否定(品牌词护城河)"**。详见 V3 skill 的 Pitfall #16 + `references/2026-07-20-bailing-case-brand-moat.md`。

### 🚨 Pitfall #17: listing 种子词 CSV 表头列索引错位（2026-07-20 案例）

**真实事故**：B0CGB215HR 跑 listing-种子词 CSV 时，列数 `must_verify()` 通过（19 列一致），但**"命中维度数"列全部显示 `-`**——因为手写 `data3.append([...])` 时多填了一列 `ORIGIN`，表头只有 19 列但数据实际写了 19 列，列名-数据语义错位。

**根因**：`safe_csv.verify_csv_safe` 只验证"列数一致"，**不验证"表头列名 = 数据列语义"**。手写 list 索引时多/少一列照样能写出来，列数检查通过。

**修复**：写完 listing 种子词 / 主推池 / 任何"按列名索引拼数据"的 CSV 后，**必须额外跑 `verify_csv_columns(path, expected=HEADER)` 验证表头列名 == 实际数据列**。

新工具：`scripts/verify_csv_columns.py`（canonical 在本 skill，与 `safe_csv.py` 并列）。

```python
from verify_csv_columns import verify_csv_columns, must_verify_columns

# 写完 listing 种子词 CSV 后
write_csv_safe(path, HEADER3, data3)
must_verify(path)                        # 验列数（已有）
must_verify_columns(path, expected=HEADER3)  # 验列名-数据对应（新加）
```

或者**用 DictWriter 避免索引错位**（推荐）：
```python
from collections import OrderedDict

def write_csv_dict(path: str, header: List[str], data_dicts: List[dict]):
    """DictWriter 写 CSV，列名-数据自动对齐，不会错位"""
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=header, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for d in data_dicts:
            w.writerow({k: d.get(k, '-') for k in header})
```

---

## 实战案例

### 案例 1：B0H35TQ81F 颈霜 Cerebro（2026-07-18）

- 输入：`US_AMAZON_cerebro_B0H35TQ81F_2026-07-18.xlsx`（4115 词）
- 输出：见 `references/2026-07-18-bailing-case-v4-design.md`
- B0H35TQ81F 22 列全集 + 3 个真实坑（2026-07-19）：见 `references/2026-07-19-v41-bailing-22col-case.md`
- **B0CGB215HR V4.1 + brand-as-blue-ocean + listing 种子词表头错位（2026-07-20）**：与 V3 skill 共享一份 case reference → `../amazon-cerebro-keyword-analysis/references/2026-07-20-bailing-case-brand-moat.md`

**TOP 实际命中**：

| Dimension | 命中数 | TOP 3 tag |
|---|---|---|
| FORM_FAMILY | 2646 (64.3%) | cream_gel / serum_oil / stick |
| AREA_FAMILY | 2304 (56.0%) | neck / face / body |
| BENEFIT_FAMILY | 1682 (40.9%) | firming / anti_aging / rejuvenation |
| INGREDIENT_FAMILY | 781 (19.0%) | collagen / vitamin_a / plant_extracts |
| PAIN_SPECIFIC | 640 (15.6%) | wrinkles / crepe_texture / sagging |
| MODIFIER_FAMILY | 335 (8.1%) | korean_beauty / natural_origin / instant |
| AUDIENCE_FAMILY | 202 (4.9%) | women_universal (138) / men_universal (37) |
| ORIGIN | 166 (4.0%) | korean (163) |
| GENERIC | 16 (0.4%) | review_keyword |
| PURCHASE_CONTEXT | 8 (0.2%) | travel_size / bulk_size |
| TEMPORAL | 2 (0.0%) | summer_specific |

**4+ dimension 同时命中样本**：

- `retinol body lotion for crepey skin` → vitamin_a + cream_gel + body + crepe_texture
- `medical grade neck lift tape` → tape_strip + neck + professional_grade + firming + healthcare_provider
- `softanas instant neck lift cream` → loss_of_firmness + cream_gel + neck + instant_results + firming

## 输出文件路径约定

| 资源 | 路径 |
|---|---|
| Skill 主文件 | `~/.hermes/skills/productivity/amazon-keyword-cosmo-attribute-analysis/SKILL.md`（本文件）|
| 属性树 JSON | `~/.hermes/skills/productivity/amazon-keyword-cosmo-attribute-analysis/assets/neck-care-attribute-tree.json` |
| 实战案例 | `~/.hermes/skills/productivity/amazon-keyword-cosmo-attribute-analysis/references/2026-07-18-bailing-case-v4-design.md` |

## 相关 Skill

- **`amazon-cerebro-keyword-analysis`** (v3)：跑 H10 Cerebro 反查 + 4 维度评估 + 推荐行动。**本 skill 的上游/下游**——本 skill 拿 H10 输出，做属性词细分；v3 拿 H10 输出，做 4 维度评估。两 skill 可串联：`Cerebro xlsx → v4 属性 → v3 评估（用 v4 属性加进推荐上下文）`
  - **共享「蓝海度」5 档口径**（2026-07-19 bailing 拍板）：v4.1 的"蓝海度"列 = v3 Step 3 维度 4 的竞品数绝对值 5 档（蓝海/温和/一般/激烈/极激烈）。两个 skill 的"蓝海度"列名 + 5 档名称必须永远同步——详见 Pitfall #10。
- **`amazon-product-research`**：选品用
- **`sellersprite-cli`**：直接调 43 个 Amazon 数据工具的 CLI

## 跨品类移植配方（port to new category）

v4 触发词树是**颈霜专用**的。**未来要把 v4 套到 loafers/earbuds/pet-food 等品类，必须重建触发词树**。下面是 4 步法：

### Step A：跑一遍原品类 token 化样本
- 拿 1000–5000 词真实 H10 报表（任意品类）
- 跑一遍触发词树，看哪些词 tag 命中 0（盲区）vs 哪些词误命中（噪声）

### Step B：补充/删除触发词
- 对每个新出现的高频 pattern（>5 次），**加入新触发词或新 dimension**
- 对误命中（如"loan"被 loan-fee 命中），**改用 token 边界或更长 phrase**

### Step C：替换品类专属维度
- 颈霜的 `PAIN_SPECIFIC` 是 crepe/sagging/wrinkles — loafers 应该是 `pain_arch / pain_blister / pain_heel / pain_circulation`
- 颈霜的 `AREA_FAMILY` 是 neck/face/body — loafers 应该是 `size / width / arch / insole / outsole`
- 其他 9 个 dimension 大多数 pattern 可复用（ingredient/origin/modifier/benefit 跨品类通用）

### Step D：跨品类保留的 5 个通用 dimension
| Dim | 跨品类通用性 | 复用难度 |
|---|---|---|
| ORIGIN | 100%（所有品类都有产地）| 直接复用 |
| MODIFIER_FAMILY | 90%（natural/organic/korean/clean 全通用）| 复用 + 增补品类专属修饰 |
| BENEFIT_FAMILY | 70%（firming/anti-aging/moisturizing 是 60% 品类都关心）| 复用 + 增补 |
| PURCHASE_CONTEXT | 100%（travel/subscribe/auto-delivery 不分品类）| 直接复用 |
| TEMPORAL | 100%（季节/事件跨品类通用）| 直接复用 |

需要重做的 5 个品类专属 dimension：INGREDIENT_FAMILY / PAIN_SPECIFIC / FORM_FAMILY / AREA_FAMILY / AUDIENCE_FAMILY。

---

## 🧭 Decision Tree (跑 v4 的标准决策路径)

```
输入：H10 报表 → 关键词列表
         │
         ▼
[Step 1] 触发词树是否覆盖当前品类？
         │
   颈霜/美妆/护肤 ──┼── 其他品类
   直接跑 v4          走"跨品类移植"4 步
         │
         ▼
[Step 2] 每个关键词打 11 dim 标签
   (多词 phrase in 字符串，单词 token boundary)
         │
         ▼
[Step 3] 统计 + 排序 + cross-tab
   - 哪些 dim 命中 0？（可能树没覆盖）
   - 哪些 dim 命中 >60%？（说明该品类"标签化强"）
   - 哪些词 4+ dim 同时命中？（真实金矿）
         │
         ▼
[Step 4] 跟 v3 联合用
   v3 给"打不打", v4 给"为什么打" → listing bullet 5 写 v4 top tag
```

## ✅ v4 Self-Check (交付前必跑)

```markdown
□ 触发词树覆盖当前品类了吗？(没覆盖 → 走跨品类移植)
□ 单词触发词都加了 word boundary？(没加 → 'men' 命中 'women' 这种 bug)
□ 误判词 < 5%？(高 → 触发词改严或加 token boundary)
□ 'men_universal' ∩ 'women_universal' 双命中 < 5 个？(高 → 单词触发词有问题)
□ ORIGIN 'australian' 没命中 'estee lauder' 这种巧合词？(高 → 单词太短)
□ 4+ dim 命中词是真实长尾词（不是巧合）？(→ 看实际样本)
□ CSV 11 维列都有数据（部分 0 可以，但所有 dim 都 0 是 bug）？
```

---

## 与 v3 skill 的串联用法

```python
# 推荐工作流：先 v3 找出"值得打的词",再 v4 拆"为什么值得打"
import json
from v3 import run_cerebro_v3          # 跑 4 维度评估
from v4 import tag_keyword             # 跑 11 dim 属性

# 跑 v3
v3_results = run_cerebro_v3("B0H35TQ81F_cerebro.xlsx")
# 拿到 Top 30 捡漏(优先) 词

# 对每个 Top 30 词跑 v4,得到"为什么是它"
for kw in v3_results['top_pickup']:
    tags = tag_keyword(kw)
    # tags = {INGREDIENT_FAMILY: ['vitamin_a'], AREA_FAMILY: ['neck'], BENEFIT_FAMILY: ['firming'], ...}
    
    # 写 listing bullet 5 时, 直接用这些 tag
    bullet = f"For {tags['AUDIENCE_FAMILY'][0]} with {tags['PAIN_SPECIFIC'][0]} on {tags['AREA_FAMILY'][0]}: "
    bullet += f"{tags['INGREDIENT_FAMILY'][0]}+{tags['BENEFIT_FAMILY'][0]} formula"
```

**示例输出**（基于 B0H35TQ81F Top 30 真实数据）：
- v3 推荐 "neck cream for women over 50"
- v4 拆解 → `mature_50plus` + `crepe_texture` + `neck` + `women_universal` 4 tag
- Listing bullet 5 写："For women over 50 with crepey skin on neck: anti-aging firming formula"

---

## v4.1 全维度版（2026-07-19 bailing 新增需求 + V3 完整 4 维度融入）

**v4.1 = V4 属性（11 维 × 108 tag）+ V3 完整 4 维度评估（相关性 / 流量 / 准入难度 / 蓝海度）**

### 4 维度完整定义

| # | 维度 | 来源列（Cerebro）| 5 档映射 | 实操含义 |
|---|---|---|---|---|
| 1 | **相关性** | `竞品表现得分` | 8-10=高 / 6-8=中 / 4-6=弱 / <4=不相关 | 词是否真属于你的产品 |
| 2 | **流量等级** | `搜索量` | S/A/B/C/D（≥50k/≥10k/≥5k/≥1k/<1k） | 词的流量大小 |
| 3 | **准入难度** ⭐ V4.1 新增 | `ABA 转化份额` | 友好<15% / 一般15-30% / 高30-50% / 很高50-70% / 极激烈>70% / **无数据=缺失或=0** | **头部垄断程度**——蓝海但头部锁死就没空隙 |
| 4 | **蓝海度** | `竞品数` | 蓝海<500 / 温和500-1k / 一般1k-5k / 激烈5k-10k / 极激烈≥10k | 竞品少 = 蓝海 |

**bailing 加准入难度维度的根本原因**：**光看蓝海度不够**——竞品少但头部垄断（ABA>70%）的词，白牌照样打不进去。准入难度解决"光蓝海没用、看有没有空隙"的问题。

### v4.1 输出列（共 22 列）

```
1. 序号
2. 关键词
3. 原分类(v3)
4-14. 11 维属性（成分家族/痛点细分/产品形态/使用部位/目标人群/修饰/功效/购买场景/季节事件/产地文化/通用异常）
15. 搜索量
16. 流量等级
17. 竞品数
18. 蓝海度
19. ABA转化份额(%)           ← V4.1 新增
20. 准入难度                  ← V4.1 新增
21. 竞品表现得分              ← V4.1 新增
22. 相关性等级                ← V4.1 新增
```

### V3 推荐行动公式（4 维度反推）

```python
def recommend_action(traffic_lv, relevance_lv, entry_lv, blue_lv):
    # 1. 不相关 → 观察
    if relevance_lv == '不相关': return '观察'
    # 2. 极激烈 → 否定
    if entry_lv == '极激烈' or blue_lv == '极激烈': return '否定'
    # 3. 蓝海 + 高相关 + 友好 → 捡漏 (优先)
    if blue_lv == '蓝海' and entry_lv in ('友好', '一般') and relevance_lv == '高':
        return '捡漏(优先)'
    # 4. 温和 + 友好 → 主推
    if blue_lv in ('温和', '蓝海') and entry_lv in ('友好', '一般'):
        return '主推'
    # 5. 一般 + 大流量 → 拓词
    if blue_lv == '一般' and relevance_lv == '高' and traffic_lv in ('S', 'A'):
        return '拓词(中后期)'
    # 6. 一般 + 一般 → 防守
    if blue_lv == '一般' and entry_lv in ('一般', '高'):
        return '防守'
    if blue_lv in ('激烈', '极激烈'): return '观察'
    return '观察'
```

**金标准捡漏**：蓝海 + 友好准入 + 高相关 + C/D 级流量（新品 0-2 周能打）

### v4.1 vs v4 区别

| 维度 | v4（纯属性） | v4.1（V4+V3全维度）|
|---|---|---|
| 颗粒度 | 11 dim × 108 tag | 同 v4 + 4 维度评估 |
| 搜索量 | ❌ | ✅ |
| 流量等级 | ❌ | ✅ S/A/B/C/D |
| 竞品数 | ❌ | ✅ |
| 蓝海度 | ❌ | ✅ V3 5 档 |
| ABA 转化份额 | ❌ | ✅ ⭐ v4.1 新增 |
| 准入难度 | ❌ | ✅ ⭐ v4.1 新增 |
| 竞品表现得分 | ❌ | ✅ ⭐ v4.1 新增 |
| 相关性等级 | ❌ | ✅ ⭐ v4.1 新增 |
| 输出列数 | 13 | **22** |

### ⚠️ V4.1 也必须加品牌词护城河 Step 0（2026-07-20 B0CGB215HR 教训）

**V3 新增 Pitfall #16 + Step 0 品牌词预过滤**（详见 `amazon-cerebro-keyword-analysis` SKILL.md）。**V4.1 必须同步**——同一份数据两份报告,口径必须一致。V4.1 在生成 22 列前必须先做品牌词过滤,把命中头部品牌词库（`dr melaxin` / `cerave` / `loreal` / `estee lauder` / `olay` / `roc` / `gold bond` 等）的词 override 成"否定",不进 22 列推荐池。

**为什么必须同步**：跨 skill 协议第 5 条 + 第 6 条——V3/V4.1 共用同一份 H10 输入,如果 V3 过滤了品牌词而 V4.1 不过滤,两份 CSV 同一行的"推荐行动"会不一致,用户对照时立即发现。

**v4.1 = V4 属性 + 4 个数值维度（搜索量 / 流量等级 / 竞品数 / 蓝海度）**。

**⚠️ 重要**：这 4 个数值维度**直接沿用 V3 的定义**，不要自己发明新口径。具体映射：

| V4.1 列 | 来源 | V3 skill 哪里定义 |
|---|---|---|
| 搜索量 | Cerebro xlsx 第 6 列 | — |
| 流量等级 S/A/B/C/D | 按搜索量分档 | V3 `Step 3 维度 2`（S≥50k / A 10k-50k / B 5k-10k / C 1k-5k / D<1k）|
| 竞品数 | Cerebro xlsx 第 12 列 | — |
| 蓝海度 | 按竞品数绝对值 5 档 | V3 `Step 3 维度 4`（<500=蓝海 / 500-1k=温和 / 1k-5k=一般 / 5k-10k=激烈 / ≥10k=极激烈）|

**为什么必须沿用 V3 而不是自创口径**：见下方 Pitfall #10「v3/v4 口径一致性」。

### v4.1 vs v4 区别

| 维度 | V4（纯属性） | V4.1（属性+数值）|
|---|---|---|
| 颗粒度 | 11 dim × 108 tag | 同 V4 + 4 个数值维度（沿用 V3 定义）|
| 搜索量 | ❌ | ✅ |
| 流量等级 | ❌ | ✅ S/A/B/C/D（沿用 V3）|
| 竞品数 | ❌ | ✅ |
| 蓝海度 | ❌ | ✅ 5 档定性（沿用 V3 竞品数绝对值，非自创）|
| 输出列数 | 13 | 18 |

## 📊 蓝海度口径（沿用 V3）

> **bailing 拍板（2026-07-19）**：和 V3 `amazon-cerebro-keyword-analysis` 保持完全一致，避免 V3/V4.1 两份报告看到的数字不同。

**列名**：`蓝海度`（5 档定性，**不做分数**）

| 竞品数 | 蓝海度 | 含义 |
|---|---|---|
| ≥ 10,000 | **极激烈** | 极端红海，新手不要碰 |
| 5,000 – 10,000 | **激烈** | 严重红海，有差异化才能打 |
| 1,000 – 5,000 | **一般** | 供需平衡，需要明确差异化 |
| 500 – 1,000 | **温和** | 友好区间，白牌可进场 |
| **< 500** | **蓝海** | 真正的蓝海，竞品少 |

**颈霜 4115 词实测分布**：

| 蓝海度 | 词数 | 占比 |
|---|---:|---:|
| 蓝海 | 2456 | 59.7% |
| 温和 | 393 | 9.6% |
| 一般 | 804 | 19.5% |
| 激烈 | 244 | 5.9% |
| 极激烈 | 216 | 5.2% |
| 无数据 | 2 | 0.0% |

### 边界 corner case（保持 V3 行为）

- 竞品 = `None`（数据缺失）→ 判"无数据"
- 竞品 = 0 → 落到 `<500` 档 = 蓝海（自然合理）

### 历史尝试（已废弃，记录用）

2026-07-19 下午我曾用「竞品/搜索 比值」做 5 档定性版（偏冷/温和/中等/偏激烈/激烈），并用 `log10(搜索量/竞品数+1)*30` 做 0-100 分数。用户截图发现两个 bug：(1) 竞品=0 时硬判 0 分被错判"红海"；(2) 列名"竞争度/竞争状态"和 v3 的"蓝海度"不一致。**已废弃**——v4.1 现在直接沿用 v3 蓝海度 5 档。详见 Pitfall #10。

### ✅ V4.1 输出

| 维度 | 路径 |
|---|---|
| CSV 主文件（V3 风格，仅英文 tag） | `~/Documents/keyword-cosmo-attribute-{input_name}-v41.csv`（18 列）|
| CSV 中文版（标签+列名中文） | `~/Documents/keyword-cosmo-attribute-{input_name}-v41-zh.csv`（18 列）|
| Obsidian 报告 | `~/Documents/ObsidianVault/01_有道原貌/Ⅳ输出/知识星球/yyyy-mm-dd-v41-cosmo-attribute-{input_name}.md` |
| 双路径同步 | obsidian + `~/` 家目录 |

### V4.1 实战案例：B0H35TQ81F 颈霜（2026-07-19）

**TOP 黄金捡漏词（C/D 级流量 + 蓝海/温和）**：
- gold bond age renew crepe corrector body lotion（8626 搜索 / 138 竞品 = 蓝海）
- olavita tri-lift peptide complex cream（7551 搜索 / 135 竞品 = 蓝海）
- hyggear dermarestore balm for crepey skin（7271 搜索 / 72 竞品 = 蓝海）

**S/A 级流量词（看属性组合找 listing 灵感）**：
- lotion（215729 搜索 / 大量竞品 = 极激烈 / 红海）
- retinol（215718 搜索 / 竞品 ~7k = 激烈）
- neck wrinkle patches（48354 搜索 / 1000 竞品 = 激烈）

**5 档蓝海度分布**（沿用 V3 口径实测 4115 词）：
- 蓝海 (<500)：2456 词（59.7%）
- 温和 (500-1000)：393 词（9.6%）
- 一般 (1000-5000)：804 词（19.5%）
- 激烈 (5000-10000)：244 词（5.9%）
- 极激烈 (≥10000)：216 词（5.2%）

### V3 + V4 + V4.1 串联用法

```
V3 → 4 维度评估 → "哪些词值得打"  （蓝海度按 V3 口径）
V4 → 11 dim 属性 → "为什么值得打"  （纯属性，不含数值评估）
V4.1 → V4 属性 + 4 维数值（沿用 V3）→ 一站式

实操：
- 找 TOP 蓝海 → V4.1 蓝海档=蓝海词
- 找 ROI 最高 → V4.1 流量 C/D + 蓝海档=蓝海
- 找 Listing bullet 灵感 → V4.1 S/A 级流量词的属性组合
```

---

## 🌐 输出命名 + 中英混合风格约定（2026-07-19 bailing 拍板）

**用户偏好**：表头/属性标签中文 + 关键词/数据/品牌英文的**混合显示**风格，避免"全英文读不懂、全中文翻译失真"两个极端。

### 命名规则

| 输出类型 | 命名 |
|---|---|
| CSV 主文件（英文 tag） | `~/Documents/keyword-cosmo-attribute-{input_name}-v41.csv` |
| CSV 中文版（标签已译） | `~/Documents/keyword-cosmo-attribute-{input_name}-v41-zh.csv` |
| Obsidian 报告 | `~/Documents/ObsidianVault/01_有道原貌/Ⅳ输出/知识星球/yyyy-mm-dd-v41-cosmo-attribute-{input_name}.md` |
| Obsidian 双路径同步 | obsidian + `~/` 家目录（防"知识星球看不到"事故） |

### 中英混合规则

| 部分 | 翻译 | 理由 |
|---|---|---|
| **CSV 表头**（11 个 dim 列名）| ✅ 翻中文 | 例如 `INGREDIENT_FAMILY` → `成分家族` |
| **CSV 行内 tag**（111 个细分标签）| ✅ 翻中文 | 例如 `vitamin_a` → `维生素A/视黄醇`，`mask_patch` → `面膜贴` |
| **关键词 / Phrase / Keyword**（实际词条）| ❌ 保留英文 | 翻译会失真、不需要 |
| **搜索量 / 竞品数 / 数值** | ❌ 保留数字 | 无需翻译 |
| **品牌名 / 产品名** | ❌ 保留英文 | GoPure / Gold Bond 等都是品牌英文 |
| **报告内专业术语** | ✅ 翻中文 + 括号英文 | 例如 "面膜贴 (mask_patch)" "矿物质 (mineral)" |
| **报告标题 / 段永平判断** | ✅ 全中文 | 阅读体验 |

### 已落地翻译映射（颈霜品类 11 dim × 111 tag）

**DIM 表头**（11 个）：
- INGREDIENT_FAMILY → 成分家族
- PAIN_SPECIFIC → 痛点细分
- FORM_FAMILY → 产品形态
- AREA_FAMILY → 使用部位
- AUDIENCE_FAMILY → 目标人群
- MODIFIER_FAMILY → 修饰/价值主张
- BENEFIT_FAMILY → 功效
- PURCHASE_CONTEXT → 购买场景
- TEMPORAL → 季节事件
- ORIGIN → 产地文化
- GENERIC → 通用异常

**TAG 翻译样例**（完整 114 个 100% 覆盖 V4.1 CSV 实际出现的 76 个 tag，存在 `assets/tag-translations.json`）：
- vitamin_a → 维生素A/视黄醇
- crepe_texture → 皱皮/鸡皮纹理
- mask_patch → 面膜贴
- gua_sha_tool → 刮痧板
- mature_50plus → 50+熟龄
- korean_beauty → 韩系美妆
- professional_grade → 专业级/医疗级
- firming → 紧致提拉
- chest_decollete → 胸部/锁骨
- turkey_neck → 火鸡脖

### 脚本：自动翻译表头+行内 tag

```python
# 翻译表（部分，共 111 个）
TAG_TRANSLATE = {
    'INGREDIENT_FAMILY': '成分家族',
    'vitamin_a': '维生素A/视黄醇',
    'mask_patch': '面膜贴',
    # ... 完整版见 assets/tag-translations.json
}

# 用法：先输出原始 v41 CSV，再生成 v41-zh CSV（中英混合版）
def translate_csv(src, dst):
    df = pd.read_csv(src)
    df = df.rename(columns={k: TAG_TRANSLATE.get(k, k) for k in df.columns})
    for col in DIM_COLS:
        df[col] = df[col].apply(lambda s: '|'.join(TAG_TRANSLATE.get(t, t) for t in s.split('|')) if s != '-' else '-')
    df.to_csv(dst, index=False)
```

### 实战案例：B0H35TQ81F 颈霜中英混合输出

| 关键词（英文） | 搜索量 | 竞品 | 蓝海 | 属性组合（中文） |
|---|---:|---:|---:|---|
| retinol body lotion | 72360 | 578 | 63.0 | 维生素A/视黄醇 + 霜/凝胶 + 身体 |
| gold bond age renew crepe corrector body lotion | 8616 | 138 | 54.1 | 矿物质 + 皱皮/鸡皮纹理 + 霜/凝胶 + 身体 + 焕活新生 |
| korean neck firming cream | 954 | 200 | - | 韩系美妆 + 霜/凝胶 + 颈部 + 紧致提拉 + 韩国 |
| neck wrinkle patches | 48354 | 1000 | 50.8 | 皱纹 + 面膜贴 + 颈部 |

---

## 变更记录

| 日期 | 变更 |
|---|---|
| 2026-07-19 | **V4.1 V3 4 维度全集 + 准入难度 BUG 修复**：bailing 加 V3 完整 4 维度（相关性 + 流量 + 准入难度 + 蓝海度）。准入难度基于 ABA 转化份额。**BUG 修复**：早期把 ABA=0% 错判"友好"——bailing 截图指出后改 `aba is None OR aba == 0 → 无数据`。B0CGB215HR 8294 词已重跑确认 |
| 2026-07-19 | **V3 蓝海度口径统一**：bailing 指出 V4.1 的"竞争度/竞争状态"和 V3 的"蓝海度"不一致——改回 V3 原口径：列名=蓝海度 / 5 档定性（极激烈/激烈/一般/温和/蓝海）/ 仅看竞品数绝对值。和 V3 CSV 视觉保持一致 |
| 2026-07-19 | **Pitfall #9 CSV 错位修复**：43 行关键词含英文逗号导致 Excel 整行列错位（v41-zh.csv）。强制约束：所有 CSV 输出必须用 `csv.writer(quoting=QUOTE_MINIMAL)`，禁止手工拼字符串；跑完必跑 `verify_csv` 验证列数。**safe_csv.py 升级为跨 skill 共享工具（canonical 在 amazon-cerebro-keyword-analysis/scripts/）** |
| 2026-07-19 | **中英混合风格约定**：bailing 拍板——CSV 表头+tag 翻译中文、关键词/数据/品牌保留英文；新增命名规则 + 翻译映射 + 自动翻译脚本 |
| 2026-07-19 | **v4.1 全维度版**：bailing 新增需求，V4 增加搜索量/流量等级 S/A/B/C/D/竞品数/蓝海度 4 个数值维度；输出 CSV 18 列；保留 V4 纯属性定位不破坏 |
| 2026-07-19 | 初版创建，bailing 设计 11 个 dimension × 108 tag 的属性树，在 B0H35TQ81F 4115 词上验证 |
| 2026-07-19 | 修复触发词 bug：单词必须 word boundary（'men' 不命中 'women'）；'au' 不命中 'australian'，改 'australian made' |
| 2026-07-19 | v4 与 v3 (4 维度评估) 并行存在，不替代 |
| 2026-07-20 | **🤝 跨 skill 同步:V3 Pitfall #16 品牌词护城河 (B0CGB215HR 教训)**—— V3 新增 Step 0 品牌词预过滤 + "白牌别碰"报告章节,V4.1 必须同步加品牌词 override,否则同数据两份报告"推荐行动"列不一致,用户对照时立即发现。详见 `amazon-cerebro-keyword-analysis` SKILL.md Pitfall #16 + `references/2026-07-20-bailing-case-brand-moat.md` |
| 2026-07-19 | **🤝 跨 skill 口径协议**（H10 反查 skill 家族）：新加本节，固化 V3↔V4.1 之间的列名/阈值/边界 case 同步硬约束 + 5 步修改工作流 + 自检脚本。**未来 agent 改任何一边数值列时必须同步另一边** |

## 🤝 跨 skill 口径协议（H10 反查 skill 家族 · 2026-07-19）

**适用范围**：`amazon-cerebro-keyword-analysis`（V3）+ 本 skill（V4.1）共同构成的亚马逊 H10 反查分析家族。

### 协议条款（每条都是硬约束）

1. **列名同步**：4 个数值列名必须两边完全一致
   - `蓝海度` / `准入难度` / `相关性等级` / `流量等级` — **任何一边改了，另一边必须同步改**

2. **5 档名称同步**：档位名称两边必须完全一致
   - 蓝海度：`蓝海 / 温和 / 一般 / 激烈 / 极激烈`
   - 准入难度：`友好 / 一般 / 高 / 很高 / 极激烈 / 无数据`
   - 相关性等级：`高 / 中 / 弱 / 不相关 / 无数据`
   - 流量等级：`S / A / B / C / D`

3. **阈值同步**：每个 5 档的数值阈值两边必须完全一致
   - 例：蓝海度 `<500=蓝海 / 500-1000=温和 / 1000-5000=一般 / 5000-10000=激烈 / ≥10000=极激烈`
   - 准入难度 `>70%=极激烈 / 50-70%=很高 / 30-50%=高 / 15-30%=一般 / <15%=友好 / None 或 0=无数据`

4. **边界 case 同步**：所有边界判定逻辑两边必须完全一致
   - `comp=None → 蓝海度='无数据'`
   - `aba=None 或 aba=0 → 准入难度='无数据'`（**不要判"友好"！** — Pitfall #15 教训）
   - `comp_perf=None → 相关性等级='无数据'`
   - `vol=None → 流量等级='D'`

5. **修改工作流**（写新数值列或改阈值时）：
   - **Step 1**：在 V3 改（V3 是权威源）
   - **Step 2**：立即同步到本 skill 的 SKILL.md
   - **Step 3**：如果涉及资产文件（tag-translations.json / attribute-tree.json），同步更新
   - **Step 4**：跑两个 skill 的 smoke test，验证结果一致
   - **Step 5**：在两边 SKILL.md 的变更记录里都登记

6. **不允许漂移**：
   - ❌ 不要把"竞争度"（v4.1 自创）当成"蓝海度"（V3 权威）的同义词
   - ❌ 不要用"竞品/搜索比值"替换"竞品数绝对值"做蓝海度
   - ❌ 不要给本 skill 加 V3 没有的额外数值列（如"竞争度" / "搜索量分位"）—— 自创新列名必踩坑（详见 Pitfall #10/14）

### V4.1 专属约定（与 V3 不同的地方）

V4.1 在 V3 之上加了**属性矩阵**（11 dim × 108 tag），这部分是 V4.1 独有的。但**数值评估 4 列必须沿用 V3 口径**。

V4.1 输出 CSV 列数：
- **英文版 v41.csv**：18 列（11 dim + 4 数值 + 序号/关键词/原分类/搜索量）
- **中文版 v41-zh.csv**：18 列（同上，标签已译）

### 触发本协议的信号

未来 agent 在以下场景**必须先读本协议**再动手：
- 改 V3 的 4 维度阈值
- 改 V4.1 的数值列名
- 给两个 skill 任何一个加新数值列
- 跨 skill join CSV 时发现列名不一致
- bailing 截图指出"这个列对不上"

### 自检脚本（每次跑完 H10 反查都跑）

```python
import csv

def cross_skill_consistency_check(v3_csv: str, v41_csv: str):
    """验证 V3 和 V4.1 同一份数据的 4 维度结果完全一致"""
    with open(v3_csv) as f:
        v3 = {r['关键词']: r for r in csv.DictReader(f)}
    with open(v41_csv) as f:
        v41 = {r['关键词']: r for r in csv.DictReader(f)}

    common = set(v3) & set(v41)
    mismatches = []
    for kw in common:
        for col in ['蓝海度', '准入难度', '相关性等级', '流量等级']:
            if v3[kw].get(col) != v41[kw].get(col):
                mismatches.append((kw, col, v3[kw].get(col), v41[kw].get(col)))

    if mismatches:
        print(f"❌ V3 vs V4.1 不一致 {len(mismatches)} 项:")
        for kw, col, v3v, v41v in mismatches[:10]:
            print(f"   {kw}: {col} V3={v3v!r} V4.1={v41v!r}")
        return False
    print(f"✅ V3 vs V4.1 完全一致（{len(common)} 词 × 4 维度）")
    return True

# 用法：跑完两个 skill 后立即调用
cross_skill_consistency_check(
    '/Users/bailing/Documents/关键词分析-B0H35TQ81F.csv',
    '/Users/bailing/Documents/keyword-cosmo-attribute-B0H35TQ81F-v41.csv'
)
```
