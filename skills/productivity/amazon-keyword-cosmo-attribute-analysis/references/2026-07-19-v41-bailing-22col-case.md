# V4.1 22 列全集 · 颈霜 B0H35TQ81F 实战案例（2026-07-19）

**完整 session 记录**：从用户要求"加 V4 的搜索量/流量/竞品数/蓝海度"开始 → 中间踩了 4 个真实坑 → 最终交付 22 列 CSV + 3 份 Obsidian 报告。

---

## 输入

- **SKU**：B0H35TQ81F（颈霜）
- **xlsx 路径**：`~/Library/Application Support/ziniaobrowserdatas/ziniao browser/【转让】本土号/US_AMAZON_cerebro_B0H35TQ81F_2026-07-18.xlsx`
- **xlsx 列数**：35 列（H10 Cerebro 模式 A，单 ASIN 反查）
- **词数**：4115 词
- **核心列定位**：
  - 列 6：`搜索量`
  - 列 12：`竞品数`
  - 列 3：`ABA总计 转化份额`（准入难度原始数据）
  - 列 32：`竞品表现得分`（相关性原始数据）

## 输出（22 列）

```
1-3. 序号 / 关键词 / 原分类(v3)
4-14. 11 维属性（V4 全套，详见 assets/tag-translations.json）
15. 搜索量
16. 流量等级（S/A/B/C/D）
17. 竞品数
18. 蓝海度（V3 口径：<500=蓝海 / 500-1k=温和 / 1k-5k=一般 / 5k-10k=激烈 / ≥10k=极激烈）
19. ABA转化份额(%)
20. 准入难度（友好<15% / 一般15-30% / 高30-50% / 很高50-70% / 极激烈>70% / 无数据）
21. 竞品表现得分
22. 相关性等级（高/中/弱/不相关）
```

---

## Session 中踩的 4 个真实坑

### 坑 #1：CSV 含逗号导致整行列错位（最早版本）
- **症状**：用户截图里"搜索量 0 / 竞品 0 / 蓝海度 0.0 / 红海"列错位
- **根因**：写中文版 CSV 时用了 `f.write(','.join(row))` 手工拼字符串，含英文逗号的关键词（如 `anua collagen retinol refining gua sha cream, neck cream for lifting & firming`）被错误拆成 3 列
- **影响**：43 行错位
- **修复**：`csv.writer(quoting=csv.QUOTE_MINIMAL)` 自动加引号包裹
- **沉淀**：SKILL.md Pitfall #9 + `scripts/safe_csv.py` 工具（canonical 在 v3，V4.1 引用）

### 坑 #2：自创「竞品/搜索 比值」5 档取代 V3 蓝海度（口径漂移）
- **症状**：用户原话"第一个竞品=0 怎么还是红海？" + "先去看一下我们 V3 版本是怎么去通过竞品，然后判断蓝海程度的"
- **根因**：V4.1 自创 `log10(搜索量/竞品数+1)*30` 公式 + 列名"竞争度/竞争状态"——和 V3 已有定义漂移
- **影响**：竞品=0 被错判红海；列名不一致让用户做 mental mapping
- **修复**：删除 V4.1 自创公式 + 列名改回 V3 原口径（蓝海/温和/一般/激烈/极激烈）
- **沉淀**：SKILL.md Pitfall #10 + 「v4.1 必须沿用 v3 口径」硬约束

### 坑 #3：准入难度把 ABA=0 错判"友好"
- **症状**：用户红框圈出"序号 172 best neck and chest cream / ABA=0 / 准入难度=友好"
- **根因**：原代码 `if conv < 15: return '友好'` 把 `conv=0` 也归到友好档
- **影响**：75% 的词被错标"友好"（实际是 Cerebro 没数据）
- **修复**：`if conv is None or conv == 0: return '无数据'`
- **沉淀**：兄弟 skill V3 同步加同样修复（SKILL.md Pitfall #15 / V4.1 表格"无数据=缺失或=0"列）

### 坑 #4：B0CGB215HR 是另一个 SKU（8294 词）不是 B0H35TQ81F
- **症状**：用户截图红框样本在 B0H35TQ81F 的 CSV 里找不到
- **根因**：用户跑过两个 SKU，B0CGB215HR 是更早的 8294 词报表，xlsx 在 `~/Library/Application Support/ziniaobrowserdatas/ziniao browser/GPT5/` 目录
- **修复**：重跑 B0CGB215HR V4.1（8294 词）作为第二份 CSV
- **沉淀**：未来跑 V4.1 之前应该先问用户"用哪个 SKU 的 xlsx"，或自动扫描所有 xlsx 路径

---

## 实测 4 维度分布

### 蓝海度（V3 口径）
- 蓝海 (<500)：2456 词（59.7%）
- 温和 (500-1000)：393 词（9.6%）
- 一般 (1000-5000)：804 词（19.5%）
- 激烈 (5000-10000)：244 词（5.9%）
- 极激烈 (≥10000)：216 词（5.2%）

### 准入难度
- 友好 (<15%)：37 词（0.9%）
- 一般 (15-30%)：183 词（4.4%）
- 高 (30-50%)：240 词（5.8%）
- 很高 (50-70%)：187 词（4.5%）
- 极激烈 (>70%)：253 词（6.1%）
- 无数据 (缺失或=0)：3215 词（78.1%）

### B0CGB215HR（8294 词，对比）
- 准入难度无数据：6239 词（75.2%）— 75-78% 是 Cerebro 不覆盖的词
- 友好/一般/高/很高/极激烈 各档占比和 B0H35TQ81F 类似

### 流量等级
- S ≥50k：12 词（0.3%）
- A 10k-50k：35 词（0.9%）
- B 5k-10k：95 词（2.3%）
- C 1k-5k：638 词（15.5%）
- D <1k：3335 词（81.0%）

---

## V3 推荐行动公式（4 维度反推）

```python
def recommend_action(traffic_lv, relevance_lv, entry_lv, blue_lv):
    if relevance_lv == '不相关': return '观察'
    if entry_lv == '极激烈' or blue_lv == '极激烈': return '否定'
    if blue_lv == '蓝海' and entry_lv in ('友好', '一般') and relevance_lv == '高':
        return '捡漏(优先)'
    if blue_lv in ('温和', '蓝海') and entry_lv in ('友好', '一般'):
        return '主推'
    if blue_lv == '一般' and relevance_lv == '高' and traffic_lv in ('S', 'A'):
        return '拓词(中后期)'
    if blue_lv == '一般' and entry_lv in ('一般', '高'):
        return '防守'
    if blue_lv in ('激烈', '极激烈'): return '观察'
    return '观察'
```

**金标准捡漏候选**（蓝海 + 友好准入 + 高相关 + C/D 级流量）= 新品 0-2 周能打：

| 关键词 | 搜索量 | 竞品 | ABA份额 | 准入 | 相关 | 蓝海 |
|---|---:|---:|---:|---:|---:|---|
| neck | 3259 | 1000 | 14.3% | 友好 | 高 | 一般 |
| skin care | 182695 | 100000 | 12.2% | 友好 | 高 | 激烈 |

（实际 TOP 15 在 8294 词中搜索后筛选得到——本案例没保留具体清单，仅给出公式参考）

---

## 输出文件清单

| 文件 | 路径 |
|---|---|
| 英文版 CSV | `~/Documents/keyword-cosmo-attribute-B0H35TQ81F-v41.csv` |
| 中文版 CSV | `~/Documents/keyword-cosmo-attribute-B0H35TQ81F-v41-zh.csv` |
| 第二 SKU CSV（8294 词） | `~/Documents/keyword-cosmo-attribute-B0CGB215HR-v41.csv` + `-zh.csv` |
| 完整分析报告（Obsidian） | `~/Documents/ObsidianVault/01_有道原貌/Ⅳ输出/知识星球/2026-07-19-v41-cosmo-attribute-颈霜4115词全维度分析.md` |
| 决策速查表 | `~/Documents/ObsidianVault/01_有道原貌/Ⅳ输出/知识星球/2026-07-19-v41-颈霜决策速查表.md` |
| 策略汇总（9K 字） | `~/Documents/ObsidianVault/01_有道原貌/Ⅳ输出/知识星球/2026-07-19-v41-颈霜市场细分+段永平式产品策略汇总.md` |
| 全部双路径同步到 ~/ 家目录 | `~/2026-07-19-*.md` 3 份 |

---

## 关键经验（下次跑 V4.1 必看）

1. **跑 V4.1 之前先 skill_view('amazon-cerebro-keyword-analysis')**——确保数值列沿用 V3 口径，绝不自创
2. **CSV 写完必跑 verify_csv_safe()**——43 行错位 bug 的预防药
3. **准入难度必有"无数据"档**——ABA=0 不能判友好
4. **中英混合显示风格**——表头+tag 中文，关键词/数据/品牌英文
5. **段永平式产品策略**（用户主线）：niche 形态创新 + K-beauty 包装 + 跨部位延伸，避开 cream 主推红海

---

## 教训：bailing 的"截图即诊断"工作流

这次 session 有个明显特征：用户**用截图直接指出 bug**，原话往往很短：

- "为什么你这里有很多列它不是对齐的？" → 触发 CSV 错位排查
- "那你这个红海度是什么意思啊？我昨天给你的是竞争激烈温和这几个状态。第一个竞品为0，怎么还是红海？" → 触发蓝海度口径修复
- "这个V4的版本还是需要把V3里面关于这个ABA的垄断放进来" → 触发准入难度新增
- "需要" → 触发 V3/V4.1 双 skill 同步
- "V3版本的表格需要更新，这种没有数据的叫无数据就好了" → 触发准入难度边界 case 修复

**Lesson**：每次看到用户发截图 + 简短提问，**默认就是发现了 bug**。第一动作是去验证 CSV/报告的具体行，不要默认"我写的没错"。

下次跑 V4.1 / V3 看见数字异常，立刻问：
1. 这行的源数据是什么？
2. 是不是边界 case 没处理（None / 0 / 缺失 / 拼写错误）？
3. 是不是列名口径和兄弟 skill 不一致？
