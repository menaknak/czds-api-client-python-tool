周期性下载TOP1K顶级域名区域文件
===========

通过 CZDS（集中化域名区数据服务）REST API 下载区文件


环境/依赖
------------


1. python 3

2. python依赖库：

```bash
pip install request
```
3. 实验所用主机配置是
```txt
系统：Ubuntu 18.04
CPU核数：16核
内存：64G
```

使用说明
---------------------

1. 编辑 `config.json`，填写相关信息，如需要下载的TLD和账号密码。  
2. 单次下载，运行命令：`python3 download-checkpoint-retry.py`  
3. 如果需要周期性下载，编辑`all-step-zonefile-run-1k-scheduler.py`，自定义脚本启动时间。运行命令`python3 all-step-zonefile-run-1k-scheduler.py`。

所有的区文件将保存在 `working-directory`/zonefiles 文件夹中。  
`working-directory` 的路径可以在 `config.json` 中指定，若未指定，则默认为当前目录。  

## 输出文件

### 目录结构
总输出目录由用户在`config.json`和`all-step-zonefile-run-1ktld-checkpoint-retry.sh`中自定义。以下展示总目录中各个分目录：
```txt
.
├── analysis
├── log
├── phase1_zonefile_extraction
├── phase4_zdns_output
└── zonefiles-1k-tld
```
- zonefiles-1k-tld：存放下载的zonefiles，每个zonefile在数据处理后压缩为gz包。
- log：
    存放`step1_zonefile_extract.py`数据处理途中发生的错误。
- phase1_zonefile_extraction：存放`step1_zonefile_extract.py`从zonefiles里提取出来的各类记录csv。并且存放每个日期下，`step2_extract_ns.py`提取出来的ns_set.txt。
    ```txt
    /home/nly/DNS/CZDS/1ktldzonefile_data/phase1_zonefile_extraction/20240417/org
    ├── A_365395.csv
    ├── AAAA_15363.csv
    ├── ds_597803.txt
    └── NS_27678121.csv
    /home/nly/DNS/CZDS/1ktldzonefile_data/phase1_zonefile_extraction/20240417/ns_set.txt
    ```
- phase4_zdns_output：存放`step4_zdnsscan.sh`zdns扫描ns_set.txt的结果。


- analyse：用于存放用户自己的分析脚本