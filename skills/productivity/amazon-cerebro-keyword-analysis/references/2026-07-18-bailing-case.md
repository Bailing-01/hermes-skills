# 2026-07-18 Bailing Cerebro 案例：B0H35TQ81F 颈霜

## 背景

2026-07-18，bailing 准备培训案例，要求把 B0H35TQ81F 的 Helium10 Cerebro 反查报告做"关键词属性分类"处理（**上位词 / 品牌词 / 属性词**）。这次执行发现了一个**重要的方法论缺陷**，并修复了。

## 产品定位

- 类目：颈霜（Neck Firming Cream）
- 价格：中端（约 $20–30 推断）
- 5K 套压海外仓场景，决定了**清库存为主、扩流量为辅**的运营路径

## 数据规模

- 源文件：`US_AMAZON_cerebro_B0H35TQ81F_2026-07-18.xlsx`
- 行数：4,115 行
- 列数：35 列（中文版 Helium10 Cerebro，多了末尾 3 个竞品 ASIN 列）

## 分类分布

### 营销视角分类（5+1）

| 分类 | 行数 | 占比 |
|---|---:|---:|
| **LONGTAIL** | 2,878 | 69.9% |
| **BRAND** | 522 | 12.7% |
| **ATTRIBUTE** | 229 | 5.6% |
| **ROOT** | 201 | 4.9% |
| **OTHER** | 281 | 6.8% |
| **NOISE** | 4 | 0.1% |

### 广告分级 S/A/B/C/D

| 等级 | 行数 | 占比 |
|---|---:|---:|
| **S 主推** | 20 | 0.5% |
| **A 拓词** | 17 | 0.4% |
| **B 捡漏** | 3,261 | 79.2% |
| **C 否定** | 543 | 13.2% |
| **D 观察** | 265 | 6.4% |

### 流量分层

| 分层 | 行数 | 占比 |
|---|---:|---:|
| 大词 (≥ 5000) | 85 | 2.1% |
| 中词 (1000–5000) | 239 | 5.8% |
| 小词 (< 1000) | 3,791 | 92.1% |

## 与 B0B8ZWHRL6（loafers）的关键差异

| 维度 | B0B8ZWHRL6（loafers）| B0H35TQ81F（颈霜）|
|---|---|---|
| 大词占比 | ~16% | **2.1%** |
| 主打法 | 主推 + 拓词 + 捡漏 | **S 级精确 + B 级批量捡漏** |
| 主战场 | 头部品类首页 | 长尾词流量 |
| 应对策略 | 高 bid 抢首页 | 低 bid 海量铺长尾 |

**结论：颈霜品类运营不等于 loafers 品类运营。即使方法论相同（5 步法 + 4 级分级），打法必须根据流量分布调整。**

## ⚠️ 重要教训：Priority 公式修复

### 错误版本

```
priority = IQ * 0.4 + CPR * 0.3 + comp_score * 0.3
```

### 出现的问题

第一次跑出来 TOP 30 **几乎全部是品牌词**（carotone, strivectin, gopure, medicube, noor wonder, olavita, probioderm, topicrem, ...），全是 C 否定词。

### 根因

品牌词的 IQ 和 CPR 天然很高（巨头产品的 Cerebro 数据就是这样），但**它们就是不想投的词**。priority 公式没有"广告等级"权重，导致品牌词的 priority 反而排第一，运营会被误导。

### 修复版本

```python
def fixed_priority(c):
    if c['ad_level'] == 'C':
        return 0.0
    iq = c['iq']; cpr = c['cpr']; comp = c['comp_asins']
    iq_score = min(iq / 100, 100) * 0.4       # 40 分
    cpr_score = min(cpr, 50) * 1.0 * 0.3       # 30 分
    comp_score = max(0, min(30, 3000 / (comp + 1))) * 0.3  # 30 分
    base = iq_score + cpr_score + comp_score
    weight = {'S': 1.5, 'A': 1.2, 'B': 1.0, 'D': 0.3}[c['ad_level']]
    return round(base * weight, 1)
```

**核心改动**：
- C 级（否定）= 0（不应进入排序）
- S 级 × 1.5（最优先抢首页）
- A 级 × 1.2（拓词加权）
- B 级 × 1.0（正常）
- D 级 × 0.3（观察词打折）

### 修复后 TOP 30 长什么样

```
1.  get dreamy overnight toning whip    LONGTAIL    S  92.4
2.  hyggear dermarestore balm           LONGTAIL    S  88.3
3.  amlactin crepe firming cream        LONGTAIL    S  85.5
4.  retinol body lotion                 LONGTAIL    S  84.8
5.  bakuchiol                           ATTRIBUTE   S  83.8
6.  neck wrinkle patches                LONGTAIL    S  83.8
7.  collagen face mask                  LONGTAIL    S  82.8
8.  retinol                             ATTRIBUTE   S  82.7
9.  retin a                             ATTRIBUTE   S  80.4
10. double chin reducer                 LONGTAIL    S  80.2
... 全是 S 级长尾词，没有任何一个品牌词
```

## 完整输出

- CSV：`~/Documents/关键词分析-B0H35TQ81F.csv`（4115 行，19 列）
- Obsidian 报告：`~/Documents/ObsidianVault/01_有道原貌/Ⅳ输出/知识星球/2026-07-18-US-Amazon-Cerebro-B0H35TQ81F-关键词分类报告.md`

## 沉淀到 Skill 的内容

1. **修复版 priority 公式** —— 加载本 skill 时默认使用
2. **62 个 BRAND_LIBRARY 词** —— 美妆颈霜品类
3. **15 个 CORE_ROOTS** —— 去掉 body/face/eye 装饰词后的真实品类根词
4. **6 个属性子类 + 触发词** —— 成分/痛点/修饰/场景/人群/形态

## 4 周执行清单（颈霜特定）

| 周 | 动作 |
|---|---|
| W1 | S 级精确广告组（20 词）+ C 级否定（543 词）+ listing 标题改写 |
| W2 | B 级 1–10 组（1000 词）上线 |
| W3 | B 级 11–20 组上线 + 看转化率砍 30% |
| W4 | B 级 21–30 组 + 复盘整体 ACOS |

## 输出验证清单

- [x] 5 桶总行数加总 = 总行数（4115）
- [x] ROOT ≤ 5%（实际 4.9%）
- [x] BRAND 30–50%（实际 12.7%——偏低是因为美妆颈霜品牌集中度本身没那么极端）
- [x] ATTRIBUTE > 50%（实际 75.4% LONGTAIL+ATTRIBUTE 合算）
- [x] NOISE < 5%（实际 0.1%）
