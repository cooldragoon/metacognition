# GitHub Upload Guide

## 1. Create the GitHub Repository

Go to [github.com/new](https://github.com/new) and create a new repository:

- **Repository name**: `metacognition`
- **Description**: `A verifiable cross-model cognitive architecture for Claude Code — evolve from session-smart to cross-session wise.`
- **Public** or **Private** (your choice)
- **Do NOT** check "Add a README file" (we already have one)
- **Do NOT** check ".gitignore" (we already have one)
- **Do NOT** check "Choose a license" (we already have one)

## 2. Push the Code

After creation, GitHub shows the `…or push an existing repository from the command line` instructions:

```bash
cd D:/cc/metacognition

# Add the remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/metacognition.git

# Push to GitHub
git push -u origin master
```

> If you have SSH keys configured, you can use the SSH URL instead:
> ```bash
> git remote add origin git@github.com:YOUR_USERNAME/metacognition.git
> git push -u origin master
> ```

## 3. Verify

Visit `https://github.com/YOUR_USERNAME/metacognition` and confirm:

- [ ] README.md renders correctly
- [ ] File tree is complete (35+ files)
- [ ] LICENSE shows MIT
- [ ] No stray files (.npy, models/, .claude/ are excluded by .gitignore)

## 4. Optional Settings

### Add Topic Tags
In the "About" section on the repo page, click the gear icon and add tags:
```
claude-code mcp knowledge-management ai-agent metacognition dev-tools
```

### Branch Protection
Settings → Branches → Add branch protection rule:
- Branch name pattern: `master`
- Check "Require a pull request before merging"

## 5. Team Collaboration

### New member onboarding

```bash
git clone https://github.com/YOUR_USERNAME/metacognition.git
cd metacognition
bash expert-brain-server/setup.sh
claude mcp add --scope user expert-brain -- python expert-brain-server/server.py
# Restart Claude Code → Session Start auto-shows seed pitfalls
```

### Sharing a promoted insight

```bash
# After local promotion (hit_count >= 5)
git add .cursor/insights/wiki/live/<insight-file>.md
git commit -m "promote: <insight title>"
git push

# Teammates pull, then run setup.sh to rebuild index/log
```

> Personal draft insights stay local. Only `live/` goes through PR merge.

## 6. Pre-Push Checklist

| File | Purpose |
|------|---------|
| `README.md` | Project landing page (English) |
| `README_zh.md` | Project landing page (Chinese) |
| `CLAUDE.md` | Project guide for AI agents |
| `AGENTS.md` | Agent entry point |
| `LICENSE` | MIT License |
| `CHANGELOG.md` | Release history |
| `.gitignore` | Exclusion rules |
| `expert-brain-server/` | MCP server source code |
| `.claude/skills/metacognition/SKILL.md` | Behavior contract |
| `.cursor/insights/wiki/draft/*.md` | Seed insights |
| `.cursor/insights/wiki/live/*.md` | Sample live constraints |
| `docs/product-intro.md` | Product introduction |
| `docs/github-upload-guide.md` | This guide |
| `docs/superpowers/specs/*` | Design specs |
| `docs/superpowers/plans/*` | Implementation plans |
