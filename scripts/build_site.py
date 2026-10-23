"""Build public pages from validated Markdown. No drafts or source files are deployed."""
from __future__ import annotations

import argparse
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from html import escape
import math
from pathlib import Path
import re
import shutil
import tempfile
from xml.etree import ElementTree as ET

from markdown_it import MarkdownIt
import yaml

BASE = "https://zcanoe.github.io"
PUBLIC_FILES = ("style.css", "tokens.css", "site.js", "blog.css", "blog.js",
                "favicon.svg", "404.html", "robots.txt", ".nojekyll")
MARKER = "<!-- NOTES -->"


def text(value):
    return escape(str(value), quote=True)


def read_posts(root):
    posts, slugs = [], set()
    for path in sorted((root / "posts").glob("*.md")):
        raw = path.read_text(encoding="utf-8-sig")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", raw, re.S)
        if not match:
            raise ValueError(f"{path.name}: 缺少 YAML frontmatter")
        try:
            meta = yaml.safe_load(match[1])
        except yaml.YAMLError as exc:
            raise ValueError(f"{path.name}: frontmatter 格式错误") from exc
        if not isinstance(meta, dict):
            raise ValueError(f"{path.name}: frontmatter 必须是字段列表")
        for key in ("title", "slug", "summary"):
            if not isinstance(meta.get(key), str) or not meta[key].strip():
                raise ValueError(f"{path.name}: {key} 必须是非空文本")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", meta["slug"]):
            raise ValueError(f"{path.name}: slug 只能使用小写字母、数字和连字符")
        if meta["slug"] in slugs:
            raise ValueError(f"{path.name}: slug 重复: {meta['slug']}")
        slugs.add(meta["slug"])
        if type(meta.get("draft")) is not bool:
            raise ValueError(f"{path.name}: 请明确填写 draft: true 或 draft: false")
        day = meta.get("date")
        try:
            if isinstance(day, str):
                day = date.fromisoformat(day)
            if type(day) is not date:
                raise ValueError()
        except ValueError as exc:
            raise ValueError(f"{path.name}: date 必须是 YYYY-MM-DD") from exc
        tags = meta.get("tags", [])
        if not isinstance(tags, list) or any(not isinstance(tag, str) or not tag.strip() for tag in tags):
            raise ValueError(f"{path.name}: tags 必须是文本数组")
        if meta["draft"]:
            continue
        body = match[2]
        # Chinese characters and Latin words both contribute to reading time.
        words = len(re.findall(r"[\u3400-\u9fff]|[a-zA-Z0-9_]+", body))
        posts.append({**meta, "date": day, "tags": list(dict.fromkeys(tags)),
                      "body": body, "minutes": max(1, math.ceil(words / 350))})
    return sorted(posts, key=lambda p: (p["date"], p["slug"]), reverse=True)


def meta_line(post):
    return (f'<time datetime="{post["date"].isoformat()}">{post["date"].isoformat()}</time>'
            f'<span>·</span><span>{post["minutes"]} <span data-en="min read">分钟阅读</span></span>')


def post_row(post):
    tags = "".join(f'<span class="note-tag">{text(tag)}</span>' for tag in post["tags"])
    search = text(" ".join([post["title"], post["summary"], *post["tags"]]))
    return (f'<article class="note-row" data-note data-search="{search}">'
            f'<div class="note-meta">{meta_line(post)}</div><div class="note-info">'
            f'<h3><a href="/blog/{post["slug"]}/">{text(post["title"])}</a></h3>'
            f'<p>{text(post["summary"])}</p><div class="note-tags">{tags}</div></div>'
            '<span class="note-arrow" aria-hidden="true">↗</span></article>')


def empty_state():
    return ('<div class="notes-empty"><span class="micro">A PLACE FOR THOUGHTS</span>'
            '<h3 data-en="The first note is on its way.">第一篇随笔，正在路上。</h3>'
            '<p data-en="A space for development notes, project reflections, and things I learn along the way.">'
            '这里将记录开发笔记、项目复盘，以及学习途中值得留下的想法。</p></div>')


def homepage_notes(posts):
    return ('<section class="section notes-section" id="notes" aria-labelledby="notes-title">'
            '<div class="section-heading notes-heading"><span class="section-number">05</span>'
            '<div><h2 id="notes-title" data-en="Notes & thoughts">随笔</h2>'
            '<p data-en="Notes from building, learning, and figuring things out.">开发中的记录，学习中的思考。</p></div>'
            '<a class="text-link notes-all" href="/blog/"><span data-en="All notes">全部随笔</span> ↗</a></div>'
            + ("".join(post_row(p) for p in posts[:3]) if posts else empty_state()) + '</section>')


def shell(root, title, description, route, content, english_title=None):
    home = (root / "index.html").read_text(encoding="utf-8")
    header = re.search(r'<header class="header">.*?</header>', home, re.S)[0]
    header = header.replace('href="#top"', 'href="/"')
    for section in ("strengths", "skills", "experience", "work", "contact"):
        header = header.replace(f'href="#{section}"', f'href="/#{section}"')
    header = header.replace('href="#notes"', 'href="/blog/" aria-current="page"')
    title_en = english_title or title
    return f'''<!DOCTYPE html>
<html lang="zh-CN" data-theme="dark" data-title-zh="{text(title)}" data-title-en="{text(title_en)}">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{text(title)}</title><meta name="description" content="{text(description)}">
<meta name="theme-color" content="#111112"><meta property="og:type" content="{'article' if route != '/blog/' else 'website'}">
<meta property="og:title" content="{text(title)}"><meta property="og:description" content="{text(description)}">
<meta property="og:url" content="{BASE}{route}"><link rel="canonical" href="{BASE}{route}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/style.css"><link rel="stylesheet" href="/blog.css">
<link rel="alternate" type="application/rss+xml" title="Canoe · 随笔" href="/feed.xml">
<script>try{{var t=localStorage.getItem("canoe-theme");if(t==="light"||t==="dark")document.documentElement.dataset.theme=t;}}catch(e){{}}</script>
<script src="/site.js" defer></script><script src="/blog.js" defer></script></head>
<body id="top" class="blog-page"><a class="skip" href="#main" data-en="Skip to main content">跳到主要内容</a>
{header}<main id="main" class="wrap blog-main">{content}</main>
<footer class="wrap footer"><div><span data-en="Junbo Zhou">周俊博</span> / Canoe<br><span class="micro">NOTES ALONG THE WAY.</span></div>
<a href="/feed.xml" data-en="Subscribe via RSS">RSS 订阅 ↗</a><a href="/" data-en="Back to homepage">返回主页 ↗</a></footer></body></html>'''


def archive(root, posts):
    intro = ('<div class="blog-intro"><p class="eyebrow">CANOE / NOTES</p>'
             '<h1 data-en="Notes & thoughts">随笔</h1><p class="blog-lead" data-en="Things I build. Things I learn. Thoughts worth keeping.">'
             '记录开发，整理所学，留下一些想法。</p></div>')
    controls = ('<div class="notes-toolbar"><label for="note-search" data-en="Search notes">搜索随笔</label>'
                '<input id="note-search" type="search" placeholder="标题、简介或标签" autocomplete="off">'
                '<span id="note-count" role="status" aria-live="polite"></span></div>') if posts else ""
    content = (intro + controls + '<div class="note-list">' +
               ("".join(post_row(p) for p in posts) if posts else empty_state()) + '</div>' +
               '<p class="search-empty" id="search-empty" hidden data-en="No matching notes. Try another keyword.">'
               '没有找到相关随笔，试试其他关键词。</p>')
    return shell(root, "随笔 · 周俊博", "周俊博的开发笔记、项目复盘与学习思考。", "/blog/", content, "Notes · Junbo Zhou")


def render_markdown(body):
    parser = MarkdownIt("commonmark", {"html": False, "linkify": False}).enable(["table", "strikethrough"])
    tokens = parser.parse(body)
    headings = []
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            anchor = f"section-{len(headings) + 1}"
            token.attrSet("id", anchor)
            headings.append((anchor, tokens[i + 1].content, token.tag))
    return parser.renderer.render(tokens, parser.options, {}), headings


def article(root, post, newer, older):
    rendered, headings = render_markdown(post["body"])
    toc = "".join(f'<li class="toc-{level}"><a href="#{anchor}">{text(label)}</a></li>'
                  for anchor, label, level in headings)
    toc = ('<aside class="article-toc"><details open><summary data-en="On this page">文章目录</summary><ol>'
           + toc + '</ol></details></aside>') if toc else ""
    adjacent = ""
    for neighbor, zh, en in ((newer, "较新一篇", "Newer note"), (older, "较早一篇", "Older note")):
        if neighbor:
            adjacent += (f'<a href="/blog/{neighbor["slug"]}/"><span class="micro" data-en="{en}">{zh}</span>'
                         f'<strong>{text(neighbor["title"])}</strong></a>')
    content = (f'<article class="article"><header class="article-header">'
               '<a class="text-link" href="/blog/" data-en="← All notes">← 全部随笔</a>'
               f'<div class="note-meta">{meta_line(post)}<span>·</span><span>Canoe</span></div>'
               f'<h1>{text(post["title"])}</h1><p class="blog-lead">{text(post["summary"])}</p>'
               '<div class="note-tags">' + "".join(f'<span class="note-tag">{text(t)}</span>' for t in post["tags"]) +
               f'</div></header><div class="article-layout"><div class="prose" lang="zh-CN">{rendered}</div>{toc}</div>'
               f'<nav class="adjacent-notes" aria-label="文章翻页">{adjacent}</nav></article>')
    return shell(root, f'{post["title"]} · Canoe', post["summary"], f'/blog/{post["slug"]}/', content)


def write_xml(output, posts):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    for key, value in (("title", "Canoe · 随笔"), ("link", BASE + "/blog/"),
                       ("description", "开发笔记、项目复盘与学习思考"), ("language", "zh-CN")):
        ET.SubElement(channel, key).text = value
    for post in posts:
        item = ET.SubElement(channel, "item")
        url = f'{BASE}/blog/{post["slug"]}/'
        for key, value in (("title", post["title"]), ("link", url), ("guid", url), ("description", post["summary"]),
                           ("pubDate", format_datetime(datetime.combine(post["date"], time(), timezone.utc)))):
            ET.SubElement(item, key).text = value
        for tag in post["tags"]:
            ET.SubElement(item, "category").text = tag
    ET.ElementTree(rss).write(output / "feed.xml", encoding="utf-8", xml_declaration=True)
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    sitemap = ET.Element(ns + "urlset")
    for route in ["/", "/blog/", *[f'/blog/{p["slug"]}/' for p in posts]]:
        node = ET.SubElement(sitemap, ns + "url")
        ET.SubElement(node, ns + "loc").text = BASE + route
    ET.ElementTree(sitemap).write(output / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def build(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    # Reject accidental writes over source or outside the selected build directory.
    if output == root or root.is_relative_to(output) or output.is_symlink():
        raise ValueError("输出目录不能覆盖源代码")
    posts = read_posts(root)
    home = (root / "index.html").read_text(encoding="utf-8")
    if home.count(MARKER) != 1:
        raise ValueError("主页必须包含一个 NOTES 构建标记")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="canoe-build-", dir=output.parent) as temp:
        stage = Path(temp) / "site"
        stage.mkdir()
        for name in PUBLIC_FILES:
            shutil.copy2(root / name, stage / name)
        (stage / "index.html").write_text(home.replace(MARKER, homepage_notes(posts)), encoding="utf-8")
        (stage / "blog").mkdir()
        (stage / "blog/index.html").write_text(archive(root, posts), encoding="utf-8")
        for i, post in enumerate(posts):
            folder = stage / "blog" / post["slug"]
            folder.mkdir()
            (folder / "index.html").write_text(article(root, post, posts[i - 1] if i else None,
                                                      posts[i + 1] if i + 1 < len(posts) else None), encoding="utf-8")
        write_xml(stage, posts)
        # Replace only after validation and rendering have succeeded.
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(stage), str(output))
    return posts


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    cli.add_argument("--output", type=Path)
    args = cli.parse_args()
    result = build(args.root, args.output or args.root / "_site")
    print(f"Built {len(result)} published posts.")
