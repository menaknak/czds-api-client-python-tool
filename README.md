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

1. 编辑 `config.json`，填写相关信息，需要填写的信息有：ICANN账号密码，"base_paths":输出路径，"target.tld.list":待下载TLD列表。  
2. 单次下载，运行命令：`python3 download-checkpoint-retry.py`  
3. 单次下载并完成数据处理，运行命令：`bash all-step-zonefile-run-1ktld-checkpoint-retry.sh`
4. 如果需要周期性下载，编辑`all-step-zonefile-run-1k-scheduler.py`，自定义脚本启动时间。运行命令`python3 all-step-zonefile-run-1k-scheduler.py`。

下载的区域文件将保存在 `working-directory` 文件夹中。  
`working-directory` 的路径可以在 `config.json` 中指定，若未指定，则默认为当前目录。  

## 输出文件

### 目录结构
总输出目录由用户在`config.json`中自定义。以下展示总目录中各个分目录：
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
    A_365395.csv：
    ```txt
    hostname,IPv4
    0.blackcat.ns.principate.org.,193.201.200.34
    0.dns.ressis.org.,194.176.0.3
    0.name.terminaldigit.org.,52.229.11.115
    0.node.org.,70.38.94.182
    0.ns-gslb.org.,185.200.246.12
    ```
    AAAA_15363.csv
    ```txt
    hostname,IPv6
    0.ns-gslb.org.,2001:0678:0f28:0000:0000:0000:0000:0008
    0.ns-gslb.org.,2001:0678:0f28:0000:0000:0000:0000:0012
    00.010101.org.,2001:08d8:1800:815b:0000:0000:0000:0001
    001.baitnet.org.,2a00:dcc0:0eda:3748:0216:3cff:fe34:b740
    010.baitnet.org.,2a00:7b80:3008:0003:0000:0000:13df:c042
    ```
    NS_27678121.csv
    ```txt
    SLD,hostname
    0--0.org.,ns1.sitehost.co.nz.
    0--0.org.,ns2.sitehost.co.nz.
    0--0.org.,ns3.sitehost.co.nz.
    0-0-0.org.,ns1-coming-soon.sav.com.
    0-0-0.org.,ns2-coming-soon.sav.com.
    ```
    ds_597803.txt
    ```txt
    coorace-hdf.org.
    innovationscheckar.org.
    apprenticeshiptracker.org.
    bangadarshan.org.
    centerfordisinformationdefense.org.
    ```
    20240417/ns_set.txt
    ```txt
    ns2.onlinesuite.net
    ns1.sellscotland.com
    ns4.mldl1-ecomm.com
    ns1.kon-cept.com
    ns1.sojo-interactive.com.lamedelegation.org
    ns4.voyagerlearning.com
    ```
- phase4_zdns_output：存放`step4_zdnsscan.sh`zdns扫描ns_set.txt的结果。
    ```txt
    /home/nly/DNS/CZDS/1ktldzonefile_data/phase4_zdns_output
    ├── zdns_ns_set_20241127_2370809_1_A_iter.txt
    ├── zdns_ns_set_20241227_2364827_1_AAAA_iter.txt
    ├── zdns_ns_set_20241227_2364827_1_A_iter.txt
    ├── zdns_ns_set_20250101_2363211_1_AAAA_iter.txt
    ├── zdns_ns_set_20250101_2363211_1_A_iter.txt
    ├── zdns_ns_set_20250108_2359051_1_AAAA_iter.txt
    └── zdns_ns_set_20250108_2359051_1_A_iter.txt
    ```
    zdns_ns_set_20250108_2359051_1_A_iter.txt
    ```txt
    {"data":{"answers":[{"answer":"113.43.208.203","class":"IN","name":"ns2.a-t-s.biz","ttl":3600,"type":"A"}],"protocol":"","resolver":""},"name":"ns2.a-t-s.biz","status":"NOERROR","timestamp":"2025-01-08T10:48:01+08:00"}
    {"data":{"protocol":"udp","resolver":"156.154.125.65:53"},"name":"pleasedropthishost15965.versistmedia.biz","status":"NXDOMAIN","timestamp":"2025-01-08T10:48:01+08:00"}
    {"data":{"protocol":"udp","resolver":"37.209.196.13:53"},"name":"dropthishost-8cedef7b-b807-4fc8-9029-351a766325fe.biz","status":"NXDOMAIN","timestamp":"2025-01-08T10:48:01+08:00"}
    {"data":{"answers":[{"answer":"194.58.198.54","class":"IN","name":"ns2.ubu.bank","ttl":172800,"type":"A"}],"protocol":"","resolver":""},"name":"ns2.ubu.bank","status":"NOERROR","timestamp":"2025-01-08T10:48:01+08:00"}
    {"data":{"answers":[{"answer":"213.199.51.231","class":"IN","name":"ns2.zendahost.top","ttl":3600,"type":"A"}],"protocol":"","resolver":""},"name":"ns2.zendahost.top","status":"NOERROR","timestamp":"2025-01-08T10:48:01+08:00"}
    ```


- analyse：用于存放用户自己的分析脚本