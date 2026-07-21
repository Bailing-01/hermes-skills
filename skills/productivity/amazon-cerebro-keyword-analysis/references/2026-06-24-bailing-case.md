# 2026-06-24 bailing Cerebro 实战记录

## 背景

bailing 是亚马逊官方讲师 ，同时也是亚马逊第三方卖家 。6 月 24 日他正在准备第二天的培训（给知无不言论坛小伙伴），需要：

1. 把上一期（5月13-14日）广告全链路课程做更新
2. 给学员补充最新的实操案例
3. 用 B0B8ZWHRL6 的 Cerebro 报表作为培训讲义的真实案例

## 案例：ASIN B0B8ZWHRL6（女式 loafers/flats）

### 产品定位
- 类目：Women's Loafers & Flats
- 价格定位：中端（推断 $30-50）
- 核心词根：loafer(1391) + flat(1161) + shoes(6075)

### 数据规模
- 源文件：`US_AMAZON_cerebro_B0B8ZWHRL6_2026-05-15.xlsx`
- 行数：10427 行
- 列数：26 列（标准 Cerebro 导出）

### 4 级分级结果

| 等级 | 数量 | 占比 | 含义 |
|---|---|---|---|
| **S 主推** | 256 | 2.5% | 精确大词，排名差，必死磕首页 |
| **A 拓词/防守** | 940 | 9.0% | 中词，已有排名 11-30 |
| **B 捡漏** | 7680 | 73.7% | 长尾小词金矿 |
| **C 否定** | 687 | 6.6% | 竞品品牌 + 西语词 |
| **D 观察** | 863 | 8.3% | 弱相关大词 |

### Top 3 主推词

1. `loafers for women` vol=113607 rank=11 → **距离首页 1 名，必死磕**
2. `womens loafers` vol=50692 rank=19 → 距离首页 9 名
3. `womens flats` vol=85531 rank=293 → 大词但无排名，主战场

### CPR 分布（关键发现）

- **80.8% 的词 CPR 是 8-12%（中等水平）**——稳态词群
- **15.2% CPR >26%**——高价值机会词
- **0% CPR <8%**——数据分布偏右

### 核心卖点词根（listing 必须强化）

- women (7283) + slip on (1327) + comfortable (387) + leather (272) + wide (596)

### 关键竞品品牌

- Skechers(180) + Clarks(144) + Naturalizer(57)
- 即使 CPR 高，品牌词也不建议投（打 C 级）

### 西语市场

- zapatos para mujer (110264, 西语) → C 级否定
- 用户目前不卖西语市场

### 综合优先级 Top 5

```
1. allbirds womens shoes          CPR=41%  vol=14383  IQ=113252  ⭐ TOP1
2. vivaia shoes for women         CPR=85%  vol=50692  IQ=192851
3. kizik womens shoes             CPR=53%  vol=24099  IQ=95125
4. adidas ballet flats for women  CPR=41%  vol=14383  IQ=27554
5. black hey dudes womens         CPR=33%  vol=7239   IQ=7239
```

## 培训讲稿建议（基于此案例）

1. **开场**：展示真实 Cerebro 数据 → 学员立刻知道"这不是 PPT 演示"
2. **方法论**：5 步法（词根拆解 → 流量分层 → 4 级分级 → CPR/竞争度 → Top N）
3. **核心展示**：Top 30 排序，让学员看到数据驱动的优先级
4. **避坑提示**：品牌词陷阱、西语词陷阱、CPR 数据格式
5. **结尾**：建议学员自己也跑一次 B0B8ZWHRL6，对比自己的结果

## 输出文件

- `/Users/bailing/Documents/关键词分析-B0B8ZWHRL6.csv` (1.4 MB, 10426 行, 19 列)
- `/Users/bailing/Documents/关键词优先级-B0B8ZWHRL6.csv` (1.4 MB, 20 列，CPR/竞争度加权)

## 教训（沉淀到 Skill）

1. `skill_manage` 工具 create action **不可靠**——必须用 `write_file` 手动写文件
2. Hermes skill 必须在 `~/.hermes/skills/{category}/` 下，不能直接放 `~/.hermes/skills/`
3. `hermes skills list` 显示的不一定真实存在，必须用 `find` 命令验证
