#!/bin/bash

#!/bin/bash
DATE=$1
START_TIME=$(date +"%Y-%m-%d %H:%M:%S")
INPUT_BASE="ns_set_$DATE"
INPUT_FILE="/home/nly/DNS/CZDS/1ktldzonefile_data/phase1_zonefile_extraction/$DATE/ns_set.txt"


DATALENGTH=$(wc -l < "$INPUT_FILE")
OUTPUT_DIR="/home/nly/DNS/CZDS/1ktldzonefile_data/phase4_zdns_output"
LOG_DIR="/home/nly/DNS/CZDS/log/phase4_zdns"

# 检查输出文件是否已存在，如果存在则加上后缀(1), (2), ...
COUNT=1
SUF="zdns_${INPUT_BASE}_${DATALENGTH}_${COUNT}"
# OUTPUT_FILE_A="${OUTPUT_DIR}/zdns_${INPUT_BASE}_A.txt"
# OUTPUT_FILE_AAAA="${OUTPUT_DIR}/zdns_${INPUT_BASE}_AAAA.txt"
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
# cat "$INPUT_FILE" | ./zdns A --name-servers=1.1.1.1 --threads=10000 > "$OUTPUT_FILE_A" &
# cat "$INPUT_FILE" | ./zdns AAAA --name-servers=1.1.1.1 --threads=10000 > "$OUTPUT_FILE_AAAA" &
# wait
# zdns A --input-file="$INPUT_FILE" --name-servers @/home/nly/DNS/CZDS/openresolver/data/pdnslist/pdns_top2000_convert.txt --threads=4000 --retries 2 --timeout 8 --output-file="$OUTPUT_FILE_A" &
# zdns AAAA --input-file="$INPUT_FILE" --name-servers @/home/nly/DNS/CZDS/openresolver/data/pdnslist/pdns_top2000_convert.txt --threads=4000 --retries 2 --timeout 8 --output-file="$OUTPUT_FILE_AAAA" &
# zdns A --input-file="$INPUT_FILE" --name-servers @/home/nly/DNS/CZDS/openresolver/data/zgc/useful_resolvers_convert.txt --threads=5000 --retries 1 --timeout 8 --output-file="$OUTPUT_FILE_A" &
# zdns AAAA --input-file="$INPUT_FILE" --name-servers @/home/nly/DNS/CZDS/openresolver/data/zgc/useful_resolvers_convert.txt --threads=5000 --retries 1 --timeout 8 --output-file="$OUTPUT_FILE_AAAA" &
zdns A --input-file="$INPUT_FILE" --iterative --threads=2500 --retries 2 --timeout 3 --output-file="$OUTPUT_FILE_A" &
zdns AAAA --input-file="$INPUT_FILE" --iterative --threads=2500 --retries 2 --timeout 3 --output-file="$OUTPUT_FILE_AAAA" &


wait
# --input-file


END_TIME=$(date +"%Y-%m-%d %H:%M:%S")
ELAPSED_TIME=$(date -u -d @"$(( $(date -d "$END_TIME" +%s) - $(date -d "$START_TIME" +%s) ))" +"%T")

# 更新日志文件
sed -i "s/\"end_time\": \"\",/\"end_time\": \"$END_TIME\",/" "$LOG_FILE"
sed -i "s/\"time\": \"\"/\"time\": \"$ELAPSED_TIME\"/" "$LOG_FILE"
# 输出运行时间
echo "Elapsed time: $ELAPSED_TIME"
