import requests
import pandas as pd
import time
import os

def save_hot_list():
    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15',
        'Host': 'api.zhihu.com'
    }
    
    # 请求参数
    params = (
        ('limit', '50'),
        ('reverse_order', '0'),
    )
    
    # 发送请求
    response = requests.get(
        'https://zhihu.com/topstory/hot-list', 
        headers=headers, 
        params=params
    )
    
    items = response.json()['data']
    rows = []
    
    # 遍历热榜数据
    for rank, item in enumerate(items, start=1):
        target = item.get('target')
        title = target.get('title')
        answer_count = target.get('answer_count')
        hot = int(item.get('detail_text').split(' ')[0])
        follower_count = target.get('follower_count')
        question_url = target.get('url').replace('api', 'www').replace('questions', 'question')
        
        rows.append({
            '排名': rank,
            '标题': title,
            '回答数': answer_count,
            '关注数': follower_count,
            '热度(万)': hot,
            '问题链接': question_url
        })
    
    # 创建DataFrame并保存
    df = pd.DataFrame(rows)
    now = time.strftime('%Y-%m-%d %H-%M-%S')
    dir_path = now.split(' ')[0]
    
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    csv_path = f'{dir_path}/{now}.csv'
    df.to_csv(csv_path, encoding='utf-8-sig', index=None)
    print(f'{now} 的热榜数据已保存到文件: {csv_path}')
    
    return df

# 执行
save_hot_list()
