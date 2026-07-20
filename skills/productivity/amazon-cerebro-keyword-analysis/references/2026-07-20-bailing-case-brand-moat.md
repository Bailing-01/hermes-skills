# 2026-07-20 Bailing 案例：B0CGB215HR 多 ASIN 综合反查 — 3 个方法论补充

## 背景

2026-07-20，bailing 跑 B0CGB215HR 的 V4.1 22 列全集梳理（8,294 词 / 多 ASIN 模式 B）。这次跑出 3 个**V3 / V4.1 现有方法论没覆盖的盲点**，必须沉淀到 skill 防止下次再踩。

## 产品定位

- 类目：颈霜（Neck Firming Cream），多 ASIN 综合反查（3 个竞品合表）
- 价格：中端（推断）
- **5K 套压海外仓场景**——决定了"清库存 > 拓词"的优先级

## 数据规模

- 源文件：`keyword-cosmo-attribute-B0CGB215HR-v41.csv`（V4.1 22 列）
- 行数：8,294 行
- 列数：23 列（V3 4 维 + V4.1 11 维 + 推荐行动）

---

## ⚠️ 新发现的 3 个盲点（必须沉到 SKILL.md 主文件）

### 盲点 1：品牌词被 V3 自动判"蓝海" — brand-as-blue-ocean 陷阱

**现象**：S/A 级头部词里出现：
- `dr melaxin` — vol=369,351 / comp=157 / ABA=45.2% → 自动判"蓝海"
- `cerave` — vol=151,215 / comp=438 / ABA=24.9% → 自动判"蓝海"

**为什么是陷阱**：这些词"竞品少"是因为**品牌护城河让别的卖家不想碰**，不是真蓝海。**白牌打这些词 = 给品牌方打广告**。

**V3 公式盲区**：现有公式只看 `comp < 500`，但**不区分"竞品少是因为没人打"和"竞品少是因为巨头独占"**。

**修复方法**（用户拍板）：在 V3 / V4.1 的 Step 3 之后增加一个**品牌词剔除步骤**：
1. 维护 `BRAND_LIBRARY`（美妆颈霜品类已有 62 个词：dr melaxin, strivectin, gopure, medicube, noor wonder, olavita, probioderm, topicrem, cerave, olay, neutrogena, ...）
2. 蓝海度判完后，**遍历所有"蓝海"档词**，凡是 token 命中 BRAND_LIBRARY 的 → **override 为"否定"**
3. 系统公式识别不了 → 必须人工加这一步

**沉淀位置**：`amazon-cerebro-keyword-analysis/SKILL.md` 的 "Pitfalls" 区新增"🚨 Pitfall #16: brand-as-blue-ocean"

---

### 盲点 2：主推池（V3 金标准 6 词）不够 5K 套清库存

**现象**：B0CGB215HR 跑出来的"主推池"（蓝海 + 友好 + 高相关 + C/D 流量）只有 6 词，月累计流量 ~5,933——按行业平均转化率算（~3%），**月单量约 178 单**，根本撑不起 5K 套清库存。

**V3 公式盲区**：V3 公式只看"是不是能打"，不看"打起来够不够"。**纯方法论驱动出的小主推池，对套压货品类是结构性不够**。

**修复方法**：在 V3 Step 4 后增加"商业可行性自检"：
1. 算出主推池 + 拓词池的**月累计搜索量**
2. 按"行业平均 2-3% 转化率"反推**理论月单量**
3. 如果理论月单量 < 清库存目标 / 清库存周期 → **报告里必须显式警示**，不能只看金标准
4. 建议改走**多 listing 矩阵**消化套压货，而不是单 ASIN 死磕

**沉淀位置**：`amazon-cerebro-keyword-analysis/SKILL.md` 的 "Pitfalls" 区新增"🚨 Pitfall #17: 主推池够不够商业目标"

---

### 盲点 3：listing 种子词 CSV 生成时表头列索引错位 bug

**现象**：跑完 `listing-种子词-B0CGB215HR-2026-07-20.csv` 后，stat 检查发现"命中维度数"列全部显示 `-`。**CSV 列数自检通过（19 列一致），但表头定义列名 + 数据行 column 索引错位 1 列**。

**根因**：手写 `data3.append([...])` 时，多填了一列 `ORIGIN`，但表头只数到 19 列时没把这一列算进表头里。**csv.writer(QUOTE_MINIMAL) 只保证列数一致，不保证列名-数据对应**。

**修复方法**：
1. 写完 CSV 后，**必须用 Python 重新 read_csv 验证列名-数据对应**（不是只验证列数）
2. 验证脚本模板：

```python
import csv
def verify_csv_columns(path, expected_header):
    """比 verify_csv_safe 多一步：验证列名 = 实际数据列"""
    with open(path) as f:
        rows = list(csv.reader(f))
    actual = rows[0]
    if actual != expected_header:
        print(f'❌ {path} 表头错位')
        print(f'   预期: {expected_header}')
        print(f'   实际: {actual}')
        return False
    return True
```

3. 或者**用一个 dict 写**，避免 index 错位：
```python
# ✅ 改用 dict + OrderedDict，列名-数据自动对齐
from collections import OrderedDict
def write_csv_dict(path, header, data_dicts):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=header, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for d in data_dicts:
            w.writerow({k: d.get(k, '-') for k in header})
```

**沉淀位置**：
- `amazon-keyword-cosmo-attribute-analysis/scripts/` 加 `verify_csv_columns.py`
- 两个 skill 的 SKILL.md 都加引用："⚠️ safe_csv.verify_csv_safe 只验列数，**列名-数据对应**必须额外跑 verify_csv_columns"

---

## 输出物

- 全量 CSV：`/Users/bailing/Documents/关键词梳理-B0CGB215HR-V3V4.1-2026-07-20.csv`（8294 行 × 23 列）
- 主推拓词池 CSV：`/Users/bailing/Documents/主推拓词池-B0CGB215HR-2026-07-20.csv`（7 词）
- listing 种子词 CSV：`/Users/bailing/Documents/listing-种子词-B0CGB215HR-2026-07-20.csv`（33 词）
- 报告：`/Users/bailing/Documents/ObsidianVault/01_有道原貌/Ⅳ输出/知识星球/2026-07-20-B0CGB215HR-V3V4.1-关键词梳理.md`（双路径同步到 `~/`）

## 关键数据快照

| 维度 | 值 |
|---|---|
| ABA 数据覆盖率 | 24.8%（2,055/8,294）|
| 主推池（V3 金标准） | 6 词，月累计 ~5,933 vol |
| 拓词池 | 1 词（neck firming cream）|
| 多维金矿（高相关+4+ dim）| 33 词 |
| 推荐行动"观察"占比 | 93.7%（7,768/8,294）|
| 主推池 vs 5K 套清仓目标 | 月单量 ~178 单，结构性不够 |

## 段永平 4 过滤结论

| 过滤器 | 判断 |
|---|---|
| 敢为天下后 | ✅ 大盘稳 |
| 差异化 | ⚠️ cream_gel 占 78%，靠 modifier+audience+ingredient 差异化 |
| 好生意 | ⚠️ 价格战激烈，套压货品类典型 |
| Stop Doing | ❌ 单 ASIN 主推池不够清库存 → 走多 listing 矩阵 |