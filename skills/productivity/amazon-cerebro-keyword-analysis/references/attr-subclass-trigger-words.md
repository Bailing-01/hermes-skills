# 6 类属性词触发词库（完整版）

> **这份是 v3.1 完整版**，对应 SKILL.md Step 1.5 表格里的"部分"列表。这里给出 6 个子类每个的**完整触发词**，方便复制粘贴到代码里。

## 用法

```python
ATTR = {
    '成分': [/* 见 §1 */],
    '痛点': [/* 见 §2 */],
    '修饰': [/* 见 §3 */],
    '场景': [/* 见 §4 */],
    '人群': [/* 见 §5 */],
    '形态': [/* 见 §6 */],
}

def attrs(kw_norm):
    out = []
    for sub, words in ATTR.items():
        if any(x in kw_norm for x in words):
            out.append(sub)
    return out
```

> 顺序无所谓，但**子类优先级**保持跟 SKILL.md 一致：成分 → 痛点 → 修饰 → 场景 → 人群 → 形态。

## §1 成分 (ingredient) — 21 个

```
retinol, collagen, hyaluronic acid, bakuchiol, hibiscus, peptide, peptides,
niacinamide, gold, snail, vitamin c, centella asiatica, ceramide, hyaluronic,
glycolic acid, keratin, q10, coenzyme, vitamin e, salicylic acid, lactic acid
```

**覆盖的常见类别**：
- 抗衰：retinol, bakuchiol, peptide, q10, coenzyme
- 保湿：hyaluronic acid, glycerin (未列入，需另加)
- 美白：vitamin c, niacinamide, glycolic acid
- 修护：centella asiatica, ceramide, snail
- 紧致：collagen, peptide, gold

## §2 痛点 (pain) — 24 个

```
turkey neck, wrinkle, wrinkles, sag, sagging, firming, tightening,
lifting, lift, dark spot, fine line, crepe, crepey, double chin, jowl,
jowls, eye bag, eye bags, dryness, puffiness, redness, acne, blemish, scar
```

**痛点覆盖范围**：
- 老化：wrinkle, fine line, sag, crepey
- 局部：turkey neck, double chin, eye bag, jowl
- 色斑：dark spot, blemish
- 质地：dryness, puffiness, redness, acne

## §3 修饰 (modifier) — 27 个

```
korean, japanese, chinese, french, american, organic, natural, vegan,
clean, clinical, cruelty free, professional, instant, advanced, premium,
anti aging, anti-aging, age defying, overnight, daily, luxury, fragrance free,
hypoallergenic, dermatologist, paraben free, sulfate free, non-comedogenic
```

**来源/品质/效果三大类**：
- 来源：korean, japanese, french, american
- 品质：organic, natural, vegan, clean, clinical, hypoallergenic
- 效果：anti aging, instant, overnight, age defying, advanced

## §4 场景 (scene) — 18 个

```
body, face, neck, eye, under eye, undereye, chest, decollete, hand,
arm, leg, mommy, pregnancy, all over, multiple areas, after sun, sun
```

**部位 × 时段**：
- 部位：face, neck, eye, body, hand, chest
- 时段：morning, night, daily, overnight
- 特殊：mommy, pregnancy, all over, after sun

> 注意：**不要把 body/face/eye 放 ROOT 库**（这是 v3 之前的常见错误）。它们是 ATTR 场景子类。

## §5 人群 (people) — 17 个

```
women, men, mature, 50+, 60+, sensitive, oily, dry, combination,
over 50, over 60, men's, womens, teens, adult, seniors, baby
```

**性别 × 年龄 × 肤质**：
- 性别：women, men, men's, womens
- 年龄：mature, 50+, 60+, over 50, over 60, teens, seniors
- 肤质：sensitive, oily, dry, combination

## §6 形态 (form) — 23 个

```
stick, patch, patches, roll-on, tape, gua sha, kit, set, tubing,
waterproof, mini, travel, softgel, jar, tube, pump, dropper,
spf, sunscreen, applicator, wand, pen
```

**产品形态**：
- 涂抹类：stick, roll-on, patch, tape, applicator
- 套装：kit, set, mini, travel
- 容器：jar, tube, pump, dropper, softgel
- 工具：gua sha, wand, pen

## 维护说明

- **新增词**：直接编辑对应章节，**别破坏格式**（保持一个 trigger word 一行的缩进）
- **删除词**：谨慎 —— 删错的词会让已分类的 Cerebro 数据**重新落到 OTHER 桶**
- **改名/合词**：触发词 = 字符串子串匹配，**空格敏感**。`anti aging` 和 `anti-aging` 是两个不同 trigger
- **跨子类重叠**：故意保留（如 `gold` 既在成分又在修饰下），因为同样的词在不同语境下可能归属不同子类

## 验证方法

```python
# 跑一个测试用例
test_cases = [
    ('korean retinol neck cream', ['成分', '修饰', '场景']),  # 期望命中
    ('anti aging wrinkle cream', ['痛点', '修饰', '成分']),  # 期望命中
    ('tubing mascara', ['形态']),                            # 单命中
    ('crema antiarrugas para mujer', ['痛点', '人群']),      # 跨语言
]
for kw, expected in test_cases:
    actual = attrs(kw.lower())
    if set(actual) == set(expected):
        print(f"✓ {kw}: {actual}")
    else:
        print(f"✗ {kw}: expected {expected}, got {actual}")
```
