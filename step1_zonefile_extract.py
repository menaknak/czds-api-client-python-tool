import time
from tqdm import tqdm
import pandas as pd
import os
import sys
from utils.path_manager import PathManager

def mkdir(path):
    path = path.strip().rstrip('/')
    exist = os.path.exists(path)
    if not exist:
        try:
            os.makedirs(path)
        except:
            pass
        
paths = PathManager()

DATE = time.strftime('%Y%m%d',time.localtime())
DATE = sys.argv[-1]

ERRORLOG = os.path.join(paths.get_dated_path('error_logs', DATE), f'{DATE}.err')
OUTPUTPATH = paths.get_dated_path('phase1_extraction', DATE)
# 获取没有DATE的phase3_domain_count路径
domain_sum_outputpath = paths.get_path('phase3_domain_count')
print(domain_sum_outputpath)
ZONEFILESPATH = paths.get_dated_path('zonefiles', DATE)
PATH = os.path.join(ZONEFILESPATH, 'zonefile_chaifen')
print(PATH)

def getfilelist(cur_path):
    filelist=[]
    for parent,dirs,files in os.walk(cur_path):
        flist=list(map(lambda x:os.path.join(parent,x),files))
        filelist.extend(flist)
    return filelist

comfilelist = getfilelist(PATH)
filelist=getfilelist(ZONEFILESPATH)

begin=time.time()
domain_sum = 0


nsrr_cols = ['SLD','hostname'] # todo: type
arr_cols = ['hostname','IPv4'] # todo: type
a4rr_cols = ['hostname','IPv6'] # todo: type

all_domain = set()


# tld_list=['app','book','bot','cam','camera','city','net','info','org']
# tld_list=["site","online","top","xyz","biz"]
# tld_list=["site","online","biz","top","xyz","net","info","org"]
# tld_list=[ "net", "org", "top", "xyz", "info", "site", "online", "biz", "win", "club", "pro", "gov", "app", "shop", "fun", "live", "cloud", "space", "tech"]

for tldfile in tqdm(filelist):
    file = tldfile.split('/')[-1]
    if 'com.' not in file  and 'tar' not in file:
        tld = file.split('.')[0]
        #filename=tld+'.txt'
        print('Processing: ',tldfile)

        sld = set()
        ns = set()
        ip = set()
        nsrr = []
        arr = []
        a4rr = []
        ds = set()


        with open(tldfile,'r') as f:
            for l in f:
                try:
                    s = l.split()
                    name = s[0]
                    typ = s[3].lower()
                    value = s[4]
                    domainsld = name
                    sld.add(domainsld)
                    if typ=='ns':
                        ns.add(value)
                        nsrr.append((name,value))
                    elif typ=='aaaa':
                        ip.add(value)

                        a4rr.append((name,value))
                    elif typ=='a':
                        ip.add(value)
                        arr.append((name,value))                
                    elif typ=='ds':
                        ds.add(name)
                except Exception as e:
                    with open(ERRORLOG,'a') as error:
                        errorstr = '记录: '+l+'发现问题: '
                        error.write(errorstr)
                        error.write('\n')
        


        nsrrdf=pd.DataFrame(nsrr)
        # nsrrdf[':LABEL']='NS'
        nsrrdf.columns = nsrr_cols

        a4rrdf=pd.DataFrame(a4rr)
        # a4rrdf[':LABEL']='AAAA'

        arrdf=pd.DataFrame(arr)
        # arrdf[':LABEL']='A'
        
        
        # 这里可以直接导入MySQL
        output = OUTPUTPATH+'/'+tld+'/'
        mkdir(output)
        nsrrdf.to_csv(output+'NS'+'_'+str(len(nsrrdf))+'.csv',index=False)
        if a4rr:
            a4rrdf.columns = a4rr_cols
        a4rrdf.to_csv(output+'AAAA'+'_'+str(len(a4rrdf))+'.csv',index=False)


        if arr:
            arrdf.columns = arr_cols
        arrdf.to_csv(output+'A'+'_'+str(len(arrdf))+'.csv',index=False)
        if ds:
            with open(output+'ds_'+str(len(ds))+'.txt','a') as f:
                for i in ds:
                    f.write(i)
                    f.write('\n')
        if sld:
            domain_sum+=len(sld)
            all_domain.update(sld)
            with open(output+'domainsum_'+str(len(sld))+'.txt','a') as f:
                for i in sld:
                    f.write(i)
                    f.write('\n')    
                
        
        del sld
        del ns
        del ip
        del nsrr
        del a4rr
        del arr
        del nsrrdf
        del a4rrdf
        del arrdf
        del ds
        
        


#先要把大文件split一下
for filename in tqdm(comfilelist):
    tld = 'com'
    print('Processing: ',filename)

    number = filename.split('.')[-1]

    sld = set()
    ns = set()
    ip = set()
    nsrr = []
    arr = []
    a4rr = []
    ds = set()


    with open(filename,'r') as f:
        for l in f:
            s = l.split()
            name = s[0]
            typ = s[3].lower()
            value = s[4]
            domainsld = name
            sld.add(domainsld)
            if typ=='ns':
                ns.add(value)
                nsrr.append((name,value))
            elif typ=='aaaa':
                ip.add(value)

                a4rr.append((name,value))
            elif typ=='a':
                ip.add(value)
                arr.append((name,value))                
            elif typ=='ds':
                ds.add(name)
     


    nsrrdf=pd.DataFrame(nsrr)
    # nsrrdf[':LABEL']='NS'
    nsrrdf.columns = nsrr_cols

    a4rrdf=pd.DataFrame(a4rr)
    # a4rrdf[':LABEL']='AAAA'
    a4rrdf.columns = a4rr_cols

    arrdf=pd.DataFrame(arr)
    # arrdf[':LABEL']='A'
    arrdf.columns = arr_cols
    
    # 这里可以直接导入MySQL
    output = OUTPUTPATH+'/'+tld+'/'
    mkdir(output)
    nsrrdf.to_csv(output+'NS_'+number+'_'+str(len(nsrrdf))+'.csv',index=False)
    if a4rr:
        a4rrdf.to_csv(output+'AAAA_'+number+'_'+str(len(a4rrdf))+'.csv',index=False)
    if arr:
        arrdf.to_csv(output+'A_'+number+'_'+str(len(arrdf))+'.csv',index=False)
    if ds:
        with open(output+'ds_'+str(len(ds))+'.txt','a') as f:
            for i in ds:
                f.write(i)
                f.write('\n')    
    if sld:
        domain_sum+=len(sld)
        all_domain.update(sld)
        with open(output+'domainsum_'+str(len(sld))+'.txt','a') as f:
            for i in sld:
                f.write(i)
                f.write('\n')
    
    del sld
    del ns
    del ip
    del nsrr
    del a4rr
    del arr
    del nsrrdf
    del a4rrdf
    del arrdf   
    del ds 
    
with open(domain_sum_outputpath+'/domainsum_'+DATE+'_'+str(domain_sum)+'.txt','a') as f:
    for i in all_domain:
        if i: f.write(i)
        f.write('\n')
end = time.time()
t=end-begin
# 转换时分秒格式
t = time.strftime("%H:%M:%S", time.gmtime(t))
print('共用时间：',t)


