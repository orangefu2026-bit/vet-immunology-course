# 《兽医免疫学》网络课程 · 教学比赛资源站

面向高校青年教师教学竞赛（青教赛）的章节化网络教学资源。第一章《抗原》为**样板章**，整站结构、视觉、互动与评价体系即“统一标准”，后续章节按同一模板扩展。

## 目录结构

```
vet-immuno-course/
├── index.html                # 课程门户（章节目录/学习闭环说明）
├── chapter01/                # 第一章 抗原（每章一个独立目录 + 独立二维码）
│   ├── index.html            # 章节首页（目标/重难点/路径/进度）
│   ├── pre.html              # 课前学习（任务/启发问题/旧知回顾/前测）
│   ├── m1..m4.html           # 知识模块（概念与特性 / 表位与特异性 / 微生物抗原 / 毒素与基因工程抗原）
│   ├── case.html             # 案例工坊（狂犬病 / 类毒素·血清疗法 / PEDV·TGEV VLP）
│   ├── quiz.html             # 在线自测（14 题即时反馈）
│   ├── homework.html         # 课后分层作业（基础/提升/拓展）
│   ├── eval.html             # 学习评价（百分制构成 + 量表 + 反馈）
│   ├── frontier.html         # 课程思政（4 点）与学科前沿（4 项，均注来源）
│   ├── teacher.html          # 教师文档：20 分钟教学设计 + 板书 + 评分映射 + 评委自评
│   ├── script.html           # 20 分钟逐字讲课稿
│   └── qrcode.html           # 扫码学习页（二维码 + 备用地址）
├── assets/css/style.css      # 统一视觉系统
├── assets/js/main.js         # 交互引擎（测验/进度/打卡/表单，无外部依赖）
└── assets/qr/                # 各章二维码 PNG（高清，部署后生成）
```

## 构建方式（改动后必读）

成品页面由 `_src/` 源生成（共享导航/页脚/上一页下一页由模板统一维护）：

```bash
python _src/build.py          # 重新生成全部页面到仓库根
```

- 改共享壳：`_src/templates/ch_shell.html`、`portal_shell.html`
- 改页面正文：`_src/pages/chapter01/*.html`（首行 `<!-- meta: title=…; desc=… -->` 生效）
- 增/删页面、改导航顺序：编辑 `_src/config.json` 的 `ch1pages`
- 部署地址：写入 `_src/config.json` 的 `deploy.ch1 / deploy.portal` 后重建，`qrcode.html` 自动显示真实备用地址

## 新增章节（第 2 章起按此复制）

1. `_src/config.json`：把该章从 `"status": "upcoming"` 改为 `"live"`；
2. 复制 `_src/pages/chapter01/` 为 `chapterXX/`，逐页替换内容（视觉与结构不变）；
3. 将本章课件放在 `_src/` 同级原始目录，用 `python _work/extract_ch1.py` 的思路提取文本 → 按蓝本模式重构（模块/案例/题库/作业/评价/思政/前沿各自独立设计）；
4. `python _src/build.py` 重建；门户首页自动生成新章卡片；
5. 部署后写入该章公网 URL → 生成独立二维码 → 放入 `assets/qr/chapterXX-qr.png` → 更新该章 `qrcode.html`。

## 内容纪律

- 科学内容忠于课件原文，不擅自改动概念；
- 扩充内容（前沿/案例/思政）均注明来源，禁止虚构文献、病例与数据；
- 若课件与其他资料冲突，先标注冲突、交由任课教师确认，不自行猜测。

## 部署与二维码（交付要求）

网站为纯静态、无构建依赖、无外部 CDN/字体请求，可直接托管于 GitHub Pages / 任意静态主机。

二维码 = 真实公网 URL 编码的标准 QR Code（≥1000×1000 PNG），禁止 localhost/本机路径。
流程：**部署 → 取得 https 公网 URL → 生成 QR → 扫码解码验证 → 交付**。
各章二维码互不相同、各自直达本章页面。
