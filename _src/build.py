# -*- coding: utf-8 -*-
"""站点构建器 v2（多章）
- _src/pages/<chapter>/<page>.html 片段 + 壳模板 → 站点根生成成品
- 遍历 config.chapters 中 status=live 的章，页面清单=student_pages（13 项，学生栏目）
- 教师源页（teacher_pages）不写入站点；由 _work/export_teacher.py 复用本模块渲染后输出到
  仓库外 00_教师比赛材料/（如需：python _work/export_teacher.py）
用法：python _src/build.py
"""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(SRC, "config.json"), encoding="utf-8"))
CHAPTERS = cfg["chapters"]
STUDENT_PAGES = cfg["student_pages"]
TEACHER_PAGES = cfg["teacher_pages"]
DEPLOY = {k: v for k, v in (cfg.get("deploy") or {}).items() if v}


def render_template(name):
    return open(os.path.join(SRC, "templates", name), encoding="utf-8").read()


def meta_of(frag):
    title, desc = "", ""
    for line in frag.splitlines()[:6]:
        m = re.search(r"<!--\s*meta:\s*(.*?)-->", line)
        if m:
            for kv in m.group(1).split(";"):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    if k.strip() == "title":
                        title = v.strip()
                    elif k.strip() == "desc":
                        desc = v.strip()
    return title, desc


def apply_deploy(text):
    """把 @@CH1_URL@@ / @@PORTAL_URL@@ 替换为已配置公网地址；并在任意章节页把
    @@CHX_URL@@(key) 形式令牌替换（兼容旧模板）。"""
    if "@@CH1_URL@@" in text:
        text = text.replace("@@CH1_URL@@", DEPLOY.get("ch1", ""))
    if "@@PORTAL_URL@@" in text:
        text = text.replace("@@PORTAL_URL@@", DEPLOY.get("portal", ""))
    for tok in re.findall(r"@@(CH\d+_URL|PORTAL_URL)@@", text):
        pass  # 保守：未知令牌保留原文由调用方处理
    return text


def shell_tokens(ch):
    return {
        "%%CHAPTER%%": ch["key"],
        "%%CH_NO%%": ch.get("no", ""),
        "%%CH_TITLE%%": ch.get("title", ""),
        "%%CH_EN%%": ch.get("en", ""),
        "%%CH_SUB%%": ch.get("subtitle", ""),
        "%%CH_DESC%%": ch.get("desc", ""),
        "%%CH_BAR%%": ch.get("bar", ch.get("no", "")),
    }


def apply_shell(page, ch, extra=None):
    for k, v in shell_tokens(ch).items():
        page = page.replace(k, v)
    if extra:
        for k, v in extra.items():
            page = page.replace(k, v)
    return page


def render_page(ch, frag, page_file, nav_pages, out_html=True):
    """渲染单页完整 HTML（供站点输出与教师包导出共用）"""
    sh = render_template("ch_shell.html")
    title, desc = meta_of(frag)
    nav_items = []
    for pp in nav_pages:
        cls = "active" if pp["file"] == page_file else ""
        nav_items.append(f'<a href="{pp["file"]}" class="{cls}">{pp["nav"]}</a>')
    foot_nav = "".join(
        f'<li><a href="{pp["file"]}">{pp["short"]}</a></li>' for pp in nav_pages
    )
    files = [pp["file"] for pp in nav_pages]
    idx = files.index(page_file) if page_file in files else -1
    pager_bits = []
    if idx > 0:
        pager_bits.append(f'<a class="btn" href="{nav_pages[idx-1]["file"]}">← {nav_pages[idx-1]["short"]}</a>')
    if 0 <= idx < len(nav_pages) - 1:
        pager_bits.append(
            f'<a class="btn primary" style="margin-left:auto" href="{nav_pages[idx+1]["file"]}">继续：{nav_pages[idx+1]["short"]} →</a>')
    pager = ('<div class="wrap" style="display:flex;gap:10px;margin-top:34px">'
             + "".join(pager_bits) + "</div>") if pager_bits else ""
    page = (
        sh.replace("%%TITLE%%", title)
        .replace("%%DESC%%", desc)
        .replace("%%NAV%%", nav_items and "".join(nav_items) or "")
        .replace("%%FOOTNAV%%", foot_nav)
        .replace("%%PAGER%%", pager)
        .replace("%%CONTENT%%", apply_deploy(frag))
    )
    page = apply_shell(page, ch)
    # 当前章公网地址注入（qrcode 页备用网址等）
    this_url = DEPLOY.get("ch" + ch["key"].replace("chapter", ""), "") or DEPLOY.get(ch["key"], "")
    if "@@THIS_URL@@" in page:
        page = page.replace("@@THIS_URL@@", this_url or "（该章公网地址将在部署后自动显示）")
    return page


def build_chapter(ch, pages, out_dir):
    frag_dir = os.path.join(SRC, "pages", ch["key"])
    os.makedirs(out_dir, exist_ok=True)
    for p in pages:
        frag_path = os.path.join(frag_dir, p["file"])
        if not os.path.exists(frag_path):
            print(f"  ! 缺片段: {ch['key']}/{p['file']}（跳过）")
            continue
        frag = open(frag_path, encoding="utf-8").read()
        page = render_page(ch, frag, p["file"], pages)
        outp = os.path.join(out_dir, p["file"])
        with io.open(outp, "w", encoding="utf-8") as f:
            f.write(page)
        print(f"  ✓ {os.path.relpath(outp, SITE)}")


def chapter_card(ch):
    if ch["status"] == "live":
        href = f'{ch["key"]}/index.html'
        st, cls = "已上线 · 可扫码学习", "live"
    else:
        href, st, cls = "#upcoming", "建设中", "soon"
    no = ch.get("no", "").replace("第", "").replace("章", "")
    return f"""<a class="nav-card {cls}" href="{href}">
  <span class="nc-idx">{no}</span>
  <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap">
    <span class="chip b-k">{ch.get("no","")}</span>
    <span class="chip {'b-ok' if ch['status']=='live' else 'b-mute'}">{st}</span>
  </div>
  <div class="nc-title">{ch["title"]} <span class="en" style="color:var(--c-main2);font-weight:600;font-size:13px">{ch["en"]}</span></div>
  <div class="nc-desc">{ch["subtitle"]}</div>
  <div class="nc-go">{"进入本章学习 →" if ch["status"]=="live" else "后续开放，敬请期待"}</div>
</a>"""


def main():
    portal_shell = render_template("portal_shell.html")
    frag = open(os.path.join(SRC, "pages", "_portal", "index.html"), encoding="utf-8").read()
    title, desc = meta_of(frag)
    cards = "\n".join(chapter_card(c) for c in CHAPTERS)
    frag = apply_deploy(frag).replace("%%CHAPTERS%%", cards)
    portal = (portal_shell.replace("%%TITLE%%", title)
              .replace("%%DESC%%", desc)
              .replace("%%CONTENT%%", frag))
    with io.open(os.path.join(SITE, "index.html"), "w", encoding="utf-8") as f:
        f.write(portal)
    print("✓ 门户 index.html")

    for ch in CHAPTERS:
        if ch["status"] != "live":
            continue
        print(f"构建章节: {ch['key']}")
        build_chapter(ch, STUDENT_PAGES, os.path.join(SITE, ch["key"]))
    print("完成。")


if __name__ == "__main__":
    main()
