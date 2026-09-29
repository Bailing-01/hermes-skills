# amazon-keyword-cosmo-attribute-analysis

> **作者**：[bailing](https://github.com/Bailing-01) ｜ 公众号「Bailing跨境」
>
> 亚马逊官方讲师 · 第三方卖家 10 年 · 前 10 亿级卖家运营经理 · 美国 PMP 项目认证
>
> 开发过多款亚马逊相关课程，目前致力于用 AI 把亚马逊的所有工作流全部自动化。

## 这个 Skill 做什么

对 H10 反查报表（Cerebro / Magnet / BlackBox 输出）做 Cosmo-aware 多维属性词分析。  
不做分类、不给推荐动作，专门把每个词拆成「主词-属性-人群场景」的细颗粒度；与 amazon-cerebro-keyword-analysis（v3）是兄弟 Skill，补 v3 没细化的属性深度。

## 怎么用

触发词：cosmo 分析、多维属性词、Cosmo-aware、成分党意图、人群标签、属性词树、属性词 vs 上位词

安装：把本文件夹复制到你的 Agent skills 目录即可（完整说明见 `SKILL.md`）。

```bash
git clone https://github.com/Bailing-01/hermes-skills.git
cp -r hermes-skills/skills/productivity/amazon-keyword-cosmo-attribute-analysis/ ~/.hermes/skills/productivity/
hermes skills list | grep amazon-keyword-cosmo-attribute-analysis
```

---

## 关于作者

我是 bailing：亚马逊官方讲师，第三方卖家 10 年，前 10 亿级卖家运营经理，美国 PMP 项目认证，开发过多款亚马逊相关课程。目前致力于用 AI 把亚马逊的所有工作流全部自动化。

GitHub 放能直接用的 Skill，更多实战复盘先发公众号「Bailing跨境」；也可以直接加我微信，备注「GitHub」。

<table>
  <tr>
    <td align="center" width="50%">
      <strong>公众号｜Bailing跨境</strong><br><br>
      亚马逊实战复盘、踩坑与 AI 提效<br><br>
      <img src="../../../assets/oa-qr.jpg" width="200" alt="微信公众号 Bailing跨境 二维码">
    </td>
    <td align="center" width="50%">
      <strong>个人微信｜bailing</strong><br><br>
      同行交流、合作、Skill 共建<br><br>
      <img src="../../../assets/wechat-qr.jpg" width="200" alt="bailing 个人微信二维码">
    </td>
  </tr>
</table>
