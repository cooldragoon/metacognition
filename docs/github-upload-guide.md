# GitHub 上传教程

## 1. 创建 GitHub 仓库

在 [github.com/new](https://github.com/new) 创建新仓库：

- **Repository name**: `metacognition`
- **Description**: `可验证的跨模型认知架构 — 让 Claude Code 从单次会话的聪明进化为跨会话的睿智。`
- **Public** 或 **Private**（自选）
- **不要** 勾选 "Add a README file"（我们已经有了）
- **不要** 勾选 ".gitignore"（我们已经有了）
- **不要** 勾选 "Choose a license"（我们已经有了）

## 2. 推送代码

创建完成后，GitHub 会显示 `…or push an existing repository from the command line` 的指引：

```bash
cd D:/cc/metacognition

# 添加远程仓库（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/metacognition.git

# 推送到 GitHub
git push -u origin master
```

> 如果已配置 SSH Key，也可以使用 SSH 地址：
> ```bash
> git remote add origin git@github.com:YOUR_USERNAME/metacognition.git
> git push -u origin master
> ```

## 3. 验证推送结果

推送成功后访问 `https://github.com/YOUR_USERNAME/metacognition`，检查：

- [ ] README.md 正常渲染
- [ ] 文件结构完整（31+ 个文件）
- [ ] LICENSE 显示 MIT
- [ ] 没有多余文件（.npy, models/, .claude/ 等已排除）

## 4. 可选设置

### 添加 Topic 标签
在仓库页面的 "About" 区域，点击齿轮图标，添加 tags：
```
claude-code, mcp, knowledge-management, ai-agent, metacognition, dev-tools
```

### 添加项目网站
如果后续部署文档网站，可以在 About 区域填入 URL。

### 保护分支
Settings → Branches → Add branch protection rule：
- Branch name pattern: `master`
- 勾选 "Require a pull request before merging"

## 5. 团队协作流程

### 新成员加入

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/metacognition.git
cd metacognition

# 一键安装
bash expert-brain-server/setup.sh

# 注册 MCP Server
claude mcp add --scope user expert-brain -- python expert-brain-server/server.py

# 重启 Claude Code → Session Start 自动展示种子陷阱
```

### 分享晋升的 insight

```bash
# 在本地晋升后（hit_count >= 5）
git add .cursor/insights/wiki/live/<insight-file>.md
git commit -m "promote: <insight title>"
git push

# 通知队友 pull
# 队友拉取后跑一次 setup.sh 重建 index/log
```

> 个人 draft insight 保留在本地，不 push。
> 只通过 PR 合并 `live/` 目录的变更。

## 6. 首次推送确认清单

推送前确认以下文件都在仓库中且内容正确：

| 文件 | 用途 | 
|------|------|
| `README.md` | 产品入口 |
| `CLAUDE.md` | 项目指南 |
| `AGENTS.md` | Agent 入口 |
| `LICENSE` | MIT 授权 |
| `CHANGELOG.md` | 版本历史 |
| `.gitignore` | 排除规则 |
| `expert-brain-server/` | MCP Server 核心代码 |
| `.claude/skills/metacognition/SKILL.md` | 行为契约 |
| `.cursor/insights/wiki/draft/*.md` | 种子数据 |
| `.cursor/insights/wiki/live/*.md` | 示例约束 |
| `docs/product-intro.md` | 产品介绍 |
| `docs/github-upload-guide.md` | 本教程 |
| `docs/superpowers/specs/*` | 设计文档 |
| `docs/superpowers/plans/*` | 实施计划 |
