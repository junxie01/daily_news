import praw
import pandas as pd
from datetime import datetime

def fetch_reddit_home_api():
    # 替换为你的凭证
    reddit = praw.Reddit(
        client_id="你的client_id",
        client_secret="你的client_secret",
        user_agent="你的user_agent",
        username="你的Reddit用户名（可选）",
        password="你的Reddit密码（可选）"
    )
    
    # 抓取主页热门板块（r/all）的前50条资讯
    hot_posts = reddit.subreddit("all").hot(limit=50)
    
    # 解析数据
    reddit_data = []
    for idx, post in enumerate(hot_posts, 1):
        reddit_data.append({
            "排名": idx,
            "标题": post.title,
            "子版块": post.subreddit_name_prefixed,  # 所属板块（如r/worldnews）
            "点赞数": post.score,
            "评论数": post.num_comments,
            "发布时间": datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M:%S"),
            "链接": f"https://www.reddit.com{post.permalink}",
            "内容摘要": post.selftext[:200] + "..." if len(post.selftext) > 200 else post.selftext,
            "是否置顶": post.stickied
        })
    
    return reddit_data

# 执行抓取并保存
if __name__ == "__main__":
    try:
        data = fetch_reddit_home_api()
        if data:
            df = pd.DataFrame(data)
            # 保存为CSV（UTF-8编码，避免乱码）
            df.to_csv("reddit_home_news.csv", index=False, encoding="utf-8-sig")
            print("抓取完成！数据已保存到 reddit_home_news.csv")
            # 打印前5条预览
            print("\n前5条资讯预览：")
            print(df.head())
    except Exception as e:
        print(f"抓取失败：{str(e)}")
