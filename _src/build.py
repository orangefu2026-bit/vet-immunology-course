# -*- coding: utf-8 -*-
"""站点构建器：_src/pages/<chapter>/<page>.html 片段 + 壳模板 → vet-immuno-course/ 成品
用法：python _src/build.py
后续新增章节：在 _src/config.json 登记章节 + 建立 _src/pages/chapterXX/*.html 片段，重跑即可。
"""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = SITE
cfg = json.load(open(os.path.join(SRC, "config.json"), encoding="utf-8"))
CH_PAGES = cfg["ch1pages"]
CHAPTERS = cfg["chapters"]


def render_template(name):
    return open(os.path.join(SRC, "templates", name), encoding="utf-8").read()


def meta_of(frag):
    """页面片段首行支持 <!-- meta: title=..; desc=.. -->"""
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


DEPLOY = {k: v for k, v in (cfg.get("deploy") or {}).items() if v}


def apply_deploy(text):
    """把片段中的 @@CH1_URL@@ / @@PORTAL_URL@@ 替换为已配置的公网地址（未配置则给出提示文案）"""
    placeholders = {
        "@@CH1_URL@@": ("ch1", "本章公网地址"),
        "@@PORTAL_URL@@": ("portal", "课程门户公网地址"),
    }
    for tok, (key, label) in placeholders.items():
        if tok in text:
            val = DEPLOY.get(key, "")
            text = text.replace(
                tok,
                val if val else f"（{label}将在网站部署并写入 _src/config.json 后自动显示）",
            )
    return text


def build_chapter(ch_key, pages, nav_home="../index.html"):
    sh = render_template("ch_shell.html")
    frag_dir = os.path.join(SRC, "pages", ch_key)
    out_dir = os.path.join(OUT, ch_key)
    os.makedirs(out_dir, exist_ok=True)
    built = []
    for i, p in enumerate(pages):
        frag_path = os.path.join(frag_dir, p["file"])
        if not os.path.exists(frag_path):
            print("  ! 缺少片段:", frag_path)
            continue
        frag = open(frag_path, encoding="utf-8").read()
        title, desc = meta_of(frag)
        # 导航
        nav_items = []
        for pp in pages:
            cls = "active" if pp["file"] == p["file"] else ""
            nav_items.append(f'<a href="{pp["file"]}" class="{cls}">{pp["nav"]}</a>')
        nav = "".join(nav_items)
        foot_nav = "".join(
            f'<li><a href="{pp["file"]}">{pp["short"]}</a></li>' for pp in pages
        )
        # 上一页 / 下一页
        idx = pages.index(p)
        prev, nxt = None, None
        if idx > 0:
            prev = pages[idx - 1]
        if idx < len(pages) - 1:
            nxt = pages[idx + 1]
        pager_bits = []
        if prev:
            pager_bits.append(
                f'<a class="btn" href="{prev["file"]}">← {prev["short"]}</a>'
            )
        if nxt:
            pager_bits.append(
                f'<a class="btn primary" style="margin-left:auto" href="{nxt["file"]}">继续：{nxt["short"]} →</a>'
            )
        pager = (
            '<div class="wrap" style="display:flex;gap:10px;margin-top:34px">'
            + "".join(pager_bits)
            + "</div>"
            if pager_bits
            else ""
        )
        page = (
            sh.replace("%%CHAPTER%%", ch_key)
            .replace("%%PAGE%%", p["file"])
            .replace("%%TITLE%%", title)
            .replace("%%DESC%%", desc)
            .replace("%%NAV%%", nav)
            .replace("%%FOOTNAV%%", foot_nav)
            .replace("%%PAGER%%", pager)
            .replace("%%CONTENT%%", apply_deploy(frag))
        )
        outp = os.path.join(out_dir, p["file"])
        with open(outp, "w", encoding="utf-8") as f:
            f.write(page)
        built.append(outp)
        print(f"  ✓ {outp}")
    return built


def chapter_card(ch):
    if ch["status"] == "live":
        icon = "✓"
        href = f'{ch["key"]}/index.html'
        st = "已上线 · 可扫码学习"
        cls = "live"
    else:
        icon = "…"
        href = "#upcoming"
        st = "按同一模板建设中"
        cls = "soon"
    return f"""<a class="nav-card {cls}" href="{href}">
  <span class="nc-idx">{ch["no"].replace("第", "").replace("章", "")}</span>
  <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap">
    <span class="chip b-k">{ch["no"]}</span>
    <span class="chip {'b-ok' if ch['status']=='live' else 'b-mute'}">{st}</span>
  </div>
  <div class="nc-title">{ch["title"]} <span class="en" style="color:var(--c-main2);font-weight:600;font-size:13px">{ch["en"]}</span></div>
  <div class="nc-desc">{ch["subtitle"]}</div>
  <div class="nc-go">{"进入本章学习 →" if ch["status"]=="live" else "后续开放，敬请期待"}</div>
</a>"""


def main():
    # 1) 章节页面
    ch = "chapter01"
    print("构建章节:", ch)
    build_chapter(ch, CH_PAGES)

    # 2) 门户
    print("构建门户 …")
    shell = render_template("portal_shell.html")
    frag_path = os.path.join(SRC, "pages", "_portal", "index.html")
    frag = open(frag_path, encoding="utf-8").read()
    title, desc = meta_of(frag)
    cards = "\n".join(chapter_card(c) for c in CHAPTERS)
    frag = frag.replace("%%CHAPTERS%%", cards)
    portal = (
        shell.replace("%%TITLE%%", title)
        .replace("%%DESC%%", desc)
        .replace("%%CONTENT%%", apply_deploy(frag))
    )
    outp = os.path.join(OUT, "index.html")
    with open(outp, "w", encoding="utf-8") as f:
        f.write(portal)
    print("  ✓", outp)
    print("完成。共生成文件：", len(os.listdir(os.path.join(OUT, "chapter01"))) + 1, "（另含 assets 静态资源）")


if __name__ == "__main__":
    main()
