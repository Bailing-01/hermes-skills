# Hermes Skills Collection by bailing

> **作者**：[bailing](https://github.com/Bailing-01) ｜ 公众号「Bailing跨境」
>
> 亚马逊官方讲师 · 第三方卖家 10 年 · 前 10 亿级卖家运营经理 · 美国 PMP 项目认证
>
> 开发过多款亚马逊相关课程，目前致力于用 AI 把亚马逊的所有工作流全部自动化。


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

**创建日期**：2026-06-24

---

## 关于作者

我是 bailing：亚马逊官方讲师，第三方卖家 10 年，前 10 亿级卖家运营经理，美国 PMP 项目认证，开发过多款亚马逊相关课程。目前致力于用 AI 把亚马逊的所有工作流全部自动化。

GitHub 放能直接用的 Skill，更多实战复盘先发公众号「Bailing跨境」；也可以直接加我微信，备注「GitHub」。

<table>
  <tr>
    <td align="center" width="50%">
      <strong>公众号｜Bailing跨境</strong><br><br>
      亚马逊实战复盘、踩坑与 AI 提效<br><br>
      <img src="./assets/oa-qr.jpg" width="200" alt="微信公众号 Bailing跨境 二维码">
    </td>
    <td align="center" width="50%">
      <strong>个人微信｜bailing</strong><br><br>
      同行交流、合作、Skill 共建<br><br>
      <img src="./assets/wechat-qr.jpg" width="200" alt="bailing 个人微信二维码">
    </td>
  </tr>
</table>
