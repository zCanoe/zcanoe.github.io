# 周俊博 · 个人主页

用于面试展示的静态个人主页，发布地址：https://zcanoe.github.io/

包含个人优势、技能、工作经历、项目职责与联系方式，支持中英文、深浅主题、移动端导航和打印为 PDF。

## 本地预览

在当前目录运行 `python -m http.server 8080`，然后打开 http://localhost:8080/ 。也可以直接打开 index.html。

## 更新内容

- `index.html`：中文内容写在元素中，英文写在对应 `data-en` 属性中；修改时同时更新两者。
- `tokens.css`：颜色与字体。
- `style.css`：布局、响应式和打印样式。
- `site.js`：语言、主题、导航与打印交互。

内容来自本人提供的简历；未虚构量化结果。网站不使用构建框架、第三方脚本、外部字体、数据采集或表单后端。

按本人选择，网站仅公开邮箱和 GitHub，不包含手机号、证件照或原始简历 PDF。

## GitHub Pages

仓库名为 `zcanoe.github.io`。在 Settings → Pages 选择 `Deploy from a branch`，设置 `main` 分支与 `/(root)` 目录，保存。每次提交后由 GitHub 自动更新网站。

页头的“保存为 PDF”使用浏览器打印功能，打印时会自动展开项目详情，结束后恢复原有状态。
