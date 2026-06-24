# Hermes Skills Collection by bailing

这是我 (bailing) 在 Hermes Agent 中使用的自定义 Skill 集合。

每个 Skill 都来自真实业务场景的实战沉淀，包含完整的 5 步方法论、阈值参数、实战案例和 Pitfall 教训。

## Skill 列表

| Skill | 类别 | 用途 | 案例 |
|---|---|---|---|
| [amazon-cerebro-keyword-analysis](./skills/productivity/amazon-cerebro-keyword-analysis/) | productivity | Helium10 Cerebro 反查关键词分析 | B0B8ZWHRL6 女式 loafers, B0DM6K8K13 颈霜 |

## 安装方法

### 单个 Skill 安装

```bash
# 克隆整个仓库
git clone https://github.com/bailing/hermes-skills.git

# 复制需要的 Skill 到你的 Hermes skills 目录
cp -r hermes-skills/skills/productivity/amazon-cerebro-keyword-analysis/ \
      ~/.hermes/skills/productivity/

# 重启 Hermes 或运行 hermes skills reload
hermes skills list | grep amazon-cerebro-keyword-analysis
```

### 批量安装（所有 Skill）

```bash
git clone https://github.com/bailing/hermes-skills.git
cp -r hermes-skills/skills/* ~/.hermes/skills/
hermes skills list
```

## 贡献

如果你也是亚马逊卖家/讲师，发现 Skill 有可改进的地方：
1. Fork 这个仓库
2. 修改对应的 SKILL.md
3. 提交 PR

## 许可证

MIT

---

**作者**：bailing（亚马逊官方讲师 + 第三方卖家）
**创建日期**：2026-06-24
