#!/usr/bin/env python3
import requests

sites = [
    'https://www.bbc.com/news',
    'https://www.nytimes.com',
    'https://www.washingtonpost.com',
    'https://www.cnn.com',
    'https://www.reuters.com',
    'https://apnews.com',
    'https://www.theguardian.com',
    'https://www.ft.com',
    'https://www.bloomberg.com',
    'https://www3.nhk.or.jp/nhkworld',
    'https://www.aljazeera.com',
    'https://www.latimes.com',
    'https://www.usatoday.com',
    'https://www.thenikkei.com',
    'https://www.asahi.com',
    'https://www.lemonde.fr',
    'https://www.spiegel.de',
    'https://www.elpais.com',
    'https://www.foxnews.com',
    'https://www.globo.com'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}

print('Testing website connections...')
print('=' * 80)

for site in sites:
    print(f'\nTesting: {site}')
    try:
        response = requests.get(site, timeout=10, headers=headers)
        print(f'Status: {response.status_code}')
        print(f'URL: {response.url}')
    except Exception as e:
        print(f'Error: {e}')
    print('-' * 60)
