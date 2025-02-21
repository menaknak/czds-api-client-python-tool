#!/bin/bash

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# 设置 PYTHONPATH 以便能找到 utils 模块
export PYTHONPATH="${SCRIPT_DIR}"

# 切换到项目根目录
cd "${SCRIPT_DIR}"

# 使用Python脚本获取配置路径
get_path() {
    python3 -c "from utils.path_manager import PathManager; print(PathManager().get_path('$1'))"
}

get_dated_path() {
    python3 -c "from utils.path_manager import PathManager; print(PathManager().get_dated_path('$1', '$2'))"
}

DATE=$1
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
INPUT_BASE="ns_set_$DATE"

# 使用PathManager获取路径
INPUT_FILE="$(get_dated_path 'phase1_extraction' "$DATE")/ns_set.txt"
OUTPUT_DIR="$(get_path 'phase4_zdns')"
LOG_DIR="$(get_path 'zdns_logs')"

# 确保输入文件存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "错误：输入文件不存在: $INPUT_FILE"
    exit 1
fi

DATALENGTH=$(wc -l < "$INPUT_FILE")

# 检查输出文件是否已存在，如果存在则加上后缀(1), (2), ...
COUNT=1
SUF="zdns_${INPUT_BASE}_${DATALENGTH}_${COUNT}"
OUTPUT_FILE_A="${OUTPUT_DIR}/${SUF}_A_iter.txt"
OUTPUT_FILE_AAAA="${OUTPUT_DIR}/${SUF}_AAAA_iter.txt"
while [ -f "$OUTPUT_FILE_A" ] || [ -f "$OUTPUT_FILE_AAAA" ]; do
    SUF="zdns_${INPUT_BASE}_${DATALENGTH}_${COUNT}"
    OUTPUT_FILE_A="${OUTPUT_DIR}/${SUF}_A.txt"
    OUTPUT_FILE_AAAA="${OUTPUT_DIR}/${SUF}_AAAA.txt"
    COUNT=$((COUNT + 1))
done

# 检查日志目录是否存在，如果不存在则创建
if [ ! -d "$LOG_DIR" ]; then
    mkdir -p "$LOG_DIR"
fi

LOG_FILE="$LOG_DIR/${SUF}.log" 

# 记录开始时间
echo "{
    \"cmd\": [
        \"cat $INPUT_FILE | ./zdns A  --iterative --threads=2500 --output-file=$OUTPUT_FILE_A\",
        \"cat $INPUT_FILE | ./zdns AAAA  --iterative --threads=2500 --output-file=$OUTPUT_FILE_AAAA\"
    ],
    \"start_time\": \"$START_TIME\",
    \"end_time\": \"\",
    \"time\": \"\"
}" > "$LOG_FILE"

# 执行 A 类型和 AAAA 类型的查询并将结果输出到指定文件
zdns A --input-file="$INPUT_FILE" --iterative --threads=2500 --retries 2 --timeout 10 --output-file="$OUTPUT_FILE_A" &
zdns AAAA --input-file="$INPUT_FILE" --iterative --threads=2500 --retries 2 --timeout 10 --output-file="$OUTPUT_FILE_AAAA" &

wait

END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
ELAPSED_TIME=$(date -u -d @"$(( $(date -d "$END_TIME" +%s) - $(date -d "$START_TIME" +%s) ))" +"%T")

# 更新日志文件
sed -i "s/\"end_time\": \"\",/\"end_time\": \"$END_TIME\",/" "$LOG_FILE"
sed -i "s/\"time\": \"\"/\"time\": \"$ELAPSED_TIME\"/" "$LOG_FILE"
# 输出运行时间
echo "Elapsed time: $ELAPSED_TIME"
