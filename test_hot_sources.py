import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.fetch_news import NewsFetcher


class HotSourceTests(unittest.TestCase):
    def setUp(self):
        self.fetcher = NewsFetcher()

    def test_metric_parser_supports_common_units(self):
        cases = {
            "39.6万": 396000,
            "1.2亿": 120000000,
            "12.5k": 12500,
            "2m": 2000000,
            "1,234 阅读": 1234,
            "349.66": 349,
            "": 0,
            None: 0,
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(self.fetcher._parse_metric(raw), expected)

    def test_rss_source_is_capped_at_five(self):
        items = "".join(
            f"<item><title>RSS 新闻 {i}</title><link>https://example.com/{i}</link></item>"
            for i in range(6)
        )
        response = Mock(text=f"<rss><channel>{items}</channel></rss>", encoding="utf-8")
        with patch.object(self.fetcher, "get_with_retry", return_value=response):
            self.fetcher.fetch_rss_feed("测试 RSS", "https://example.com/rss")
        self.assertEqual(len(self.fetcher.news_list), 5)

    def test_tmtpost_parser_uses_hot_page_order_and_cap(self):
        cards = "".join(
            f"""
            <div class="item">
              <a class="_left" href="/article/{i}"><span class="_tit">钛媒体热门 {i}</span></a>
              <span class="action_reads">{10 - i}万</span>
              <p class="desc">摘要 {i}</p>
            </div>
            """
            for i in range(6)
        )
        parsed = self.fetcher._parse_tmtpost(cards)
        self.assertEqual([item["title"] for item in parsed], [f"钛媒体热门 {i}" for i in range(5)])
        self.assertEqual(parsed[0]["views"], 100000)
        self.assertEqual(parsed[0]["url"], "https://www.tmtpost.com/article/0")

    def test_36kr_parser_only_uses_ranked_top_list(self):
        payload = {
            "data": {
                "topList": [
                    {
                        "rank": rank,
                        "itemId": 100 + rank,
                        "widgetTitle": f"36氪人气榜 {rank}",
                        "summary": f"摘要 {rank}",
                        "statHot": str(200 - rank),
                        "publishTime": 1789430619865,
                    }
                    for rank in range(6, 0, -1)
                ],
                "hotList": [{"rank": 1, "widgetTitle": "不应采用的综合榜"}],
            }
        }
        parsed = self.fetcher._parse_36kr(payload)
        self.assertEqual([item["title"] for item in parsed], [f"36氪人气榜 {i}" for i in range(1, 6)])
        self.assertEqual(parsed[0]["url"], "https://36kr.com/p/101")

    def test_expanded_hot_sources_are_configured(self):
        expected = {
            "钛媒体", "36氪", "虎嗅", "Phys.org", "WIRED", "The Verge",
            "NPR", "Security Affairs", "FreeBuf", "Scientific American", "The Guardian",
        }
        configured = {source["name"] for source in self.fetcher.web_sources}
        self.assertTrue(expected.issubset(configured))

    def test_huxiu_parser_sorts_only_cards_with_public_metrics(self):
        html = "".join(
            f"""
            <article><h3><a href="/article/{i}.html">虎嗅热点文章 {i}</a></h3>
            <span>{score} 阅读</span><span>{i} 收藏</span></article>
            """
            for i, score in enumerate([20, 80, 40, 100, 60, 10])
        )
        parsed = self.fetcher._parse_huxiu(html)
        self.assertEqual([item["title"] for item in parsed], [
            "虎嗅热点文章 3", "虎嗅热点文章 1", "虎嗅热点文章 4",
            "虎嗅热点文章 2", "虎嗅热点文章 0",
        ])

    def test_huxiu_api_parser_sorts_candidate_pool_by_interactions(self):
        payload = {'success': True, 'data': {'dataList': [
            {
                'aid': i, 'title': f'虎嗅 API 候选 {i}', 'summary': f'摘要 {i}',
                'dateline': 1789476000 + i, 'pic_path': f'https://img.example/{i}.jpg',
                'count_info': {'viewnum': views, 'commentnum': i, 'favtimes': i, 'sharetimes': i},
            }
            for i, views in enumerate([10, 80, 40, 100, 60, 20])
        ]}}
        parsed = self.fetcher._parse_huxiu_payload(payload)
        self.assertEqual([item['title'] for item in parsed], [
            '虎嗅 API 候选 3', '虎嗅 API 候选 1', '虎嗅 API 候选 4',
            '虎嗅 API 候选 2', '虎嗅 API 候选 5',
        ])
        self.assertEqual(parsed[0]['url'], 'https://www.huxiu.com/article/3.html')

    def test_phys_parser_preserves_rank_last_day_order(self):
        html = "".join(
            f'<article class="sorted-article"><h3><a href="/news/2026-09-story-{i}.html">Phys ranked story {i}</a></h3></article>'
            for i in range(6)
        )
        parsed = self.fetcher._parse_phys_org(html)
        self.assertEqual([item["title"] for item in parsed], [f"Phys ranked story {i}" for i in range(5)])

    def test_wired_parser_uses_article_most_popular_module(self):
        html = self._ranked_fixture("Most Popular", "/story/wired-", "WIRED popular")
        parsed = self.fetcher._parse_wired_article(html)
        self.assertEqual([item["title"] for item in parsed], [f"WIRED popular {i}" for i in range(5)])

    def test_verge_parser_uses_most_popular_section(self):
        html = self._ranked_fixture("Most Popular", "/news/verge-", "Verge popular")
        parsed = self.fetcher._parse_the_verge(html)
        self.assertEqual([item["title"] for item in parsed], [f"Verge popular {i}" for i in range(5)])

    def test_npr_parser_uses_editorial_top_stories(self):
        html = self._ranked_fixture("Top Stories", "/2026/09/15/npr-", "NPR top story")
        parsed = self.fetcher._parse_npr(html)
        self.assertEqual([item["title"] for item in parsed], [f"NPR top story {i}" for i in range(5)])

    def test_npr_parser_accepts_official_top_stories_rss(self):
        rss = "<rss><channel>" + "".join(
            f"<item><title>NPR RSS {i}</title><link>https://www.npr.org/{i}</link><description>摘要</description></item>"
            for i in range(6)
        ) + "</channel></rss>"
        parsed = self.fetcher._parse_npr(rss)
        self.assertEqual([item["title"] for item in parsed], [f"NPR RSS {i}" for i in range(5)])

    def test_security_affairs_parser_uses_most_popular_section(self):
        html = self._ranked_fixture("most popular", "/2026/09/security-", "Security popular")
        parsed = self.fetcher._parse_security_affairs(html)
        self.assertEqual([item["title"] for item in parsed], [f"Security popular {i}" for i in range(5)])

    def test_freebuf_parser_sorts_by_public_interactions(self):
        html = "".join(
            f"""
            <article><h3><a href="/articles/web/{i}.html">FreeBuf security article {i}</a></h3>
            <span>{views}围观</span><span>{i}收藏</span><span>{i}喜欢</span></article>
            """
            for i, views in enumerate([10, 80, 40, 100, 60, 20])
        )
        parsed = self.fetcher._parse_freebuf(html)
        self.assertEqual([item["title"] for item in parsed], [
            "FreeBuf security article 3", "FreeBuf security article 1",
            "FreeBuf security article 4", "FreeBuf security article 2",
            "FreeBuf security article 5",
        ])

    def test_freebuf_api_parser_keeps_hot_list_order_and_metrics(self):
        payload = {'data': {'list': [
            {
                'post_title': f'FreeBuf API hot {i}',
                'url': f'/articles/web/{i}.html',
                'read_count': 100 - i,
                'comment_num': i,
                'favorite': i + 1,
                'like': i + 2,
                'content': f'摘要 {i}',
                'post_date': '2026-09-15 08:00:00',
            }
            for i in range(6)
        ]}}
        parsed = self.fetcher._parse_freebuf_payload(payload)
        self.assertEqual([item['title'] for item in parsed], [f'FreeBuf API hot {i}' for i in range(5)])
        self.assertEqual(parsed[0]['views'], 100)
        self.assertEqual(parsed[0]['favorites'], 3)

    def test_scientific_american_parser_requires_popular_cards(self):
        popular = "".join(
            f'<div class="story-card"><span>Popular</span><a href="/article/science-{i}/">Scientific popular story {i}</a></div>'
            for i in range(6)
        )
        html = '<article><h3><a href="/article/latest/">Latest but not popular</a></h3></article>' + popular
        parsed = self.fetcher._parse_scientific_american(html)
        self.assertEqual([item["title"] for item in parsed], [f"Scientific popular story {i}" for i in range(5)])

    def test_guardian_parser_uses_most_read_order(self):
        cards = "".join(
            f'<li><a href="/world/2026/sep/15/story-{i}" aria-label="Guardian most read {i}"></a><h3>Guardian most read {i}</h3></li>'
            for i in range(6)
        )
        html = f'<section><h2>Most read across The Guardian</h2><ol>{cards}</ol></section>'
        parsed = self.fetcher._parse_the_guardian(html)
        self.assertEqual([item["title"] for item in parsed], [f"Guardian most read {i}" for i in range(5)])

    def test_security_affairs_parser_accepts_h5_ranked_links(self):
        cards = "".join(
            f'<div><h5><a href="/2026/09/security-{i}.html">Security h5 popular {i}</a></h5></div>'
            for i in range(6)
        )
        parsed = self.fetcher._parse_security_affairs(f'<section><h2>most popular</h2>{cards}</section>')
        self.assertEqual([item['title'] for item in parsed], [f'Security h5 popular {i}' for i in range(5)])

    def test_block_pages_produce_no_ranked_items(self):
        blocked = "<html><title>Just a moment...</title><p>Checking your browser before accessing</p></html>"
        self.assertEqual(self.fetcher._parse_the_verge(blocked), [])
        self.assertEqual(self.fetcher._parse_huxiu(blocked), [])
        normal_large_page = self._ranked_fixture(
            "Most read across The Guardian", "/world/story-", "Guardian story"
        ) + (" captcha-script " + "x" * 100000)
        self.assertEqual(len(self.fetcher._parse_the_guardian(normal_large_page)), 5)

    def test_hacker_news_is_capped_at_five(self):
        now = int(datetime.now().timestamp())

        def fake_get(url, timeout=None):
            response = Mock()
            if url.endswith('topstories.json'):
                response.json.return_value = list(range(6))
            else:
                story_id = int(url.rsplit('/', 1)[-1].split('.')[0])
                response.json.return_value = {
                    'title': f'Hacker News {story_id}', 'time': now,
                    'score': 100 - story_id, 'descendants': story_id,
                }
            return response

        with patch.object(self.fetcher, 'get_with_retry', side_effect=fake_get), patch('time.sleep'):
            self.fetcher.fetch_hackernews()
        self.assertEqual(len(self.fetcher.news_list), 5)

    def test_reddit_is_capped_to_five_across_all_subreddits(self):
        now = datetime.now().timestamp()

        def fake_get(url, timeout=None):
            sub = url.split('/r/', 1)[1].split('/', 1)[0]
            score = len(sub)
            response = Mock()
            response.json.return_value = {'data': {'children': [{'data': {
                'title': f'Reddit story from {sub}', 'created_utc': now,
                'subreddit': sub, 'permalink': f'/r/{sub}/comments/1',
                'score': score, 'num_comments': score,
            }}]}}
            return response

        with patch.object(self.fetcher, 'get_with_retry', side_effect=fake_get):
            self.fetcher.fetch_reddit()
        self.assertEqual(len(self.fetcher.news_list), 5)
        self.assertEqual(
            [item['favorites'] for item in self.fetcher.news_list],
            sorted([item['favorites'] for item in self.fetcher.news_list], reverse=True),
        )

    def test_zhihu_is_capped_at_five(self):
        now = int(datetime.now().timestamp())
        response = Mock()
        response.json.return_value = {'data': [
            {
                'detail_text': f'{100 - i} 万热度',
                'target': {'id': i, 'title': f'知乎热榜 {i}', 'created': now},
            }
            for i in range(6)
        ]}
        with patch.object(self.fetcher, 'get_with_retry', return_value=response):
            self.fetcher.fetch_zhihu()
        self.assertEqual(len(self.fetcher.news_list), 5)

    @staticmethod
    def _ranked_fixture(heading, prefix, title_prefix):
        cards = "".join(
            f'<article><h3><a href="{prefix}{i}">{title_prefix} {i}</a></h3></article>'
            for i in range(6)
        )
        return f'<section><h2>{heading}</h2>{cards}</section>'


class FrontendContractTests(unittest.TestCase):
    def test_frontend_has_fixed_hotness_sort_without_sort_buttons(self):
        html = Path("index.html").read_text(encoding="utf-8")
        self.assertNotIn('class="sort-buttons"', html)
        self.assertNotIn("currentSort", html)
        self.assertNotIn(".sort-buttons", html)
        self.assertIn("Number(b.hotness)", html)


if __name__ == "__main__":
    unittest.main()
