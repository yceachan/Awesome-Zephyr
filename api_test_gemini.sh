#!/bin/bash

# Gemini API 连通性测试脚本
#
# 功能:
#   用于测试与 Google Gemini API 的连通性。支持通过参数选择模型和设置超时。
#
# 用法:
#   确保已设置环境变量 GEMINI_API_KEY。
#   例如: export GEMINI_API_KEY="你的API密钥"
#
#   ./gemini_api_test.sh [选项]
#
# 选项:
#   -v <version>  指定模型版本。有效值: '2.5', '3.1'。 (默认: '2.5')
#   -m <seconds>  指定 cURL 请求的超时时间（秒）。 (默认: 60)
#   -h            显示此帮助信息。
#
# 示例:
#   1. 使用默认值 (2.5 模型, 60s 超时):
#      ./gemini_api_test.sh
#
#   2. 测试 3.1 模型 (60s 超时):
#      ./gemini_api_test.sh -v 3.1
#
#   3. 使用 2.5 模型并设置 90s 超时:
#      ./gemini_api_test.sh -m 90
#
#   4. 同时指定 3.1 模型和 120s 超时:
#      ./gemini_api_test.sh -v 3.1 -m 120

# 1. 设置默认值
DEFAULT_MODEL_VERSION="2.5"
DEFAULT_TIMEOUT=60

MODEL_VERSION=$DEFAULT_MODEL_VERSION
TIMEOUT=$DEFAULT_TIMEOUT

# 帮助函数
show_help() {
    grep "^# " "$0" | cut -c 3-
    exit 0
}

# 2. 解析命令行选项
while getopts "v:m:h" opt; do
  case $opt in
    v) MODEL_VERSION="$OPTARG" ;;
    m) TIMEOUT="$OPTARG" ;;
    h) show_help ;;
    \?) echo "错误: 无效的选项。使用 -h 获取帮助。" >&2; exit 1 ;;
  esac
done

# 3. 验证并选择模型名称
MODEL_NAME=""
case $MODEL_VERSION in
    "2.5")
        MODEL_NAME="gemini-2.5-pro"
        ;;
    "3.1")
        MODEL_NAME="gemini-3.1-pro-preview"
        ;;
    *)
        echo "错误: 无效的模型版本 '$MODEL_VERSION'. 请使用 '2.5' 或 '3.1'." >&2
        exit 1
        ;;
esac

# 4. 设置 API 端点
GEMINI_API_ENDPOINT="https://generativelanguage.googleapis.com/v1beta/models/${MODEL_NAME}:generateContent"

# 5. 检查 API 密钥
if [ -z "$GEMINI_API_KEY" ]; then
  echo "错误: 请确保已设置 GEMINI_API_KEY 环境变量。" >&2
  exit 1
fi

# 6. 执行测试
echo "正在测试 Gemini API 连通性..."
echo "模型: $MODEL_NAME"
echo "超时: ${TIMEOUT}s"
echo "API 端点: $GEMINI_API_ENDPOINT"
echo "-------------------------------------------"

# 执行 curl 请求并捕获输出
# 1. 使用 -v 获取详细调试信息
# 2. 将密钥放入 Header "x-goog-api-key" 中
# 3. 使用 -w 附加 HTTP 状态码到输出末尾
# 4. 将 stderr 重定向到 stdout (2>&1) 以便处理
raw_output=$(curl -v \
  --request POST \
  --url "${GEMINI_API_ENDPOINT}" \
  --header 'Content-Type: application/json' \
  --header "x-goog-api-key: ${GEMINI_API_KEY}" \
  --data '{"contents": [{"parts": [{"text": "Hello, Gemini!"}]}]}' \
  -w "\n__HTTP_STATUS__:%{http_code}" \
  -m "$TIMEOUT" 2>&1)

# 提取 HTTP 状态码并从输出中移除
http_code=$(echo "$raw_output" | grep -o '__HTTP_STATUS__:[0-9]*' | cut -d ':' -f 2 | tail -n 1)
clean_output=$(echo "$raw_output" | sed '/__HTTP_STATUS__:[0-9]*/d')

# 打印日志并脱敏密钥
echo "$clean_output" | sed "s/${GEMINI_API_KEY}/[REDACTED]/g"

echo -e "\n-------------------------------------------"
echo "测试完成。请检查上方输出中的调试信息。"

# 在日志尾部单独渲染 RESULT CODE
if [ "$http_code" = "200" ]; then
  echo -e "\n✅  [HTTP RESULT CODE: $http_code] 连接成功！"
else
  echo -e "\n❌  [HTTP RESULT CODE: ${http_code:-UNKNOWN}] 连接异常。"
fi
