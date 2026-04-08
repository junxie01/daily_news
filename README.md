# 热点资讯 + AI 新闻简报

一个自动抓取24小时热门资讯，并使用 AI 生成个性化新闻简报的网页应用。

**在线访问**: https://www.seis-jun.xyz/daily_news/

## 功能特性

1. **多源资讯抓取**：从新浪新闻、36氪、第一财经等40+国内外媒体抓取热门资讯
2. **智能去重聚合**：自动识别重复资讯，保留最早来源并聚合多平台数据
3. **多维度热度评分**：基于浏览量、评论数、转发量、收藏数计算综合热度
4. **交互式展示**：支持按热度/浏览量/评论数/转发量/收藏数排序，查看热门/冷门资讯
5. **AI 新闻简报**：专为科研学者定制的 AI 深度分析，包含：
   - 今日值得关注的新闻及趋势洞察
   - 科研 funding 动态、学术机会、投资洞察
   - 个性化学习路径和行动建议
   - 相关知识扩展（定义、由来、趋势）
6. **自动化更新**：GitHub Actions 每天自动抓取新闻并生成 AI 简报

## 快速开始

### 本地运行

1. 克隆仓库
2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量（可选，用于 AI 简报）：
```bash
# 复制 .env.example 为 .env 并填写你的 API 密钥
cp .env.example .env
# 编辑 .env 文件，添加你的 Qwen/DeepSeek/OpenAI API 密钥
```

4. 运行爬虫：
```bash
python scripts/fetch_news.py
```

5. 生成 AI 简报（需要配置 API 密钥）：
```bash
python scripts/generate_brief.py
```

6. 打开 `index.html` 在浏览器中查看

### 部署到GitHub Pages

1. 在GitHub上创建仓库
2. 推送代码
3. 启用GitHub Pages（Settings → Pages → Source 选择 GitHub Actions）
4. 配置GitHub Secrets（用于 AI 简报）：
   - `QWEN_API_KEY`：你的通义千问 API 密钥
   - （可选）`DEFAULT_AI_PROVIDER`：默认 AI 提供商（qwen/deepseek/openai）

## GitHub Actions 自动更新

工作流已配置为每天 UTC 23:00（北京时间早上 07:00）自动运行：

- 抓取最新资讯（从 40+ 新闻源）
- 计算热度评分并去重
- 调用 AI 生成个性化新闻简报
- 自动提交并部署到网站

也可以手动触发工作流（Actions → Update Hot News and Deploy → Run workflow）

## 项目结构

```
daily_news/
├── .github/
│   └── workflows/
│       └── update-news.yml     # GitHub Actions 配置
├── scripts/
│   ├── fetch_news.py           # 新闻爬虫脚本
│   └── generate_brief.py       # AI 简报生成脚本
├── data/                       # 数据目录
│   ├── news.json               # 新闻数据
│   └── brief.json              # AI 生成的简报
├── index.html                  # 热点资讯主页
├── brief.html                  # AI 新闻简报页面
├── .env                        # 环境变量（本地使用，不提交）
├── requirements.txt            # Python 依赖
└── README.md                   # 说明文档
```

## 集成到现有网站

本项目已部署到 https://www.seis-jun.xyz/daily_news/

### 方式1：独立页面（推荐）
1. Fork 本仓库
2. 配置 GitHub Secrets（QWEN_API_KEY）
3. 启用 GitHub Pages
4. 在您的网站添加链接指向该地址

### 方式2：子目录集成
1. 在您的网站仓库中创建 `daily_news/` 子目录
2. 将项目文件复制到该目录
3. 修改 GitHub Actions 配置以适应新路径

## 扩展爬虫

### 已支持的资讯源

| 序号 | 名称 | 网址 | 描述 | 状态 |
|------|------|------|------|------|
| 1 | Reddit | https://www.reddit.com/ | 全球最大综合社区论坛，按主题分 subreddit（如 r/technology, r/AskReddit） | 不可用 |
| 2 | Quora | https://www.quora.com/ | 问答社区，覆盖科技、文化、生活等多领域知识分享 | 待实现 |
| 3 | Stack Overflow | https://stackoverflow.com/ | 程序员技术问答首选平台（Stack Exchange 网络核心站） | 待实现 |
| 4 | Hacker News | https://news.ycombinator.com/ | Y Combinator 运营，聚焦创业、计算机科学与科技新闻 | 可用 |
| 5 | GitHub Discussions | https://github.com/ | 代码托管平台内置讨论区，开发者协作与技术交流活跃 | 待实现 |
| 6 | Dev.to | https://dev.to/ | 开发者友好型社区，分享教程、经验与开源项目 | 待实现 |
| 7 | Slashdot | https://slashdot.org/ | 老牌科技新闻论坛，"News for Nerds"，评论文化深厚 | 待实现 |
| 8 | CodeProject | https://www.codeproject.com/ | 软件开发资源与论坛，含大量代码示例与解决方案 | 待实现 |
| 9 | DZone | https://dzone.com/ | 面向开发者与技术决策者的文章、教程与社区讨论 | 待实现 |
| 10 | Codeforces | https://codeforces.com/ | 编程竞赛平台，含算法讨论区与题解社区 | 待实现 |
| 11 | Experts Exchange | https://www.experts-exchange.com/ | IT技术问答论坛（部分内容需订阅） | 待实现 |
| 12 | Unix.com Forums | https://www.unix.com/ | Unix/Linux 系统管理与开发专业论坛 | 待实现 |
| 13 | Computing.net | https://www.computing.net/ | 计算机软硬件技术支持与故障排查社区 | 待实现 |
| 14 | Quantocracy | https://quantocracy.com/ | 量化交易、金融工程领域精选内容聚合与讨论 | 待实现 |
| 15 | ResearchGate | https://www.researchgate.net/ | 全球科研人员学术交流平台，论文分享与合作枢纽 | 待实现 |
| 16 | BlackHatWorld | https://www.blackhatworld.com/ | 数字营销、SEO、联盟营销领域专业论坛（含白帽/灰帽讨论） | 待实现 |
| 17 | TripAdvisor Forums | https://www.tripadvisor.com/ | 全球旅行者经验分享、目的地攻略与酒店点评社区 | 待实现 |
| 18 | Something Awful | https://forums.somethingawful.com/ | 综合娱乐论坛（需付费注册），以幽默文化与深度讨论著称 | 待实现 |
| 19 | Super User | https://superuser.com/ | Stack Exchange 旗下，专注通用计算机技术问题解答 | 待实现 |
| 20 | Warrior Forum | https://www.warriorforum.com/ | 联盟营销、电商创业领域老牌论坛，实战经验丰富 | 待实现 |

### 内置资讯源

| 名称 | 类型 | 状态 |
|------|------|------|
| 新浪新闻 | RSS | 可用 |
| 凤凰网 | RSS | 可用 |
| 新华网 | RSS | 可用 |
| 澎湃新闻 | RSS | 可用 |
| 36氪 | RSS | 可用 |
| 虎嗅 | RSS | 可用 |
| 网易新闻 | RSS | 不可用 |
| 环球时报 | RSS | 不可用 |
| 人民网 | Web | 可用 |
| 央视网 | Web | 可用 |
| 中国新闻网 | Web | 可用 |
| 环球网 | Web | 可用 |
| 光明网 | Web | 可用 |
| 中国经济网 | Web | 可用 |
| 界面新闻 | Web | 可用 |
| 财新 | Web | 可用 |
| 第一财经 | Web | 可用 |
| 21世纪经济报道 | Web | 可用 |
| 每日经济新闻 | Web | 可用 |
| 腾讯新闻 | Web | 可用 |
| 今日头条 | Web | 可用 |
| 一点资讯 | Web | 可用 |
| 钛媒体 | Web | 可用 |
| 亿欧网 | Web | 可用 |
| PingWest | Web | 可用 |
| 爱范儿 | Web | 可用 |
| 华尔街见闻 | Web | 可用 |
| 东方财富网 | Web | 可用 |
| 金融界 | Web | 可用 |
| 中国证券报 | Web | 可用 |
| CNN | Web | 可用 |
| AP新闻 | Web | 可用 |
| NHK世界 | Web | 可用 |
| 洛杉矶时报 | Web | 可用 |
| 朝日新闻 | Web | 不可用 |
| 知乎 | API | 不可用 |

## 自定义

### 添加新闻源

编辑 `scripts/fetch_news.py`，在 `web_sources` 列表中添加新的新闻源：

```python
web_sources = [
    {'name': '新来源名称', 'url': 'https://example.com', 'selector': '.title'},
    # ... 其他来源
]
```

### 切换 AI 提供商

支持以下 AI 提供商：
- **通义千问 (Qwen)**：推荐，国内访问稳定（默认）
- **DeepSeek**：性价比高
- **OpenAI**：GPT-4o-mini 等模型
- **Moonshot (Kimi)**：国内大模型

修改 `.env` 文件或 GitHub Secrets 中的 `DEFAULT_AI_PROVIDER` 切换提供商。

## 许可证

MIT License
