#!/usr/bin/env python3
"""只读烟雾测试：抓取新增网站并打印结果，不写入 data/。"""

from fetch_news import MAX_ITEMS_PER_SOURCE, NewsFetcher


SOURCES = (
    '钛媒体', '36氪', '虎嗅', 'Phys.org', 'WIRED', 'The Verge', 'NPR',
    'Security Affairs', 'FreeBuf', 'Scientific American', 'The Guardian',
)


def main():
    for source in SOURCES:
        fetcher = NewsFetcher()
        fetcher.max_retries = 1
        fetcher.timeout = 12
        fetcher.fetch_hotlist({'name': source})
        items = fetcher.news_list
        status = 'OK' if items else 'SKIP'
        print(f'[{status}] {source}: {len(items)}/{MAX_ITEMS_PER_SOURCE}')
        for item in items:
            print(f'  - {item["title"]} | {item["url"]}')
        if len(items) > MAX_ITEMS_PER_SOURCE:
            raise AssertionError(f'{source} returned more than {MAX_ITEMS_PER_SOURCE} items')


if __name__ == '__main__':
    main()
