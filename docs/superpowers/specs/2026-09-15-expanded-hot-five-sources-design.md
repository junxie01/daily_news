# 扩展新闻源与每站热度前五设计

日期：2026-09-15  
状态：用户已确认，已实现并完成离线与只读网络验证

## 范围

在原有热榜与 RSS 来源基础上，接入钛媒体、36氪、虎嗅、Phys.org、WIRED、The Verge、NPR、Security Affairs、FreeBuf、Scientific American 和 The Guardian。整个项目统一限制为每个网站最多保留 5 条。

本设计取代 `2026-09-15-hot-top10-sources-design.md` 中“四站、每站十条”的数量和来源范围；其余不依赖 AI、不改变综合热度权重、单站失败不阻断全局的边界继续有效。

## 热度口径

- 钛媒体、36氪、Phys.org、The Verge、Security Affairs、The Guardian：按站点明确提供的热门、排行或最多阅读列表顺序取前五。
- WIRED：从当前文章页公开的 Most Popular 模块取前五；首页文章只作为进入该模块的入口，不冒充热门条目。
- Scientific American：只取带 Popular 标记的文章卡片。
- 虎嗅、FreeBuf：只在页面公开互动数可解析时按互动数排序；无指标、风控页或解析失败时跳过，不用最新文章补位。
- NPR：该站没有稳定公开的 Most Viewed 页面，采用官方首页或官方 Top Stories RSS 的编辑排序，并在实现和日志中保持该口径，不称为浏览量热榜。
- 原有 RSS、Hacker News、Reddit、知乎及中文热榜也统一限制为每站五条；Reddit 在现有趣闻 subreddit 候选中按公开分数选全站前五。

## 实现与验证

- 保持现有单文件抓取器结构，不增加依赖。
- 每个解析器先返回已校验、去重的候选，再一次性写入 `news_list`。
- 新增离线最小 HTML/JSON 测试，覆盖榜单顺序、互动排序、风控页和五条上限。
- 首页删除全部排序按钮和可变排序状态，固定按 `hotness` 降序；新闻卡片统计保留。
- 网络烟雾测试只打印结果，不调用 `save_data()`，不改写 `data/news.json`。
