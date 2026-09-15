# 四站热度前十抓取与固定热度排序 Implementation Plan

> 已被 `../specs/2026-09-15-expanded-hot-five-sources-design.md` 的最新范围取代：11 个新增来源，整个项目每站最多 5 条。本文件仅保留为原始实施计划记录。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为钛媒体、36氪、虎嗅和 Phys.org 增加每站最多 10 条的热度新闻抓取，并让首页固定按综合热度排序且不再显示排序按钮。

**Architecture:** 保持现有 `NewsFetcher` 单文件结构，在热榜分派区增加纯解析方法和四个薄网络适配器；解析方法先返回完整候选列表，网络适配器只在成功解析后一次性写入 `news_list`。首页继续使用现有 `hotness` 字段，只移除可变排序状态和控件，不改变综合热度算法。

**Tech Stack:** Python 3、`requests`、BeautifulSoup/lxml、标准库 `unittest`/`unittest.mock`、原生 HTML/CSS/JavaScript。

---

## 文件结构

- Create: `test_hot_sources.py` — 四站解析、异常隔离、数量上限和首页静态契约测试。
- Modify: `scripts/fetch_news.py:43-49,1989-2131` — 四站配置、共享解析辅助函数、纯解析器和网络适配器。
- Modify: `index.html:54-60,269-271,288-296,316-318,369-377,476-483` — 删除排序控件和可变排序逻辑，固定按 `hotness` 排序。
- Create: `scripts/smoke_hot_sources.py` — 只读抓取四站并打印结果，不调用 `save_data()`。

设计依据：`docs/superpowers/specs/2026-09-15-hot-top10-sources-design.md`。

### Task 1: 建立共享热榜解析辅助函数

**Files:**
- Create: `test_hot_sources.py`
- Modify: `scripts/fetch_news.py:2007-2024`

- [ ] **Step 1: 写失败测试，锁定数量解析、风控识别和新闻对象字段**

创建 `test_hot_sources.py`：

```python
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from scripts.fetch_news import NewsFetcher


class HotSourceTests(unittest.TestCase):
    def setUp(self):
        self.fetcher = NewsFetcher()

    def test_parse_metric_supports_chinese_and_english_units(self):
        cases = {
            "39.6万": 396000,
            "1.2亿": 120000000,
            "12.5k": 12500,
            "2m": 2000000,
            "1,234 阅读": 1234,
            "": 0,
            None: 0,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(self.fetcher._parse_metric(raw), expected)

    def test_block_page_detection(self):
        self.assertTrue(self.fetcher._looks_blocked("Checking your connection before proceeding"))
        self.assertTrue(self.fetcher._looks_blocked("请完成验证码 captcha"))
        self.assertFalse(self.fetcher._looks_blocked("<article>正常新闻</article>"))

    def test_build_hot_news_normalizes_fields(self):
        news = self.fetcher._build_hot_news(
            source="测试热榜",
            title="  一条用于测试的有效新闻标题  ",
            url="https://example.com/1",
            hot="1.5万",
            desc="摘要",
            comments="12",
            publish_time="2026-09-15T08:00:00",
        )
        self.assertEqual(news["title"], "一条用于测试的有效新闻标题")
        self.assertEqual(news["views"], 15000)
        self.assertEqual(news["comments"], 12)
        self.assertEqual(news["publish_time"], "2026-09-15T08:00:00")
        self.assertEqual(news["image"], "")
        self.assertIsNone(self.fetcher._build_hot_news("测试", "   "))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认因辅助方法不存在而失败**

Run: `python3 -m unittest test_hot_sources.HotSourceTests -v`

Expected: 3 个测试失败，错误包含 `NewsFetcher object has no attribute '_parse_metric'`、`_looks_blocked` 或 `_build_hot_news`。

- [ ] **Step 3: 写最小共享实现，并让旧 `_hot_append` 复用新闻对象构造**

在 `scripts/fetch_news.py` 的 `_hot_append` 前加入：

```python
    def _parse_metric(self, value):
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return max(0, int(value))

        text = str(value).strip().lower().replace(',', '')
        if not text:
            return 0

        multiplier = 1
        if '亿' in text:
            multiplier = 100000000
        elif '万' in text:
            multiplier = 10000
        elif re.search(r'\bm\b', text) or text.endswith('m'):
            multiplier = 1000000
        elif re.search(r'\bk\b', text) or text.endswith('k'):
            multiplier = 1000

        match = re.search(r'\d+(?:\.\d+)?', text)
        if not match:
            return 0
        return max(0, int(float(match.group()) * multiplier))

    def _looks_blocked(self, text):
        lowered = (text or '').lower()
        markers = (
            'checking your connection',
            'cf-chl-',
            'captcha',
            '验证码',
            '访问过于频繁',
        )
        return any(marker in lowered for marker in markers)

    def _build_hot_news(self, source, title, url='', hot=0, desc='',
                        comments=0, forwards=0, favorites=0,
                        publish_time=None, image=''):
        title = self.clean_title(title or '')
        if not title:
            return None
        if isinstance(publish_time, datetime):
            publish_time = publish_time.isoformat()
        elif publish_time:
            publish_time = str(publish_time)
        else:
            publish_time = datetime.now().isoformat()
        return {
            'id': self.get_hash(title),
            'title': title,
            'source': source,
            'url': url or '',
            'publish_time': publish_time,
            'views': self._parse_metric(hot),
            'comments': self._parse_metric(comments),
            'forwards': self._parse_metric(forwards),
            'favorites': self._parse_metric(favorites),
            'content': desc or '',
            'image': image or '',
        }

    def _extend_hot_items(self, source, items):
        valid_items = [item for item in items if item][:10]
        self.news_list.extend(valid_items)
        print(f'  {source}: parsed {len(valid_items)} hot items')
```

将 `_hot_append` 改成：

```python
    def _hot_append(self, source, title, url='', hot=0, desc='',
                    comments=0, forwards=0, favorites=0):
        news = self._build_hot_news(
            source=source,
            title=title,
            url=url,
            hot=hot,
            desc=desc,
            comments=comments,
            forwards=forwards,
            favorites=favorites,
        )
        if news:
            self.news_list.append(news)
```

- [ ] **Step 4: 运行共享辅助函数测试**

Run: `python3 -m unittest test_hot_sources.HotSourceTests -v`

Expected: `Ran 3 tests` 和 `OK`。

- [ ] **Step 5: 提交共享基础代码**

```bash
git add test_hot_sources.py scripts/fetch_news.py
git commit -m "test: define hot source parsing contracts"
```

### Task 2: 接入钛媒体热门文章前十

**Files:**
- Modify: `test_hot_sources.py`
- Modify: `scripts/fetch_news.py:1985-2131`

- [ ] **Step 1: 写失败测试，锁定页面顺序、数量上限、绝对链接和阅读量**

向 `HotSourceTests` 添加：

```python
    def test_parse_tmt_hot_keeps_first_ten_ranked_articles(self):
        cards = []
        for rank in range(1, 13):
            cards.append(
                '<div class="item">'
                f'<a class="_left" href="/article/{rank}.html">'
                f'<div class="_tit">钛媒体热榜测试新闻标题第{rank}条</div></a>'
                f'<div class="action_reads">{rank}.5万</div>'
                f'<div class="_time">· 9月{rank}日</div>'
                f'<div class="_des">摘要{rank}</div>'
                '</div>'
            )
        result = self.fetcher._parse_tmt_hot(''.join(cards))
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]["title"], "钛媒体热榜测试新闻标题第1条")
        self.assertEqual(result[0]["url"], "https://www.tmtpost.com/article/1.html")
        self.assertEqual(result[0]["views"], 15000)
        first_publish_time = datetime.fromisoformat(result[0]["publish_time"])
        self.assertEqual((first_publish_time.month, first_publish_time.day), (9, 1))
        self.assertEqual(result[-1]["title"], "钛媒体热榜测试新闻标题第10条")

    def test_parse_tmt_hot_rejects_block_page(self):
        self.assertEqual(self.fetcher._parse_tmt_hot("Checking your connection"), [])
```

- [ ] **Step 2: 运行钛媒体测试并确认失败**

Run: `python3 -m unittest test_hot_sources.HotSourceTests.test_parse_tmt_hot_keeps_first_ten_ranked_articles test_hot_sources.HotSourceTests.test_parse_tmt_hot_rejects_block_page -v`

Expected: FAIL，错误包含 `_parse_tmt_hot` 不存在。

- [ ] **Step 3: 实现钛媒体纯解析器和网络适配器**

在热榜方法区加入：

```python
    def _parse_tmt_publish_time(self, text):
        match = re.search(r'(\d{1,2})月(\d{1,2})日', text or '')
        if not match:
            return None
        now = datetime.now()
        try:
            publish_time = datetime(now.year, int(match.group(1)), int(match.group(2)))
        except ValueError:
            return None
        if publish_time > now + timedelta(days=1):
            publish_time = publish_time.replace(year=now.year - 1)
        return publish_time

    def _parse_tmt_hot(self, html):
        if self._looks_blocked(html):
            return []
        soup = BeautifulSoup(html, 'lxml')
        items = []
        seen_urls = set()
        for card in soup.select('.item'):
            title_node = card.select_one('._tit')
            link_node = card.select_one('a._left[href], a[href]')
            if not title_node or not link_node:
                continue
            url = urljoin('https://www.tmtpost.com/', link_node.get('href', ''))
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            views_node = card.select_one('.action_reads')
            desc_node = card.select_one('._des, .item-des, p')
            time_node = card.select_one('._time, time')
            publish_time = None
            if time_node:
                publish_time = time_node.get('datetime') or self._parse_tmt_publish_time(
                    time_node.get_text(' ', strip=True)
                )
            news = self._build_hot_news(
                source='钛媒体',
                title=title_node.get_text(' ', strip=True),
                url=url,
                hot=views_node.get_text(' ', strip=True) if views_node else 0,
                desc=desc_node.get_text(' ', strip=True) if desc_node else '',
                publish_time=publish_time,
            )
            if news:
                items.append(news)
            if len(items) == 10:
                break
        return items

    def _hot_tmt(self):
        url = 'https://www.tmtpost.com/hot'
        response = self.get_with_retry(url)
        if not response:
            return
        response.encoding = 'utf-8'
        self._extend_hot_items('钛媒体', self._parse_tmt_hot(response.text))
```

- [ ] **Step 4: 运行钛媒体测试和已有共享测试**

Run: `python3 -m unittest test_hot_sources -v`

Expected: `Ran 5 tests` 和 `OK`。

- [ ] **Step 5: 提交钛媒体适配器**

```bash
git add test_hot_sources.py scripts/fetch_news.py
git commit -m "feat: fetch TMTPost hot top ten"
```

### Task 3: 接入 36氪 48 小时人气榜前十

**Files:**
- Modify: `test_hot_sources.py`
- Modify: `scripts/fetch_news.py:1985-2131`

- [ ] **Step 1: 写失败测试，确保只读 `topList` 并按 `rank` 排序**

向 `HotSourceTests` 添加：

```python
    def test_parse_36kr_uses_top_list_and_rank(self):
        top_list = []
        for rank in range(12, 0, -1):
            top_list.append({
                "rank": rank,
                "itemId": str(1000 + rank),
                "widgetTitle": f"36氪人气榜测试新闻标题第{rank}条",
                "summary": f"摘要{rank}",
                "publishTime": 1789430400000 + rank,
                "statHot": f"{rank}.5万",
                "widgetImage": f"https://img.example.com/{rank}.jpg",
            })
        payload = {
            "data": {
                "topList": top_list,
                "hotList": [{"rank": 0, "widgetTitle": "不得混入的综合榜文章"}],
                "collectList": [{"rank": 0, "widgetTitle": "不得混入的收藏榜文章"}],
            }
        }
        result = self.fetcher._parse_36kr_hot(payload)
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]["title"], "36氪人气榜测试新闻标题第1条")
        self.assertEqual(result[0]["url"], "https://36kr.com/p/1001")
        self.assertEqual(result[0]["views"], 15000)
        self.assertEqual(result[-1]["title"], "36氪人气榜测试新闻标题第10条")
        self.assertNotIn("综合榜", " ".join(item["title"] for item in result))
```

- [ ] **Step 2: 运行 36氪测试并确认失败**

Run: `python3 -m unittest test_hot_sources.HotSourceTests.test_parse_36kr_uses_top_list_and_rank -v`

Expected: FAIL，错误包含 `_parse_36kr_hot` 不存在。

- [ ] **Step 3: 实现 36氪纯解析器和 POST 网络适配器**

在热榜方法区加入：

```python
    def _parse_36kr_hot(self, payload):
        items = ((payload or {}).get('data') or {}).get('topList') or []
        ranked = sorted(
            items,
            key=lambda item: self._parse_metric(item.get('rank')) or 999999,
        )
        result = []
        seen_ids = set()
        for item in ranked:
            item_id = str(item.get('itemId') or '').strip()
            title = item.get('widgetTitle') or ''
            if not item_id or item_id in seen_ids or not title:
                continue
            seen_ids.add(item_id)
            publish_time = None
            raw_time = item.get('publishTime')
            if raw_time:
                try:
                    publish_time = datetime.fromtimestamp(float(raw_time) / 1000)
                except (TypeError, ValueError, OSError):
                    publish_time = None
            news = self._build_hot_news(
                source='36氪',
                title=title,
                url=f'https://36kr.com/p/{item_id}',
                hot=item.get('statHot') or 0,
                desc=item.get('summary') or '',
                publish_time=publish_time,
                image=item.get('widgetImage') or '',
            )
            if news:
                result.append(news)
            if len(result) == 10:
                break
        return result

    def _hot_36kr(self):
        url = 'https://gateway.36kr.com/api/mis/x/rank/list'
        payload = {
            'partner_id': 'web',
            'timestamp': int(time.time() * 1000),
            'param': {'siteId': 1, 'platformId': 2},
        }
        response = self.session.post(
            url,
            json=payload,
            headers={'Referer': 'https://36kr.com/hot-list/catalog'},
            timeout=self.timeout,
        )
        response.raise_for_status()
        self._extend_hot_items('36氪', self._parse_36kr_hot(response.json()))
```

- [ ] **Step 4: 运行全部解析测试**

Run: `python3 -m unittest test_hot_sources -v`

Expected: `Ran 6 tests` 和 `OK`。

- [ ] **Step 5: 提交 36氪适配器**

```bash
git add test_hot_sources.py scripts/fetch_news.py
git commit -m "feat: fetch 36Kr popularity top ten"
```

### Task 4: 接入 Phys.org 过去一天排行前十

**Files:**
- Modify: `test_hot_sources.py`
- Modify: `scripts/fetch_news.py:1985-2131`

- [ ] **Step 1: 写失败测试，锁定排行顺序、去重和风控页拒绝**

向 `HotSourceTests` 添加：

```python
    def test_parse_phys_rank_keeps_page_order_and_limit(self):
        articles = []
        for rank in range(1, 13):
            articles.append(
                '<article class="sorted-article">'
                f'<h3><a href="/news/2026-09-test-{rank}.html">'
                f'Phys org ranked science headline number {rank}</a></h3>'
                f'<p>Science summary number {rank} with enough detail.</p>'
                f'<time datetime="2026-09-15T0{rank % 10}:00:00+00:00"></time>'
                '</article>'
            )
        result = self.fetcher._parse_phys_hot(''.join(articles))
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]["url"], "https://phys.org/news/2026-09-test-1.html")
        self.assertEqual(result[-1]["title"], "Phys org ranked science headline number 10")
        self.assertTrue(all(item["views"] == 0 for item in result))

    def test_parse_phys_rank_rejects_cloudflare_page(self):
        self.assertEqual(self.fetcher._parse_phys_hot('<div id="cf-chl-test">Checking your connection</div>'), [])
```

- [ ] **Step 2: 运行 Phys.org 测试并确认失败**

Run: `python3 -m unittest test_hot_sources.HotSourceTests.test_parse_phys_rank_keeps_page_order_and_limit test_hot_sources.HotSourceTests.test_parse_phys_rank_rejects_cloudflare_page -v`

Expected: FAIL，错误包含 `_parse_phys_hot` 不存在。

- [ ] **Step 3: 实现 Phys.org 纯解析器和网络适配器**

在热榜方法区加入：

```python
    def _parse_phys_hot(self, html):
        if self._looks_blocked(html):
            return []
        soup = BeautifulSoup(html, 'lxml')
        links = []
        selectors = (
            '.sorted-article-content h3 a[href]',
            '.sorted-article h3 a[href]',
            'article h3 a[href]',
        )
        for selector in selectors:
            links = soup.select(selector)
            if links:
                break

        result = []
        seen_urls = set()
        for link_node in links:
            url = urljoin('https://phys.org/', link_node.get('href', ''))
            if not url.startswith('https://phys.org/') or url in seen_urls:
                continue
            seen_urls.add(url)
            container = link_node.find_parent('article')
            if container is None:
                container = link_node.find_parent(
                    'div', class_=re.compile(r'sorted-article')
                )
            if container is None:
                container = link_node.parent
            desc_node = container.select_one('p') if container else None
            time_node = container.select_one('time') if container else None
            news = self._build_hot_news(
                source='Phys.org',
                title=link_node.get_text(' ', strip=True),
                url=url,
                desc=desc_node.get_text(' ', strip=True) if desc_node else '',
                publish_time=time_node.get('datetime') if time_node else None,
            )
            if news:
                result.append(news)
            if len(result) == 10:
                break
        return result

    def _hot_phys(self):
        url = 'https://phys.org/sort/rank/1d/'
        response = self.get_with_retry(url)
        if not response:
            return
        response.encoding = response.apparent_encoding or 'utf-8'
        self._extend_hot_items('Phys.org', self._parse_phys_hot(response.text))
```

- [ ] **Step 4: 运行全部解析测试**

Run: `python3 -m unittest test_hot_sources -v`

Expected: `Ran 8 tests` 和 `OK`。

- [ ] **Step 5: 提交 Phys.org 适配器**

```bash
git add test_hot_sources.py scripts/fetch_news.py
git commit -m "feat: fetch Phys.org daily ranked top ten"
```

### Task 5: 接入虎嗅公开互动热度前十

**Files:**
- Modify: `test_hot_sources.py`
- Modify: `scripts/fetch_news.py:1985-2131`

- [ ] **Step 1: 写失败测试，确保按互动数而非页面时间排序且不补最新文章**

向 `HotSourceTests` 添加：

```python
    def test_parse_huxiu_sorts_only_items_with_public_interactions(self):
        articles = []
        for rank in range(1, 13):
            interactions = 13 - rank
            articles.append(
                '<article class="article-item">'
                f'<a class="article-title" href="/article/{2000 + rank}.html">'
                f'虎嗅互动热度测试新闻标题第{rank}条</a>'
                f'<span class="comment-count">{interactions}</span>'
                f'<p>虎嗅测试摘要{rank}</p>'
                '</article>'
            )
        articles.append(
            '<article class="article-item">'
            '<a class="article-title" href="/article/9999.html">最新但没有互动指标的新闻标题</a>'
            '</article>'
        )
        result = self.fetcher._parse_huxiu_hot(''.join(articles))
        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]["comments"], 12)
        self.assertEqual(result[-1]["comments"], 3)
        self.assertNotIn("最新但没有互动指标", " ".join(item["title"] for item in result))

    def test_parse_huxiu_does_not_fall_back_on_missing_metrics(self):
        html = (
            '<article><a href="/article/1.html">只有发布时间没有互动指标的有效新闻标题</a>'
            '<time>1分钟前</time></article>'
        )
        self.assertEqual(self.fetcher._parse_huxiu_hot(html), [])
```

- [ ] **Step 2: 运行虎嗅测试并确认失败**

Run: `python3 -m unittest test_hot_sources.HotSourceTests.test_parse_huxiu_sorts_only_items_with_public_interactions test_hot_sources.HotSourceTests.test_parse_huxiu_does_not_fall_back_on_missing_metrics -v`

Expected: FAIL，错误包含 `_parse_huxiu_hot` 不存在。

- [ ] **Step 3: 实现虎嗅互动指标解析和网络适配器**

在热榜方法区加入：

```python
    def _parse_huxiu_hot(self, html):
        if self._looks_blocked(html):
            return []
        soup = BeautifulSoup(html, 'lxml')
        candidates = []
        seen_urls = set()
        for link_node in soup.select('a[href*="/article/"]'):
            href = link_node.get('href', '')
            if not re.search(r'/article/\d+\.html', href):
                continue
            url = urljoin('https://www.huxiu.com/', href)
            if url in seen_urls:
                continue
            container = link_node.find_parent(['article', 'li'])
            if container is None:
                container = link_node.find_parent(
                    'div', class_=re.compile(r'article|item|card', re.I)
                )
            if container is None:
                continue
            metric_node = container.select_one(
                '[class*="comment"], [class*="reply"], '
                '[class*="interact"], [class*="hot-num"]'
            )
            if metric_node is None:
                continue
            seen_urls.add(url)
            desc_node = container.select_one('p')
            time_node = container.select_one('time')
            news = self._build_hot_news(
                source='虎嗅',
                title=link_node.get_text(' ', strip=True),
                url=url,
                comments=self._parse_metric(metric_node.get_text(' ', strip=True)),
                desc=desc_node.get_text(' ', strip=True) if desc_node else '',
                publish_time=time_node.get('datetime') if time_node else None,
            )
            if news:
                candidates.append(news)
        return sorted(
            candidates,
            key=lambda item: item['comments'],
            reverse=True,
        )[:10]

    def _hot_huxiu(self):
        url = 'https://www.huxiu.com/article/'
        response = self.get_with_retry(url)
        if not response:
            return
        response.encoding = 'utf-8'
        self._extend_hot_items('虎嗅', self._parse_huxiu_hot(response.text))
```

- [ ] **Step 4: 运行全部解析测试**

Run: `python3 -m unittest test_hot_sources -v`

Expected: `Ran 10 tests` 和 `OK`。

- [ ] **Step 5: 提交虎嗅适配器**

```bash
git add test_hot_sources.py scripts/fetch_news.py
git commit -m "feat: rank Huxiu articles by public interactions"
```

### Task 6: 集成四站分派并验证单来源失败隔离

**Files:**
- Modify: `test_hot_sources.py`
- Modify: `scripts/fetch_news.py:43-49,1989-2005`

- [ ] **Step 1: 写失败测试，锁定四站配置、分派和异常隔离**

向 `HotSourceTests` 添加：

```python
    def test_four_hot_sources_are_configured(self):
        names = {source["name"] for source in self.fetcher.web_sources}
        self.assertTrue({"钛媒体", "36氪", "虎嗅", "Phys.org"}.issubset(names))

    def test_fetch_hotlist_isolates_one_source_failure(self):
        with patch.object(self.fetcher, "_hot_tmt", side_effect=RuntimeError("blocked")):
            self.fetcher.fetch_hotlist({"name": "钛媒体"})
        self.assertEqual(self.fetcher.news_list, [])

    def test_fetch_hotlist_dispatches_new_source(self):
        with patch.object(self.fetcher, "_hot_phys") as handler:
            self.fetcher.fetch_hotlist({"name": "Phys.org"})
        handler.assert_called_once_with()
```

- [ ] **Step 2: 运行集成测试并确认配置或分派失败**

Run: `python3 -m unittest test_hot_sources.HotSourceTests.test_four_hot_sources_are_configured test_hot_sources.HotSourceTests.test_fetch_hotlist_isolates_one_source_failure test_hot_sources.HotSourceTests.test_fetch_hotlist_dispatches_new_source -v`

Expected: 至少一个测试 FAIL，因为四站尚未加入 `web_sources` 或 `handlers`。

- [ ] **Step 3: 将四站加入配置与分派表**

把 `web_sources` 扩展为：

```python
        self.web_sources = [
            {'name': '微博热搜', 'url': 'https://s.weibo.com/top/summary?cate=realtimehot', 'selector': 'td.td-02 a'},
            {'name': '百度热搜', 'url': 'https://top.baidu.com/board?tab=realtime', 'selector': '.c-single-text-ellipsis, .content_1YyZf'},
            {'name': '今日头条热榜', 'url': 'https://www.toutiao.com/', 'selector': '.title'},
            {'name': 'B站热门', 'url': 'https://www.bilibili.com/v/popular/rank/all', 'selector': '.info .title'},
            {'name': '抖音热榜', 'url': 'https://www.douyin.com/hot', 'selector': '.title'},
            {'name': '钛媒体', 'url': 'https://www.tmtpost.com/hot'},
            {'name': '36氪', 'url': 'https://36kr.com/hot-list/catalog'},
            {'name': '虎嗅', 'url': 'https://www.huxiu.com/article/'},
            {'name': 'Phys.org', 'url': 'https://phys.org/sort/rank/1d/'},
        ]
```

把 `fetch_hotlist` 的 `handlers` 扩展为：

```python
        handlers = {
            '微博热搜': self._hot_weibo,
            '百度热搜': self._hot_baidu,
            '今日头条热榜': self._hot_toutiao,
            'B站热门': self._hot_bilibili,
            '抖音热榜': self._hot_douyin,
            '钛媒体': self._hot_tmt,
            '36氪': self._hot_36kr,
            '虎嗅': self._hot_huxiu,
            'Phys.org': self._hot_phys,
        }
```

- [ ] **Step 4: 运行全部单元测试和语法检查**

Run: `python3 -m unittest test_hot_sources -v`

Expected: `Ran 13 tests` 和 `OK`。

Run: `python3 -m py_compile scripts/fetch_news.py test_hot_sources.py`

Expected: 无输出，退出码 0。

- [ ] **Step 5: 提交四站集成**

```bash
git add test_hot_sources.py scripts/fetch_news.py
git commit -m "feat: register four hot news sources"
```

### Task 7: 删除排序按钮并固定按综合热度排序

**Files:**
- Modify: `test_hot_sources.py`
- Modify: `index.html:54-60,269-271,288-296,316-318,369-377,476-483`

- [ ] **Step 1: 写失败的首页静态契约测试**

向 `HotSourceTests` 添加：

```python
    def test_index_has_no_sort_controls_and_uses_hotness(self):
        html = Path("index.html").read_text(encoding="utf-8")
        self.assertNotIn('class="sort-buttons"', html)
        self.assertNotIn("data-sort=", html)
        self.assertNotIn("currentSort", html)
        self.assertNotIn(".sort-buttons", html)
        self.assertIn("Number(b.hotness)", html)
        self.assertIn("Number(a.hotness)", html)

    def test_index_keeps_news_card_statistics(self):
        html = Path("index.html").read_text(encoding="utf-8")
        for label in ("热度:", "浏览:", "评论:", "转发:", "收藏:"):
            self.assertIn(label, html)
```

- [ ] **Step 2: 运行首页测试并确认失败**

Run: `python3 -m unittest test_hot_sources.HotSourceTests.test_index_has_no_sort_controls_and_uses_hotness test_hot_sources.HotSourceTests.test_index_keeps_news_card_statistics -v`

Expected: 第一个测试 FAIL，第二个测试 PASS。

- [ ] **Step 3: 删除排序控件、孤立样式和事件监听，固定比较字段**

在 `index.html` 中执行以下最小修改：

1. 删除完整的 `.sort-buttons` CSS 规则。
2. 将移动端规则：

```css
            .sort-buttons, .view-buttons {
                justify-content: center;
            }
```

改为：

```css
            .view-buttons {
                justify-content: center;
            }
```

3. 删除 `<div class="sort-buttons">` 及其五个按钮。
4. 删除 `let currentSort = 'hotness';`。
5. 将排序比较器改为：

```javascript
            // 固定按综合热度降序，同分按发布时间新→旧
            const sorted = catNews.slice().sort((a, b) => {
                const d = (Number(b.hotness) || 0) - (Number(a.hotness) || 0);
                if (d !== 0) return d;
                return (Date.parse(b.publish_time) || 0) - (Date.parse(a.publish_time) || 0);
            });
```

6. 删除完整的 `document.querySelectorAll('.sort-buttons button')` 事件监听块。

- [ ] **Step 4: 运行首页契约测试与全部单元测试**

Run: `python3 -m unittest test_hot_sources -v`

Expected: `Ran 15 tests` 和 `OK`。

- [ ] **Step 5: 提交首页修改**

```bash
git add test_hot_sources.py index.html
git commit -m "feat: keep only fixed hotness ordering"
```

### Task 8: 增加不写新闻数据的四站网络烟雾脚本

**Files:**
- Modify: `test_hot_sources.py`
- Create: `scripts/smoke_hot_sources.py`

- [ ] **Step 1: 写失败测试，确保烟雾脚本存在且不调用保存方法**

向 `HotSourceTests` 添加：

```python
    def test_smoke_script_is_read_only(self):
        source = Path("scripts/smoke_hot_sources.py").read_text(encoding="utf-8")
        self.assertNotIn("save_data(", source)
        self.assertNotIn(".run()", source)
        for name in ("钛媒体", "36氪", "虎嗅", "Phys.org"):
            self.assertIn(name, source)
```

- [ ] **Step 2: 运行烟雾脚本契约测试并确认文件不存在**

Run: `python3 -m unittest test_hot_sources.HotSourceTests.test_smoke_script_is_read_only -v`

Expected: ERROR，包含 `FileNotFoundError: scripts/smoke_hot_sources.py`。

- [ ] **Step 3: 创建只读烟雾脚本**

创建 `scripts/smoke_hot_sources.py`：

```python
#!/usr/bin/env python3
"""Read-only live smoke check for the four hot-news sources."""

from fetch_news import NewsFetcher


SOURCES = (
    {'name': '钛媒体'},
    {'name': '36氪'},
    {'name': '虎嗅'},
    {'name': 'Phys.org'},
)


def main():
    fetcher = NewsFetcher()
    for source in SOURCES:
        before = len(fetcher.news_list)
        fetcher.fetch_hotlist(source)
        items = fetcher.news_list[before:]
        print(f'{source["name"]}: {len(items)} items')
        for index, item in enumerate(items, 1):
            print(f'  {index:02d}. {item["title"]} | {item["url"]}')
        if len(items) > 10:
            raise RuntimeError(f'{source["name"]} returned more than 10 items')


if __name__ == '__main__':
    main()
```

- [ ] **Step 4: 运行烟雾脚本静态契约测试**

Run: `python3 -m unittest test_hot_sources.HotSourceTests.test_smoke_script_is_read_only -v`

Expected: `Ran 1 test` 和 `OK`。

- [ ] **Step 5: 提交只读烟雾脚本**

```bash
git add test_hot_sources.py scripts/smoke_hot_sources.py
git commit -m "test: add read-only hot source smoke check"
```

### Task 9: 完整验证，不覆盖 `data/news.json`

**Files:**
- Verify: `scripts/fetch_news.py`
- Verify: `scripts/smoke_hot_sources.py`
- Verify: `test_hot_sources.py`
- Verify: `index.html`
- Verify unchanged: `data/news.json`

- [ ] **Step 1: 记录现有新闻数据校验值**

Run: `shasum -a 256 data/news.json`

Expected: 输出一个 SHA-256 值；保存该值用于 Step 5 对照。

- [ ] **Step 2: 运行全部离线单元测试**

Run: `python3 -m unittest test_hot_sources -v`

Expected: `Ran 16 tests` 和 `OK`。

- [ ] **Step 3: 运行 Python 语法检查**

Run: `python3 -m py_compile scripts/fetch_news.py scripts/smoke_hot_sources.py test_hot_sources.py`

Expected: 无输出，退出码 0。

- [ ] **Step 4: 运行四站只读网络烟雾测试**

Run: `python3 scripts/smoke_hot_sources.py`

Expected: 四个来源各输出 `0` 至 `10` 条；零条必须伴随抓取失败或解析为零的日志，不允许出现 Traceback。若站点风控导致零条，将该站记为当前网络风险，不以最新新闻补位。

- [ ] **Step 5: 再次核对新闻数据未改变**

Run: `shasum -a 256 data/news.json`

Expected: SHA-256 与 Step 1 完全一致。

- [ ] **Step 6: 检查差异质量和工作区状态**

Run: `git diff --check`

Expected: 无输出，退出码 0。

Run: `git status --short --branch`

Expected: 无未提交文件；分支仅显示相对远端 ahead 状态。

## 自检结果

- 设计中的四个来源、每站上限 10 条、虎嗅互动代理、不以最新补位、单来源失败隔离、前端固定热度排序、保留卡片统计和不覆盖新闻数据均有对应任务。
- 所有新增方法名在测试与实现步骤中一致：`_parse_metric`、`_looks_blocked`、`_build_hot_news`、`_extend_hot_items`、`_parse_tmt_hot`、`_parse_36kr_hot`、`_parse_phys_hot`、`_parse_huxiu_hot`。
- 计划不增加依赖，不改目录结构，不修改综合热度权重，不调用完整 `run()` 或 `save_data()` 做验证。
