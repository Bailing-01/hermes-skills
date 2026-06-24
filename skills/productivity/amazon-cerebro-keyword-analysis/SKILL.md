---
name: amazon-cerebro-keyword-analysis
description: Analyze Cerebro/Helium10 reverse-ASIN keyword reports for Amazon advertising training and operations. Use when user mentions Cerebro 报表, 关键词分析, 广告词分级, 反查关键词, keyword classification, SABC分级, 流量分层, 词根拆解, B0B8ZWHRL6, 颈霜, loafers, 广告培训案例. Produces CSV with 4-tier classification (S/A/B/C/D) + traffic-tier splits + CPR/competition scoring + root-word breakdown. Distilled from bailing's real client cases (B0DM6K8K12 neck cream, B0B8ZWHRL6 loafers).
---

# Amazon Cerebro 关键词分析 Skill

## 触发场景

当用户提到以下任何一项时加载此 skill：

- "Cerebro 报表"、"Helium10 反查"、"反查关键词"
- "关键词分析"、"广告词分级"、"SABC 分级"
- "词根拆解"、"流量分层"、"核心词/上位词/属性词"
- ASIN 号（B0B8ZWHRL6、B0DM6K8K12 等）
- 产品类目（loafers、颈霜、neck cream 等）
- "给学员讲案例"、"培训素材"

## 输入数据格式

**Cerebro 反查报表**（Helium10 导出），26 列：

| 列 | 含义 | 说明 |
|---|---|---|
| 关键词词组 | Keyword Phrase | 主键 |
| ABA 点击份额 | Amazon Click Share | % |
| ABA 转化份额 | Amazon Conversion Share | % |
| 关键词销量 | Search Volume | 月搜索量 |
| IQ 得分 | IQ Score | 综合竞争分 |
| 搜索量 | Exact Search Volume | 精确月搜 |
| 趋势 | Trend | 12 个月趋势 |
| PPC 建议价（低/最高/最低）| PPC Bid Suggestion | 出价区间 |
| 广告 ASIN 数 | Ad ASINs | 投广告的 ASIN 数 |
| 竞品数 | Competing Products | 自然结果竞品数 |
| CPR | Click Probability Ratio | 点击概率，Cerebro 核心指标 |
| 标题密度 | Title Density | 该词在标题中的密度 |
| 自然位 | Organic Rank | 自然排名 |
| 商品推广位 | Sponsored Product Rank | SP 广告位 |
| AC 位 | AC Rank |  |
| HR 位 | HR Rank |  |
| SBH 位 | SBH Rank |  |
| 品牌视频位 | SBV Rank |  |
| 亚马逊推荐位 | Amazon Recommended Rank |  |
| 广告排名 | Ad Rank |  |
| 自然排名 | Organic Rank |  |

## 5 步方法论

### Step 1：词根拆解

将每个关键词拆成 4 类词根：

```
核心词根（如 loafers/flat/shoes）：主词，决定产品类目归属
上位词根（如 womens/women）：修饰词，限定人群/性别
属性词根（如 slip on/comfortable/leather/black/dress）：差异化卖点
弱相关词根（如 brand 名、其他品类）：边界词
```

**实战技巧**：
- 找核心词：把所有"自然排名=1"的词筛出来，它们的词根就是你的核心词
- B0B8ZWHRL6 案例：loafer(1391) + flat(1161) + shoes(6075) → 核心词根
- B0DM6K8K12 颈霜案例：neck(181) + cream(243) + firming(120)

### Step 2：流量分层

| 分层 | 阈值（月搜索量） | 策略定位 |
|---|---|---|
| **大词** | ≥ 5000 | 主战场、首页必争 |
| **中词** | 1000-5000 | 防守 + 拓词 |
| **小词** | < 1000 | 长尾捡漏，精确匹配 |

### Step 3：4 级广告分级

```
S 级 [主推]  ：核心大词 + IQ 高 + 自然排名差（11-50）→ 精确匹配抢首页
A 级 [拓词]  ：中词 + 已有排名（11-30）→ 词组/广泛匹配防守
B 级 [捡漏]  ：长尾小词 + IQ 中 → 海量词 + 低价 CPC 测试
C 级 [否定]  ：竞品品牌 + 不相关品类 + 西语词 → 加入否定清单
D 级 [观察]  ：弱相关但量大 → 不投，但持续观察流量变化
```

### Step 4：CPR + 竞争度加权

Cerebro 的 CPR（Click Probability Ratio）是核心指标，必须分桶：

| CPR 区间 | 含义 | 行动 |
|---|---|---|
| < 8% | 低点击概率 | 流量小，可能不值得投 |
| 8-12% | 中等（80% 词落在这） | 稳态词群 |
| 12-26% | 较高 | 高价值词 |
| > 26% | 极高（15% 词） | 优先抢，但要小心品牌词 |

**竞争度等级**（用 ad_asins + comp_asins 综合判定）：

```
低竞争：ad_asins < 100 且 comp_asins < 50
中竞争：ad_asins 100-300
高竞争：ad_asins 300-500
红海：ad_asins > 500
```

**综合优先级得分公式**：

```
优先级得分 = IQ_norm * 0.4 + (CPR_norm * 0.3) + 竞争度加权 * 0.3
```

### Step 5：Top N 排序输出

- Top 30 主推词（按综合优先级）
- Top 50 否定词（高 CPR + 竞品品牌）
- Top 100 捡漏词（低竞争 + 中等 CPR）

## 输出格式

CSV 文件，UTF-8 编码，列结构（19 列）：

```
序号,关键词,核心词根,上位词,属性词,弱相关,搜索量,CPR%,竞争度,
广告ASIN数,竞品数,IQ得分,自然排名,广告排名,
推荐行动(精确/词组/广泛/否定/观察),
流量分级(大/中/小),
广告分级(S/A/B/C/D),
综合优先级,备注
```

## 关键阈值（基于 bailing 案例总结）

- **vol ≥ 5000** = 大词
- **1000 ≤ vol < 5000** = 中词
- **vol < 1000** = 小词
- **IQ ≥ 1000 且排名差（11-50）** = S 级
- **品牌词（vans/cole haan/whitin/allbirds/skechers）** = 即使 CPR 高也要打 C 级（不建议抢品牌词）
- **西语词（zapatos/zapatillas）** = C 级（用户目前不卖西语市场）
- **5K-10K 套压货品类**（如 B0DM6K8K12 颈霜）：priority 倒挂，C 级反而是机会词——这些是大词黑名单，没投过的也别投

## 实战案例（2026-06-24）

### 案例 1：B0DM6K8K12 颈霜

- 5K 套压海外仓，FDA 注，MSRP $25.99
- 4 级分级：D=863 / A=940 / B=7680 / C=687 / S=256
- 关键词词根：neck(181) + cream(243) + firming(120) + skin(80)
- 关键洞察：清仓优先级高于拓词，长尾低竞争词先跑

### 案例 2：B0B8ZWHRL6 女式 loafers/flats

- 10427 行 Cerebro 数据
- 4 级分级：S=256 / A=940 / B=7680 / C=687 / D=863
- 关键词词根：loafer(1391) + flat(1161) + shoes(6075)
- 属性词 Top 5：women(7283) + slip on(1327) + black(834) + dress(783) + wide(596)
- 关键竞品品牌：Skechers(180) + Clarks(144) + Naturalizer(57)
- Top 主推词：`loafers for women` vol=113607 rank=11 → 距离首页 1 名，必死磕

## 错误警示

- 不要把"Rufus→Alexa"和"Alexa+"（Echo 上的）混淆——是两回事
- 不要凭印象编造产品名/事实——培训讲错一个产品名会被学员抓出来
- CPR 数据格式：**直接是百分比数值**（8=8%，10=10%），不是 x100

## 输出文件路径约定

- 关键词分析表：`~/Documents/关键词分析-{ASIN}.csv`
- 关键词优先级表：`~/Documents/关键词优先级-{ASIN}.csv`
- Skill 位置：`~/.hermes/skills/productivity/amazon-cerebro-keyword-analysis/`
- 参考案例：`~/.hermes/skills/productivity/amazon-cerebro-keyword-analysis/references/`

## 相关 Skill

- `amazon-competitor-monitor`（productivity/）：竞品监控
- `amazon-product-selection`（productivity/）：选品分析
- `amazon-seller-training-deck`（productivity/）：培训 PPT 生成
- `amazon-training-content-prep`：亚马逊培训内容准备（更通用）
- `amazon-inventory-liquidation`：库存清仓策略

## Pitfall 教训（必须记住）

1. **Cerebro 报表要 Excel 读 `.xlsx`**——用 `openpyxl` 或 `pandas`，别用 csv 模块
2. **创建/编辑 Skill 的文件写入协议**——见 `software-development/hermes-agent-skill-authoring` skill 的 Common Pitfalls #2：`skill_manage(action='create')` 对 user-local skills 也不可靠，必须用 `write_file` 手动写