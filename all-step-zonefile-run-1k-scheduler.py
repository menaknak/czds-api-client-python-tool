import schedule
import subprocess
import time

# 定义要执行的命令
# command = "bash /home/nly/DNS/CZDS/script/all-step-zonefile-run.sh"
# command = "bash /home/nly/DNS/CZDS/czds-api-client-python-1k-tld/all-step-zonefile-run-1ktld.sh"
command = "bash /home/nly/DNS/CZDS/czds-api-client-python-1k-tld/all-step-zonefile-run-1ktld-checkpoint-retry.sh"

# 定义要执行的时间
schedule.every().wednesday.at("04:00").do(subprocess.call, command, shell=True)
# schedule.every().thursday.at("16:34").do(subprocess.call, command, shell=True)

# 持续运行程序
while True:
    schedule.run_pending()
    time.sleep(1)
