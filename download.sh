#!/usr/bin/env bash
# 加载 Conda 初始化脚本（使用你的实际路径）
source /home/nly/anaconda3/etc/profile.d/conda.sh

# 激活 base 环境
conda activate base

# 使用Python脚本获取配置路径
get_path() {
    python3 -c "from utils.path_manager import PathManager; print(PathManager().get_path('$1'))"
}

get_dated_path() {
    python3 -c "from utils.path_manager import PathManager; print(PathManager().get_dated_path('$1', '$2'))"
}

# 直接使用硬编码的项目根目录，因为这是固定的
PROJECT_ROOT="/home/nly/DNS/CZDS/czds-api-client-python-tool"
echo "开始测试......"
cd "$PROJECT_ROOT"

#监控并重新启动download-checkpoint-retry.py
while true; do
    python3 download-checkpoint-retry.py
    if [ $? -eq 0 ]; then
        break
    else
        echo "download-checkpoint-retry.py 异常退出，等待300秒后重新启动..."
        sleep 300
    fi
done

# DATE=$(date +%Y%m%d)
DATE="yyyymmdd"
ZONEFILE_DIR=$(get_dated_path 'zonefiles' "$DATE")
LOG_DIR=$(get_path 'log_root')
LOG_FILE="$LOG_DIR/$DATE.txt"

cd "$ZONEFILE_DIR"
echo "当前路径是：$(pwd)"

# 遍历所有 gz 文件并解压
for file in *.gz; do
    if ! gzip -df "$file"; then
        echo "解压 $file 失败，删除损坏的文件" >> "$LOG_FILE"
        rm -f "$file"
    fi
done

wait

# 循环处理目录中的所有.tar文件
for file in *.tar; do
    tar -xvf "$file" && rm "$file"
done

# 拆分com.txt
# CHAIFEN="$ZONEFILE_DIR/zonefile_chaifen"
# mkdir -p "$CHAIFEN"
# split -l 10000000 "$ZONEFILE_DIR/com.txt" "$CHAIFEN/com.txt"
# wait

# 提取csv信息
python3 "$PROJECT_ROOT/step1_zonefile_extract.py" "$DATE"
wait

cd "$PROJECT_ROOT"

# 二阶段扫描
PHASE1=$(get_dated_path 'phase1_extraction' "$DATE")
echo "$PHASE1"

# 处理csv提取ns
python3 "$PROJECT_ROOT/step2_extract_ns.py" "$PHASE1"
wait

# cd "$PROJECT_ROOT"

# # 用zdns扫描所有ns
# sh "$PROJECT_ROOT/step4_zdnsscan.sh" "$DATE"
# wait

# 压缩zonefile，删去不需要的文件
cd "$ZONEFILE_DIR"
find . -type d -name "zonefile_chaifen" -exec rm -r {} +
find . -type f -name "*.txt" -exec bash -c 'tar -czf "${1%.txt}.tar.gz" "$1" && rm "$1"' _ {} \;