#!/bin/bash

# 模拟 PowerShell 的 g-sparse 功能 (带物理清理)
# 用法: g_sparse <github-tree-url>
function g_sparse {
    local url="$1"
    
    # 正则匹配 GitHub URL 结构
    local regex="https://github.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)"
    
    if [[ $url =~ $regex ]]; then
        local user="${BASH_REMATCH[1]}"
        local repo="${BASH_REMATCH[2]}"
        local branch="${BASH_REMATCH[3]}"
        local subpath="${BASH_REMATCH[4]}"
        local repo_url="https://github.com/${user}/${repo}.git"
        local target_base=$(basename "$subpath")

        echo "🚀 Syncing from: $repo_url ($branch)"
        echo "📂 Target path:  $subpath"

        # 1. 创建临时目录
        local tmp_dir=$(mktemp -d)
        local original_pwd=$(pwd)

        # 2. 极简克隆 (Sparse & Shallow)
        # --filter=blob:none 极其重要，它不下载任何文件内容，只拉取索引
        git clone --depth 1 --filter=blob:none --sparse --branch "$branch" "$repo_url" "$tmp_dir" 2>/dev/null
        
        cd "$tmp_dir" || return
        
        # 3. 设置稀疏检出目标并同步文件
        echo "📥 Fetching files..."
        git sparse-checkout set "$subpath" 2>/dev/null
        git checkout "$branch" 2>/dev/null

        # 4. 将内容同步到执行命令时的目录
        if [ -d "$subpath" ]; then
            echo "📦 Moving files to $original_pwd..."
            # 使用 cp -a 保持权限，并覆盖
            cp -a "$subpath/." "$original_pwd/"
            echo "✅ Sync complete."
        else
            echo "❌ Error: Path $subpath not found in repository."
        fi

        # 5. 彻底清理临时空间
        cd "$original_pwd" || return
        rm -rf "$tmp_dir"
        echo "🧹 Temporary repository cleaned."
    else
        echo "❌ Error: Invalid GitHub tree URL."
        return 1
    fi
}

# 业务函数
function obs_sync_config {
    local target_dir="$HOME/Zephyr-Suite/note"
    
    mkdir -p "$target_dir"
    cd "$target_dir" || return
    
    # 执行同步 (该操作会将远程 .obsidian 下的内容拉取到当前目录的 .obsidian 下)
    # 因为远程路径是 .obsidian，g_sparse 会在当前目录下创建/更新 .obsidian
    g_sparse "https://github.com/yceachan/OsCookbook/tree/main/.obsidian"
    
    # 返回原目录
    cd - > /dev/null
}