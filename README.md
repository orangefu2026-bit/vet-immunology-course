# 《兽医免疫学》网络课程

以教学课件为内容依据、面向**学生在线学习**的章节化网络教学资源。第一章《抗原》为样板章——整站结构、视觉、互动与评价体系即“统一标准”，后续章节按同一模板扩展。每章一个**独立二维码**，扫码直达本章页面。

> 网络教学站点只提供学生栏目；教师备赛材料（20 分钟教学设计、逐字讲课稿、板书、评分映射、自评）为**线下本地文件**，存放于仓库外的 `00_教师比赛材料/`，不随 GitHub Pages 发布、不进学生可见导航。

## 章内页面（网络教学 · 每章 13 页）

| 栏目 | 文件 | 说明 |
|---|---|---|
| 首页 | `chapter01/index.html` | 学习目标 / 重难点 / 学习路径与进度 / 学习任务清单 |
| 课前学习 | `chapter01/pre.html` | 学习任务 · 启发问题 · 旧知回顾 · 前测（即时反馈） |
| 核心知识 | `chapter01/m1.html` … `m4.html` | 模块化知识 + 图示化 + 启发性问题 + 模块自测 |
| 案例教学 | `chapter01/case.html` | 狂犬病处置 / 破伤风类毒素 / PEDV·TGEV VLP 疫苗 |
| 课堂互动 | `chapter01/quiz.html` | 课堂互动 · 在线自测（单选/多选/判断/情境，即时反馈） |
| 课后作业 | `chapter01/homework.html` | 基础 / 提升 / 拓展分层作业 |
| 学习评价 | `chapter01/eval.html` | 百分制构成 · 能力画像 · 自评量表 · 反馈问卷 |
| 课程思政 | `chapter01/sip.html` | 4 个融入点（专业知识→切入点→活动→价值引领） |
| 学科前沿 | `chapter01/frontier.html` | 4 项前沿（mRNA/AlphaFold/VLP/ASF，注明来源） |
| 扫码学习 | `chapter01/qrcode.html` | 本章二维码 + 备用网址 + 二维码规划表 |

共享资源：`assets/css/style.css`（视觉系统）、`assets/js/main.js`（测验/进度/打卡引擎，无外部依赖）、`assets/qr/`（各章二维码 PNG）。

## 构建方式（改动后必读）

```bash
python _src/build.py          # 站点根（仓库根）下执行，重新生成全部页面
```

- 改共享壳：`_src/templates/ch_shell.html`、`portal_shell.html`
- 改页面正文：`_src/pages/chapter01/*.html`（首行 `<!-- meta: title=…; desc=… -->` 生效）
- 增删页面、改导航顺序：编辑 `_src/config.json` 的 `ch1pages`
- 部署地址：`_src/config.json` 的 `deploy.ch1 / deploy.portal`（build 时注入 qrcode 页备用网址）
- 生成目录只增不删：**从 config 移除页面后请手动删除旧的生成文件**（如 `rm chapter01/teacher.html`）

## 新增章节（第 2 章起按此复制）

1. `_src/config.json`：把该章 `"status": "upcoming"` 改为 `"live"`（门户自动出卡片）；
2. 复制 `_src/pages/chapter01/` 为 `chapterXX/`，逐页替换内容（栏目与视觉不变，知识点/案例/思政/前沿按新章独立设计）；
3. `python _src/build.py` 重建 → 本地验证 → 推送；
4. 部署后写入该章公网 URL → 生成独立二维码（`python _work/gen_qr.py <URL> assets/qr/chapterXX-qr.png`，自动解码自检）→ 同步更新该章 `qrcode.html`。

## 教师比赛材料（不进网络站点）

用以下命令把已生成的教师文档导出为本地单文件（内联样式、可离线打开与打印、链接指向线上资源）：

```bash
python _work/export_teacher.py     # 输出到仓库外 00_教师比赛材料/
```

输出：`第一章_抗原_20分钟教学设计与板书.html`、`第一章_抗原_20分钟逐字讲课稿.html`。

## 内容纪律

- 科学内容忠于课件原文，不擅自改动概念；
- 扩充内容（前沿/案例/思政）均注明来源，禁止虚构文献、病例与数据；
- 若课件与其他资料冲突，先标注冲突、交由任课教师确认，不自行猜测。

## 部署与二维码

网站为纯静态、无构建依赖、无外部 CDN/字体请求，托管于 GitHub Pages（当前：公开仓库，main 分支根目录）。二维码 = 真实公网 URL 编码的标准 QR（≥1000×1000 PNG、留白充足），禁止 localhost / 本机路径；各章二维码互不相同、各自直达本章页面。
