#!/bin/bash

# 推送脚本 - 将代码推送到GitHub仓库

echo "=== 开始推送代码到 GitHub ==="

# 检查当前目录状态
echo "检查当前目录状态..."
git status

# 检查是否有未提交的更改
if git status --porcelain | grep -q .; then
    echo "有未提交的更改，先提交..."
    # 添加所有更改的文件
    echo "添加所有更改的文件..."
    git add .
    
    # 提交更改
    echo "提交更改..."
    git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 拉取远程更改
echo "拉取远程更改..."
git pull --rebase git@github.com:junxie01/daily_news.git main

# 处理冲突（如果有）
if [ $? -ne 0 ]; then
    echo "拉取时出现冲突，尝试自动解决..."
    
    # 检查是否有data/news.json文件的冲突
    if git status --porcelain | grep -q "UU data/news.json"; then
        echo "检测到data/news.json文件冲突，使用本地版本覆盖..."
        git checkout --ours data/news.json
        git add data/news.json
        git rebase --continue
    else
        echo "无法自动解决冲突，请手动解决冲突后再运行此脚本"
        exit 1
    fi
fi

# 再次检查是否有更改（可能是rebase产生的）
if git status --porcelain | grep -q .; then
    echo "有更改需要提交..."
    # 添加所有更改的文件
    echo "添加所有更改的文件..."
    git add .
    
    # 提交更改
    echo "提交更改..."
    git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到GitHub仓库（使用SSH方式）
echo "推送到GitHub仓库..."
git push git@github.com:junxie01/daily_news.git main

echo "=== 推送完成 ==="
