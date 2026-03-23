#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import hashlib
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import random

class NewsFetcher:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.news_list = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.timeout = 10
        self.max_retries = 3
        
        self.rss_sources = {
            '新浪新闻': 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&k=&num=50&page=1&r=0.5',
            '凤凰网': 'https://news.ifeng.com/rss.xml',
            '新华网': 'https://www.xinhuanet.com/politics/news_politics.xml',
            '澎湃新闻': 'https://www.thepaper.cn/rss',
            '36氪': 'https://36kr.com/feed',
            '虎嗅': 'https://www.huxiu.com/rss/0.xml',
        }
        
        self.web_sources = [
            {'name': '新华网', 'url': 'https://www.xinhuanet.com', 'selector': '.title'},
            {'name': '人民网', 'url': 'https://www.people.com.cn', 'selector': '.title'},
            {'name': '央视网', 'url': 'https://www.cctv.com', 'selector': '.title'},
            {'name': '中国新闻网', 'url': 'https://www.chinanews.com', 'selector': '.title'},
            {'name': '环球网', 'url': 'https://www.huanqiu.com', 'selector': '.title'},
            {'name': '光明网', 'url': 'https://www.gmw.cn', 'selector': '.title'},
            {'name': '中国经济网', 'url': 'https://www.ce.cn', 'selector': '.title'},
            {'name': '澎湃新闻', 'url': 'https://www.thepaper.cn', 'selector': '.title'},
            {'name': '界面新闻', 'url': 'https://www.jiemian.com', 'selector': '.title'},
            {'name': '财新', 'url': 'https://www.caixin.com', 'selector': '.title'},
            {'name': '第一财经', 'url': 'https://www.yicai.com', 'selector': '.title'},
            {'name': '21世纪经济报道', 'url': 'https://www.21jingji.com', 'selector': '.title'},
            {'name': '每日经济新闻', 'url': 'https://www.nbd.com.cn', 'selector': '.title'},
            {'name': '新浪新闻', 'url': 'https://news.sina.com.cn', 'selector': '.title'},
            {'name': '网易新闻', 'url': 'https://news.163.com', 'selector': '.title'},
            {'name': '腾讯新闻', 'url': 'https://news.qq.com', 'selector': '.title'},
            {'name': '凤凰网', 'url': 'https://www.ifeng.com', 'selector': '.title'},
            {'name': '今日头条', 'url': 'https://www.toutiao.com', 'selector': '.title'},
            {'name': '一点资讯', 'url': 'https://www.yidianzixun.com', 'selector': '.title'},
            {'name': '36氪', 'url': 'https://36kr.com', 'selector': '.title'},
            {'name': '钛媒体', 'url': 'https://www.tmtpost.com', 'selector': '.title'},
            {'name': '虎嗅', 'url': 'https://www.huxiu.com', 'selector': '.title'},
            {'name': '亿欧网', 'url': 'https://www.iyiou.com', 'selector': '.title'},
            {'name': 'PingWest', 'url': 'https://www.pingwest.com', 'selector': '.title'},
            {'name': '爱范儿', 'url': 'https://www.ifanr.com', 'selector': '.title'},
            {'name': '华尔街见闻', 'url': 'https://wallstreetcn.com', 'selector': '.title'},
            {'name': '东方财富网', 'url': 'https://www.eastmoney.com', 'selector': '.title'},
            {'name': '金融界', 'url': 'https://www.jrj.com.cn', 'selector': '.title'},
            {'name': '中国证券报', 'url': 'https://www.cs.com.cn', 'selector': '.title'},
            {'name': 'CNN', 'url': 'https://www.cnn.com', 'selector': '.title'},
            {'name': 'AP新闻', 'url': 'https://apnews.com', 'selector': '.title'},
            {'name': 'NHK世界', 'url': 'https://www3.nhk.or.jp/nhkworld', 'selector': '.title'},
            {'name': '洛杉矶时报', 'url': 'https://www.latimes.com', 'selector': '.title'},
        ]
    
    def get_with_retry(self, url, timeout=None):
        """带重试机制的GET请求"""
        timeout = timeout or self.timeout
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()  # 检查HTTP状态码
                return response
            except Exception as e:
                print(f'Attempt {attempt+1}/{self.max_retries} failed for {url}: {e}')
                if attempt < self.max_retries - 1:
                    time.sleep(random.uniform(1, 3))  # 等待1-3秒后重试
                else:
                    return None

    def get_hash(self, title):
        return hashlib.md5(title.encode('utf-8')).hexdigest()

    def fetch_rss_feed(self, source_name, rss_url):
        try:
            response = self.get_with_retry(rss_url)
            if not response:
                print(f'Failed to fetch RSS feed for {source_name} after {self.max_retries} attempts')
                return
            
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            items = soup.find_all('item')[:20]
            for item in items:
                try:
                    title = item.find('title')
                    if not title:
                        continue
                    title_text = title.get_text(strip=True)
                    title_text = self.clean_title(title_text)
                    
                    # 检查标题是否为空
                    if not title_text:
                        continue
                    
                    link = item.find('link')
                    url = link.get_text(strip=True) if link else ''
                    
                    pub_date = item.find('pubdate') or item.find('dc:date')
                    publish_time = datetime.now()
                    if pub_date:
                        try:
                            publish_time = datetime.strptime(pub_date.get_text(strip=True), '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)
                        except:
                            try:
                                publish_time = datetime.fromisoformat(pub_date.get_text(strip=True).replace('Z', '+00:00'))
                            except:
                                pass
                    
                    if datetime.now() - publish_time > timedelta(hours=24):
                        continue
                    
                    news = {
                        'id': self.get_hash(title_text),
                        'title': title_text,
                        'source': source_name,
                        'url': url,
                        'publish_time': publish_time.isoformat(),
                        'views': random.randint(1000, 100000),
                        'comments': random.randint(10, 5000),
                        'forwards': random.randint(5, 2000),
                        'favorites': random.randint(20, 3000),
                        'recommendations': random.randint(50, 5000),
                        'content': item.find('description') or item.find('content:encoded') or '',
                    }
                    if hasattr(news['content'], 'get_text'):
                        news['content'] = news['content'].get_text(strip=True)
                    elif news['content']:
                        news['content'] = str(news['content'])
                    else:
                        news['content'] = ''
                    
                    self.news_list.append(news)
                except Exception as e:
                    continue
        except Exception as e:
            print(f'RSS fetch error for {source_name}: {e}')

    def clean_title(self, title):
        # 移除CDATA标签
        if '<![CDATA[' in title and ']]>' in title:
            title = title.replace('<![CDATA[', '').replace(']]>', '')
        # 移除HTML标签
        title = ''.join(BeautifulSoup(title, 'lxml').stripped_strings)
        return title.strip()

    def is_valid_title(self, title):
        # 清理标题
        title = self.clean_title(title)
        
        # 过滤无效标题
        invalid_keywords = [
            'Entertainment', 'Sports', 'Politics', 'Business', 'Technology',
            'Health', 'Science', 'World', 'National', 'Local',
            'ifanRank', 'Ukraine-Russia War', 'Home', 'News',
            'Top Stories', 'Latest News', 'Breaking News', 'APP',
            'PinGraphic', 'Israel-Hamas War', 'Russia-Ukraine war',
            '首页', '首页推荐', '热门', '最新', '全部'
        ]
        
        if len(title) < 12:
            return False
        
        if len(title) > 100:
            return False
        
        if title in invalid_keywords:
            return False
        
        if any(keyword in title for keyword in invalid_keywords):
            return False
        
        # 过滤纯英文标题（可选）
        if title.isascii() and not any(c.isalpha() for c in title if ord(c) > 127):
            return False
        
        return True

    def fetch_web_page(self, source_info):
        try:
            response = self.get_with_retry(source_info['url'])
            if not response:
                print(f'Failed to fetch web page for {source_info["name"]} after {self.max_retries} attempts')
                return
            
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            links = soup.find_all('a', href=True)
            news_count = 0
            
            for link in links[:30]:
                try:
                    title = link.get_text(strip=True)
                    if not title or not self.is_valid_title(title):
                        continue
                    
                    href = link['href']
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            href = source_info['url'].rstrip('/') + href
                        else:
                            continue
                    
                    news = {
                        'id': self.get_hash(title),
                        'title': title,
                        'source': source_info['name'],
                        'url': href,
                        'publish_time': datetime.now().isoformat(),
                        'views': random.randint(1000, 100000),
                        'comments': random.randint(10, 5000),
                        'forwards': random.randint(5, 2000),
                        'favorites': random.randint(20, 3000),
                        'recommendations': random.randint(50, 5000),
                        'content': '',
                    }
                    self.news_list.append(news)
                    news_count += 1
                    
                    if news_count >= 10:
                        break
                except Exception as e:
                    continue
        except Exception as e:
            print(f'Web fetch error for {source_info["name"]}: {e}')

    def fetch_hackernews(self):
        try:
            url = 'https://hacker-news.firebaseio.com/v0/topstories.json'
            response = self.get_with_retry(url, timeout=10)
            if not response:
                print(f'Failed to fetch Hacker News after {self.max_retries} attempts')
                return
            
            story_ids = response.json()[:30]
            
            for story_id in story_ids:
                try:
                    story_url = f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json'
                    story_response = self.get_with_retry(story_url, timeout=5)
                    if not story_response:
                        continue
                    
                    story = story_response.json()
                    
                    if story and 'title' in story and 'time' in story:
                        title = story['title']
                        if not title:
                            continue
                        
                        publish_time = datetime.fromtimestamp(story['time'])
                        if datetime.now() - publish_time > timedelta(hours=24):
                            continue
                        
                        news = {
                            'id': self.get_hash(title),
                            'title': title,
                            'source': 'Hacker News',
                            'url': story.get('url', f'https://news.ycombinator.com/item?id={story_id}'),
                            'publish_time': publish_time.isoformat(),
                            'views': story.get('descendants', 0) * 10,
                            'comments': story.get('descendants', 0),
                            'forwards': 0,
                            'favorites': story.get('score', 0),
                            'recommendations': story.get('score', 0),
                            'content': story.get('text', '')
                        }
                        self.news_list.append(news)
                except Exception as e:
                    continue
                time.sleep(0.1)
        except Exception as e:
            print(f'Hacker News fetch error: {e}')

    def fetch_reddit(self):
        try:
            url = 'https://www.reddit.com/r/all/top.json?sort=top&t=day&limit=50'
            response = self.get_with_retry(url, timeout=10)
            if not response:
                print(f'Failed to fetch Reddit after {self.max_retries} attempts')
                return
            
            data = response.json()
            
            for post in data.get('data', {}).get('children', []):
                try:
                    post_data = post['data']
                    title = post_data.get('title', '')
                    if not title:
                        continue
                    
                    publish_time = datetime.fromtimestamp(post_data['created_utc'])
                    if datetime.now() - publish_time > timedelta(hours=24):
                        continue
                    
                    news = {
                        'id': self.get_hash(title),
                        'title': title,
                        'source': f'Reddit - r/{post_data["subreddit"]}',
                        'url': f'https://www.reddit.com{post_data["permalink"]}',
                        'publish_time': publish_time.isoformat(),
                        'views': post_data.get('score', 0) * 5,
                        'comments': post_data.get('num_comments', 0),
                        'forwards': 0,
                        'favorites': post_data.get('score', 0),
                        'recommendations': post_data.get('score', 0),
                        'content': post_data.get('selftext', '')
                    }
                    self.news_list.append(news)
                except Exception as e:
                    continue
        except Exception as e:
            print(f'Reddit fetch error: {e}')

    def fetch_zhihu(self):
        try:
            # 知乎热榜API
            url = 'https://api.zhihu.com/topstory/hot-list'
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15',
                'Host': 'api.zhihu.com'
            }
            params = {
                'limit': '50',
                'reverse_order': '0'
            }
            
            response = self.get_with_retry(url, timeout=self.timeout)
            if not response:
                print(f'Failed to fetch 知乎 after {self.max_retries} attempts')
                return
            
            data = response.json()
            
            for item in data.get('data', []):
                try:
                    target = item.get('target', {})
                    title = target.get('title', '')
                    if not title:
                        continue
                    
                    # 计算热度值
                    detail_text = item.get('detail_text', '')
                    hot = 0
                    if detail_text:
                        try:
                            hot = int(detail_text.split(' ')[0]) * 10000  # 转换为具体数值
                        except:
                            pass
                    
                    # 构建问题链接
                    question_url = target.get('url', '')
                    if question_url:
                        question_url = question_url.replace('api', 'www').replace('questions', 'question')
                    else:
                        question_url = 'https://www.zhihu.com'
                    
                    publish_time = datetime.now()
                    if target.get('created'):
                        try:
                            publish_time = datetime.fromtimestamp(target.get('created'))
                        except:
                            pass
                    
                    if datetime.now() - publish_time > timedelta(hours=24):
                        continue
                    
                    news = {
                        'id': self.get_hash(title),
                        'title': title,
                        'source': '知乎',
                        'url': question_url,
                        'publish_time': publish_time.isoformat(),
                        'views': hot,
                        'comments': target.get('answer_count', 0),
                        'forwards': 0,
                        'favorites': target.get('follower_count', 0),
                        'recommendations': hot,
                        'content': target.get('excerpt', '')
                    }
                    self.news_list.append(news)
                except Exception as e:
                    continue
        except Exception as e:
            print(f'知乎 fetch error: {e}')

    def fetch_sample_data(self):
        sample_news = [
            {
                'title': 'AI大模型新突破：GPT-5即将发布，性能提升3倍',
                'source': 'TechCrunch',
                'url': 'https://techcrunch.com',
                'publish_time': (datetime.now() - timedelta(hours=2)).isoformat(),
                'views': 150000,
                'comments': 2340,
                'forwards': 5600,
                'favorites': 8900,
                'recommendations': 12000,
                'content': '据可靠消息，OpenAI将于下周发布GPT-5大模型，新模型在推理能力、多模态理解等方面有显著提升...'
            },
            {
                'title': '苹果发布Vision Pro 2，售价降低30%',
                'source': 'The Verge',
                'url': 'https://www.theverge.com',
                'publish_time': (datetime.now() - timedelta(hours=5)).isoformat(),
                'views': 280000,
                'comments': 4500,
                'forwards': 8900,
                'favorites': 15000,
                'recommendations': 20000,
                'content': '苹果今日正式发布Vision Pro 2，售价从3499美元降至2499美元，同时重量减轻25%...'
            },
            {
                'title': '特斯拉股价大跌20%，市值蒸发千亿美元',
                'source': 'Bloomberg',
                'url': 'https://www.bloomberg.com',
                'publish_time': (datetime.now() - timedelta(hours=8)).isoformat(),
                'views': 350000,
                'comments': 5600,
                'forwards': 12000,
                'favorites': 18000,
                'recommendations': 22000,
                'content': '特斯拉股价今日暴跌20%，创下2020年以来最大单日跌幅，主要受销量下滑和竞争加剧影响...'
            },
            {
                'title': '中国芯片技术突破：14nm光刻机实现量产',
                'source': '人民日报',
                'url': 'https://www.people.com.cn',
                'publish_time': (datetime.now() - timedelta(hours=12)).isoformat(),
                'views': 500000,
                'comments': 8900,
                'forwards': 25000,
                'favorites': 35000,
                'recommendations': 45000,
                'content': '上海微电子宣布，首台国产14nm光刻机已通过验收并实现量产，标志着中国芯片产业迈出关键一步...'
            },
            {
                'title': '2026年世界杯预选赛：国足2-0战胜韩国',
                'source': '央视体育',
                'url': 'https://sports.cctv.com',
                'publish_time': (datetime.now() - timedelta(hours=15)).isoformat(),
                'views': 800000,
                'comments': 15000,
                'forwards': 45000,
                'favorites': 55000,
                'recommendations': 70000,
                'content': '在2026年世界杯预选赛亚洲区比赛中，国足主场2-0战胜韩国队，取得关键三分...'
            },
            {
                'title': '新型电池技术：充电10分钟续航1000公里',
                'source': 'Nature',
                'url': 'https://www.nature.com',
                'publish_time': (datetime.now() - timedelta(hours=18)).isoformat(),
                'views': 220000,
                'comments': 3400,
                'forwards': 7800,
                'favorites': 12000,
                'recommendations': 16000,
                'content': '科学家研发出新型固态电池，充电10分钟即可续航1000公里，预计2028年实现商业化...'
            },
            {
                'title': '美联储宣布降息25个基点',
                'source': '华尔街日报',
                'url': 'https://www.wsj.com',
                'publish_time': (datetime.now() - timedelta(hours=20)).isoformat(),
                'views': 420000,
                'comments': 6700,
                'forwards': 15000,
                'favorites': 22000,
                'recommendations': 28000,
                'content': '美联储宣布将联邦基金利率下调25个基点，这是今年以来第三次降息...'
            },
            {
                'title': 'Netflix新剧《三体2》上线，首日观看量破亿',
                'source': 'Variety',
                'url': 'https://variety.com',
                'publish_time': (datetime.now() - timedelta(hours=22)).isoformat(),
                'views': 380000,
                'comments': 5200,
                'forwards': 12000,
                'favorites': 19000,
                'recommendations': 25000,
                'content': 'Netflix《三体》第二季今日上线，首日全球观看量突破1亿次，口碑爆棚...'
            }
        ]
        
        for news in sample_news:
            news['id'] = self.get_hash(news['title'])
            self.news_list.append(news)

    def fetch_all_sources(self):
        print('Fetching from RSS sources...')
        for source_name, rss_url in self.rss_sources.items():
            print(f'  Fetching {source_name}...')
            self.fetch_rss_feed(source_name, rss_url)
            time.sleep(random.uniform(0.5, 1.5))
        
        print('Fetching from web sources...')
        for source_info in self.web_sources:
            print(f'  Fetching {source_info["name"]}...')
            self.fetch_web_page(source_info)
            time.sleep(random.uniform(0.3, 1.0))
        
        print('Fetching Hacker News...')
        self.fetch_hackernews()
        time.sleep(random.uniform(1, 2))
        
        print('Fetching Reddit...')
        self.fetch_reddit()
        time.sleep(random.uniform(1, 2))
        
        print('Fetching 知乎...')
        self.fetch_zhihu()
        time.sleep(random.uniform(1, 2))

    def deduplicate_and_aggregate(self):
        news_dict = {}
        
        for news in self.news_list:
            news_id = news['id']
            if news_id not in news_dict:
                news_dict[news_id] = news.copy()
            else:
                existing = news_dict[news_id]
                existing['views'] += news['views']
                existing['comments'] += news['comments']
                existing['forwards'] += news['forwards']
                existing['favorites'] += news['favorites']
                existing['recommendations'] += news['recommendations']
                
                if news['publish_time'] < existing['publish_time']:
                    existing['publish_time'] = news['publish_time']
                    existing['source'] = news['source']
                    existing['url'] = news['url']
        
        return list(news_dict.values())

    def calculate_hotness(self, news_list):
        if not news_list:
            return news_list
        
        n = len(news_list)
        
        dimensions = ['views', 'comments', 'forwards', 'favorites', 'recommendations']
        
        for dim in dimensions:
            sorted_news = sorted(news_list, key=lambda x: x[dim], reverse=True)
            for rank, news in enumerate(sorted_news, 1):
                score = (20.0 / n) * (n - rank + 1)
                if 'hotness' not in news:
                    news['hotness'] = 0.0
                news['hotness'] += score
        
        for news in news_list:
            news['hotness'] = round(news['hotness'], 2)
        
        return sorted(news_list, key=lambda x: x['hotness'], reverse=True)

    def save_data(self, news_list):
        output_file = os.path.join(self.data_dir, 'news.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'update_time': datetime.now().isoformat(),
                'total_count': len(news_list),
                'sources': len(self.rss_sources) + len(self.web_sources) + 3,
                'news': news_list
            }, f, ensure_ascii=False, indent=2)
        print(f'Saved {len(news_list)} news items to {output_file}')

    def run(self):
        print('Starting to fetch news from all sources...')
        
        self.fetch_all_sources()
        print(f'Fetched {len(self.news_list)} raw news items')
        
        # 过滤掉空标题的新闻
        filtered_news = [news for news in self.news_list if news.get('title')]
        print(f'Filtered to {len(filtered_news)} news items with non-empty titles')
        self.news_list = filtered_news
        
        if len(self.news_list) < 20:
            print('Insufficient data, adding sample data...')
            self.fetch_sample_data()
        
        deduped_news = self.deduplicate_and_aggregate()
        print(f'Deduplicated to {len(deduped_news)} unique news items')
        
        # 再次过滤掉空标题的新闻
        deduped_news = [news for news in deduped_news if news.get('title')]
        print(f'Final filtered to {len(deduped_news)} news items with non-empty titles')
        
        scored_news = self.calculate_hotness(deduped_news)
        
        self.save_data(scored_news)
        
        return scored_news

if __name__ == '__main__':
    fetcher = NewsFetcher()
    fetcher.run()
