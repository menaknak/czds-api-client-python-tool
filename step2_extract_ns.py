from pprint import pprint as pp
import pandas as pd
import time
from collections import Counter,defaultdict
import os
import sys

def getfilelist(cur_path):
    filelist=[]
    for parent,dirs,files in os.walk(cur_path):
        flist=list(map(lambda x:os.path.join(parent,x),files))
        filelist.extend(flist)
    return filelist

# DATE = time.strftime('%Y%m%d',time.localtime())

# PATH='/home/nly/DNS/CZDS/data/phase1_zonefile_extraction/'+DATE+'/'
PATH = sys.argv[-1]+'/'
allfilelist = getfilelist(PATH)

from tqdm import tqdm
filelist = [i for i in allfilelist if 'NS' in os.path.basename(i)]
extract_set = set()
for f in tqdm(filelist):
    # print(f)
    df = pd.read_csv(f)
    extract_set.update(df['hostname'])
    del df

save_filename = PATH+'ns_set.txt'
with open(save_filename,'w') as f:
    for i in extract_set:
        i = i.rstrip('.')
        f.write(i)
        f.write('\n')