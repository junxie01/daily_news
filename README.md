# 每日趣闻 · 全球猎奇

一个自动抓取并展示「好玩 / 奇怪 / 长见识」资讯的网页应用，专为爱看全球趣闻的人打造。

**在线访问**: https://www.seis-jun.xyz/daily_news/

## 功能特性

1. **双栏资讯**：「趣新闻」（Reddit 趣味 subreddit、Hacker News、Atlas Obscura / Kottke / Mental Floss 等奇趣 RSS）与「硬新闻」（微博 / 百度 / 头条 / B站 / 抖音 / 知乎 中文热榜）分开抓取，网页顶部一键切换
2. **智能去重聚合**：自动识别重复资讯，保留最早来源并聚合多平台数据
3. **四维热度打分**：浏览量 / 评论数 / 转发量 / 收藏数 四个维度各按排名占 25%，合计满分 100（真实指标，不伪造）
4. **缩略图 + 历史归档**：资讯带封面图（无图源用渐变占位块兜底）；每天快照存入 `data/archive/YYYY-MM-DD.json`，网页可翻看往期
5. **交互式展示**：支持按热度/浏览量/评论数/转发量/收藏数排序，并在「趣新闻 / 硬新闻」之间切换
6. **自动化更新**：GitHub Actions 每天自动抓取新闻并部署网页，无需 AI API 或付费额度

> 源清单以代码为准：`scripts/fetch_news.py` 里的 `rss_sources`、`web_sources`，以及 `fetch_reddit()` 中的 subreddit 列表。想加/换源直接改这几处即可。

## 快速开始

### 本地运行

1. 克隆仓库
2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行爬虫：
```bash
python scripts/fetch_news.py
```

4. 打开 `index.html` 在浏览器中查看

### 部署到GitHub Pages

1. 在GitHub上创建仓库
2. 推送代码
3. 启用GitHub Pages（Settings → Pages → Source 选择 GitHub Actions）

## GitHub Actions 自动更新

工作流已配置为每天 UTC 23:00（北京时间早上 07:00）自动运行：

- 抓取最新资讯（从 40+ 新闻源）
- 计算热度评分并去重
- 自动提交并部署到网站

也可以手动触发工作流（Actions → Update Hot News and Deploy → Run workflow）

## 项目结构

```
daily_news/
├── .github/
│   └── workflows/
│       └── update-news.yml     # GitHub Actions 配置
├── scripts/
│   └── fetch_news.py           # 新闻爬虫脚本
├── data/                       # 数据目录
│   └── news.json               # 新闻数据
├── index.html                  # 热点资讯主页
├── requirements.txt            # Python 依赖
└── README.md                   # 说明文档
```

## 集成到现有网站

本项目已部署到 https://www.seis-jun.xyz/daily_news/

### 方式1：独立页面（推荐）
1. Fork 本仓库
2. 启用 GitHub Pages
3. 在您的网站添加链接指向该地址

### 方式2：子目录集成
1. 在您的网站仓库中创建 `daily_news/` 子目录
2. 将项目文件复制到该目录
3. 修改 GitHub Actions 配置以适应新路径

## 扩展爬虫

### 当前资讯源

项目把内容分成两类，网页顶部用「趣新闻 / 硬新闻」按钮切换：

**🟢 趣新闻（RSS + 社区）**

| 源 | 类型 | 说明 |
|------|------|------|
| Atlas Obscura | RSS | 冷门地点 / 奇异历史 |
| Kottke | RSS | 每日有趣链接合集 |
| Mental Floss | RSS | 冷知识百科 |
| Damn Interesting | RSS | 猎奇历史 / 人物 |
| Neatorama | RSS | 奇怪有趣事物聚合 |
| Bored Panda | RSS | 轻松搞笑图文（带缩略图） |
| 煎蛋 | RSS | 中文趣闻 / 无聊图 |
| xkcd | RSS | 极客漫画 |
| Hacker News | API | 科技 / 长见识，含真实评论数 |
| Reddit（14 个趣闻 subreddit） | API | interestingasfuck / nextfuckinglevel / todayilearned / NotTheOnion / oddlysatisfying / DIY / woahdude …，含真实分数与缩略图 |

**🔴 硬新闻（中文热榜）**

| 源 | 类型 | 说明 |
|------|------|------|
| 微博热搜 | 网页 | 实时热搜 |
| 百度热搜 | 网页 | 实时热榜 |
| 今日头条热榜 | 网页 | 头条热榜 |
| B站热门 | 网页 | 全站热门 |
| 抖音热榜 | 网页 | 实时热榜 |
| 知乎 | API | 知乎热榜（含真实热度值） |

> 注：Reddit 在 GitHub Actions 等云厂商 IP 上常被限流（返回空），本地运行正常；届时由 HN + 趣闻 RSS 兜底。

## 自定义

### 添加新闻源

编辑 `scripts/fetch_news.py` 增源：

```python
- 加 RSS 趣闻源：往 `rss_sources` 字典追加 `'名称': 'RSS_URL'`；
- 加 Reddit 趣闻版块：往 `fetch_reddit()` 里的 `subreddits` 列表追加 subreddit 名；
- 加 HN 类社区：扩展 `fetch_hackernews()`；
- 加硬新闻网页源：往 `web_sources` 列表追加 `{'name': '名称', 'url': '...', 'selector': '.标题选择器'}`。
```

## 许可证

MIT License
