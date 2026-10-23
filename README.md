# 周俊博 · 个人主页与随笔

> 当前源码仓库为私有，联系邮箱为 `internetcanoe@gmail.com`。GitHub Free 不支持私有仓库的 Pages，因此当前 `github.io` 网站停用。CI 仍会校验文章并构建，Pages 未启用时跳过部署。若要保持源码私有并恢复此地址，请升级支持私有 Pages 的套餐，在 Settings → Pages 启用 GitHub Actions；之后提交文章或手动运行工作流即可恢复自动发布。

主页：<https://zcanoe.github.io/> · 随笔：<https://zcanoe.github.io/blog/>

## 发布随笔（只需浏览器）

1. 用 **zCanoe** 登录 GitHub，打开 [新建文章](https://github.com/zCanoe/zcanoe.github.io/new/main/posts)，文件名填 `my-note.md`，保留在 `posts/` 目录。
2. 粘贴下面模板，填写标题、日期、唯一英文 slug、简介、标签和正文。
3. 写好后设置 `draft: false`，点 **Commit changes** 提交到 **main**。
4. 在 [Actions](https://github.com/zCanoe/zcanoe.github.io/actions/workflows/pages.yml) 查看 **Build and deploy site**。Pages 启用后，成功部署会一起更新文章页、归档、主页最新 3 篇、RSS 和 sitemap，通常需要几分钟；当前未启用 Pages 时仅校验和构建，部署显示 skipped。

```markdown
---
title: "我的文章标题"
date: 2026-10-23
slug: my-note
summary: "用一两句话介绍这篇文章。"
tags: [Java, 开发笔记]
draft: false
---

正文从这里开始，使用 Markdown。

## 一个小标题

记录问题、思考和解决过程。
```

- `slug` 仅用小写英文字母、数字和连字符，全站唯一。发布后尽量不改，否则原链接失效。
- `date` 用 `YYYY-MM-DD`，按日期倒序展示；未来日期不是定时发布，`draft: false` 会立即发布。
- `draft` 必须明确写 `true` 或 `false`；`true` 不进入网站、RSS 或 sitemap。
- **公开仓库的草稿 Markdown 在 GitHub 上仍然可见。未准备公开的内容请保存在本地，不要提交。**
- 支持标题、列表、引用、链接、远程图片、代码块、表格和删除线。原始 HTML 不执行；目前不复制本地图片目录，请用公开的 HTTPS 图片链接。
- 自动生成目录和阅读时间；中英文按钮切换界面，正文保留原文。

## 修改、撤回与失败恢复

打开 [posts 目录](https://github.com/zCanoe/zcanoe.github.io/tree/main/posts)，编辑对应 `.md` 并提交即可更新。把 `draft` 改为 `true` 或删除文件并提交即可撤下。GitHub 历史仍保留原内容，CDN/搜索引擎也可能有缓存，请勿提交隐私资料。

校验失败时不会发布，线上保留上一次成功版本。在 Actions 打开失败任务的 build 步骤，按提示修复再提交；也可点击 Run workflow 手动重建。

## 发布权限与 CI/CD

访客只能阅读，没有公开投稿接口或自建密码。写作使用 GitHub 登录和仓库写权限。请保持仓库只有本人拥有写权限，不要邀请其他写入者或给不可信 GitHub App 写权限。

`.github/workflows/pages.yml`：PR 只运行测试和构建；仅仓库 `zCanoe/zcanoe.github.io` 的拥有者在 `main` 上触发 push/手动运行才可部署。构建只读仓库，部署只授予 Pages 和 OIDC 权限，无需 PAT 或额外 Secrets。GitHub 管理员始终可以修改工作流，此限制基于你独占账号与仓库管理权限。

Settings → Pages → Source 设为 **GitHub Actions**。`_site/` 为构建产物，只复制公开资源，草稿、源文档、构建脚本不进入 Pages。

## 本地预览与测试

需要 Python 3.12：

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/build_site.py
python -m http.server 8080 --directory _site
```

打开 <http://localhost:8080/>。源 `index.html` 的 NOTES 标记由构建替换，预览请使用 `_site/`。

## 页面维护

- `index.html`：中文主页、`data-en` 英文文案与随笔构建标记。
- `tokens.css` / `style.css`：主题布局；`blog.css`：随笔排版。
- `site.js`：语言、主题、导航、打印；`blog.js`：归档搜索。
- `scripts/build_site.py`：校验、Markdown、文章/归档/首页生成、RSS 和 sitemap。

保留中英文、深浅主题、移动导航及打印。页面没有第三方运行时或统计服务。仅公开邮箱和 GitHub，不提供手机号、证件照或原始简历下载。
