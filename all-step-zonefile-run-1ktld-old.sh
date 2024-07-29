#!/usr/bin/env bash
 
echo "开始测试......"
cd /home/nly/DNS/CZDS/czds-api-client-python-1k-tld
python3 download.py
wait
DATE=$(date +%Y%m%d) 
# DATE='20240517'
DIR="/home/nly/DNS/CZDS/1ktldzonefile_data/zonefiles-1k-tld/$DATE"
cd "$DIR"
# 打印当前路径
echo "当前路径是：$(pwd)"

LOG_DIR="/home/nly/DNS/CZDS/1ktldzonefile_data/log"
LOG_FILE="$LOG_DIR/$DATE.txt"

# 遍历所有 gz 文件并解压
for file in *.gz; do
  if ! gzip -df "$file"; then
    echo "解压 $file 失败，删除损坏的文件" >> "$LOG_FILE"
    rm -f "$file"
  fi
done

# 等待所有后台任务完成
wait

# 循环处理目录中的所有.tar文件，解压并删除
for file in *.tar; do
    tar -xvf "$file" && rm "$file"
done

# 拆分com.txt
CHAIFEN="$DIR/zonefile_chaifen"
mkdir "$CHAIFEN"
split -l 10000000 "$DIR/com.txt" "$CHAIFEN/com.txt"
wait

#提取csv信息
python3 /home/nly/DNS/CZDS/czds-api-client-python-1k-tld/step1_zonefile_extract.py "$DATE"
wait
        


# # 做二阶段扫描
PHASE1="/home/nly/DNS/CZDS/1ktldzonefile_data/phase1_zonefile_extraction/$DATE"
echo "$PHASE1"
# # 处理csv提取ns
python3 /home/nly/DNS/CZDS/czds-api-client-python-1k-tld/step2_extract_ns.py "$PHASE1"
wait


# step4是用zdns扫描所有ns
sh /home/nly/DNS/CZDS/czds-api-client-python-1k-tld/step4_try.sh "$DATE"
wait


# # # 压缩zonefile，删去不需要的 zonefile——拆分文件夹
find . -type d -name "zonefile_chaifen" -exec rm -r {} +
find . -type f -name "*.txt" -exec bash -c 'tar -czvf "${1%.txt}.tar.gz" "$1" && rm "$1"' _ {} \;

