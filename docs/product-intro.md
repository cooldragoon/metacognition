# MetaCognition 产品介绍

> **你的 AI 编程助手越用越聪明。**
>
> 同一个坑，不跳第二次。同一个 bug，不查第二次。同一个教训，不学第二次。
> 每次说"记住了"，它真的记住了——下次打开 Claude Code，陷阱已经在等你绕开它。

## 定位

**三个系统，各司其职：**

| 系统 | 解决什么问题 | 一句话 |
|------|------------|--------|
| **Superpowers** | 过程纪律 | 你怎么工作 — brainstorming → TDD → review → ship |
| **gstack** | 工程质量 | 你建了什么 — 浏览器 QA、专家 review、设计审查 |
| **MetaCognition** | 知识持久化 | **你学到了什么** — 陷阱记忆、跨会话检索、自动提醒 |

Superpowers 让你**不跳步骤**。gstack 让你**不走弯路**。MetaCognition 让你**不踩同一个坑两次**。

三个系统独立运行，没有硬依赖。你可以在只用 Superpowers 的项目里加 MetaCognition，也可以在 gstack 的 review 流程中嵌入 MetaCognition 的知识检索。

---

## 解决的核心痛点

### 痛点 1：经验在会话关闭后清零

你花 3 小时排查了一个诡异的环境问题——VS Code 终端里 conda 找不到，最后发现是 Terminal Profile 默认用了 PowerShell。下次换了个项目、过了一周，遇到同样的症状，从零开始排查。

**MetaCognition 怎么解决**：解决问题后说"记住了"，系统自动记录 symptom/root_cause/resolution + query variants。下次 Session Start 自动检索命中，直接提示已知方案。

### 痛点 2：盲目重试消耗 Token 和代码质量

同一个 bug 修了 3 次还没好，Claude Code 在有限的上下文里反复试不同的方案，每次尝试都改一堆文件，代码树越来越乱。

**MetaCognition + Superpowers debugging**：Superpowers 的 systematic-debugging 在 2 次失败后强制停下来分析根因。MetaCognition 在停下来的时候检索知识库——"这个错误之前见过吗？"——如果有匹配，直接注入已知根因，跳过无效重试。

### 痛点 3：团队知识只存在老人脑子里

Alice 踩过的 Docker 卷挂载陷阱，Bob 2 周后原样踩一次。新人 Dave 入职第一周，80% 的时间在踩老人早已知道的坑。

**MetaCognition 怎么解决**：每条 insight 有 hit_count。同一条陷阱被 3 个人命中 5 次后自动晋升为 Live Constraint。所有人的 Session Start 自动加载。

### 痛点 4：规则库膨胀导致主智能体幻觉

把所有偶发经验直接写进 CLAUDE.md → 每次会话都加载 → 上下文被稀释 → 模型在处理微小任务时也能看到完全不相关的规则 → 产生幻觉或拒绝执行。

**MetaCognition 怎么解决**：知识按需检索。Session Start 只注入与当前项目+环境匹配的 top-N 条约束。Micro 任务（改个 CSS 颜色）零感知通过。知识衰减机制保证过时规则自动降级。

---

## 使用场景

### 场景 A：Session Start 自动守护

```
你打开 Claude Code，什么都没说。

MetaCognition 自动运行:
  → retrieve("metacognition Windows Python bash VS Code Claude Code")
  → 命中 3 条 high-severity 已知陷阱
  → 展示给你:

⚠ 发现已知陷阱:

1. [HIGH] conda activate 在 VS Code 终端中失败
   → 把 Terminal Profile 从 PowerShell 改成 Git Bash
   
2. [HIGH] MCP Server 配了 settings.local.json 不生效
   → 用 claude mcp add --scope user 注册

3. [HIGH] MCP Server 改代码后 SyntaxError 导致静默失败
   → 改完 server.py 先跑 py_compile.compile() 检查语法
```

你没问任何问题，但已经避开了 3 个可能浪费你数小时的陷阱。

### 场景 B：TDD + 检索测试模式

```
你: 给 UserProfile 组件写个异步加载的测试

Claude 写了个用 jest.mock('../api/userApi') 的测试。
你: 这个 mock 方式太脆弱，重构后路径变了就失效。

Claude 第 2 次尝试 —— 用了 waitFor({ timeout: 1000 })
你: 魔法数字在 CI 里会失败。

MetaCognition detect 2 次失败:
  → retrieve("react async component test mock pattern fragile")
  → 命中: "React 异步组件测试用 MSW 替代 jest.mock"
  → 注入上下文: 使用 MSW + waitForElementToBeRemoved + 显式状态断言
  
Claude 第 3 次: 直接应用 MSW 模式，一次通过。
你: 测试不再耦合实现细节，重构后自动通过。
```

### 场景 C：gstack review 发现 → MetaCognition 记住 → 下次自动提醒

```
gstack /review 发现了 N+1 查询问题。

你: 修好了。记住了。

MetaCognition:
  → draft_insight(symptom="N+1 in user list endpoint",
      root_cause="has_many association not eager-loaded",
      resolution="Always check includes() for has_many in list endpoints",
      variants=["lazy loading causing extra queries", "association preload in API endpoint", ...])

下次 gstack review 同一个项目的另一个 PR:
  → Session Start 检索命中 "N+1" insight
  → 评审上下文自动注入: "这个项目之前出现过 N+1 查询问题，检查 includes()"

review 的 specialist agent 看到了这条约束，直接用它检查新代码。
```

### 场景 D：新成员 Onboarding

```
Dave 第一天入职，clone 项目，装好 Claude Code + MetaCognition。

打开 Claude Code:
  → Session Start 自动检索
  → 9 条种子 insight 全部命中匹配
  → 展示 top-5 高严重度陷阱:
  
  "Welcome! 以下是该项目已知的 5 条防御红线:"

Dave 还没写一行代码，已经知道了:
  - MCP 配置用什么格式
  - 改完 server 代码要先 syntax check
  - Windows 上 bash 路径处理约定
  - conda 终端 Profile 设置
  - 新 MCP tool 要加 permissions 白名单

Onboarding 从 "踩坑一周学会" 变成 "打开 IDE 即知"。
```

---

## 与 Superpowers 的嵌入点

| Superpowers 阶段 | MetaCognition 动作 |
|-----------------|-------------------|
| **Session Start** | `retrieve` — 加载已知陷阱 |
| **brainstorming** （Phase 3 计划） | 检索类似设计决策、已知反模式 |
| **writing-plans**（Phase 3 计划） | 检索受影响模块的历史脆弱性 |
| **systematic-debugging**（Phase 3 计划） | 检索类似 bug 的历史根因 |
| **执行中** | "记住了" → `draft_insight` |
| **verification-before-completion**（Phase 3 计划） | 全量决策门检查 |

## 与 gstack 的嵌入点

| gstack 阶段 | MetaCognition 动作 |
|------------|-------------------|
| **/review** | 检索项目历史 bug 模式 → 注入 specialist agent |
| **/qa** | 检索已知测试反模式 → 注入测试策略上下文 |
| **/investigate** | 检索类似排查路径 → 加速根因定位 |
| **/ship** | 检查所有 Live Constraint 是否满足 → gate check |

---

## 技术特性

| 特性 | 实现 |
|------|------|
| **存储** | 本地 Markdown 文件，零外部依赖 |
| **搜索** | model2vec 向量 (256-dim, 32ms) + Jaccard 关键词 fallback |
| **去重** | 写入时关键词 + 向量双重去重 |
| **Query variants** | 每条 insight 嵌入 2-4 种不同问法，提升语义召回 |
| **知识生命周期** | draft → live (hit>=5) → archive (180d) |
| **衰减** | 90 天未命中 hit_count 减半，防止僵尸规则 |
| **种子数据** | 开箱自带 9 条 insight，新用户即刻体验 |
| **测试** | 46 场景, 0.2s, 0 失败 |
| **平台** | Windows / macOS / Linux |

---

## 与 Claude Code Auto-Memory 的关系

Claude Code 内置了 Auto-Memory（`~/.claude/projects/*/memory/`），它们不冲突：

| | Auto-Memory | MetaCognition |
|---|---|---|
| **记什么** | 用户偏好、反馈、项目上下文 | 陷阱、反模式、解决方案 |
| **谁触发** | 后台 agent 自动 | 用户主动说"记住了" |
| **检索时机** | 会话初始化 | Session Start + 按需 |
| **结构** | 自由文本 markdown | 结构化 symptom/root_cause/resolution + variants |
| **生命周期** | 无 | draft → live → archive + 衰减 |

Auto-Memory 记"你喜欢什么"。MetaCognition 记"坑在哪里"。缺哪个补哪个。

---

*MetaCognition — 让你的 AI 编程助手不仅有过程纪律 (Superpowers) 和工程能力 (gstack)，还有跨会话的记忆。*
