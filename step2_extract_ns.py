from pprint import pprint as pp
import pandas as pd
import time
from collections import Counter, defaultdict
import os
import sys

def getfilelist(cur_path):
    filelist = []
    for parent, dirs, files in os.walk(cur_path):
        flist = list(map(lambda x: os.path.join(parent, x), files))
        filelist.extend(flist)
    return filelist

# DATE = time.strftime('%Y%m%d', time.localtime())

# PATH='/home/nly/DNS/CZDS/data/phase1_zonefile_extraction/'+DATE+'/'
PATH = sys.argv[-1] + '/'
allfilelist = getfilelist(PATH)

from tqdm import tqdm
filelist = [i for i in allfilelist if 'NS' in os.path.basename(i)]
extract_set = set()
for f in tqdm(filelist):
    try:
        df = pd.read_csv(f)
        extract_set.update(df['hostname'])
        del df
    except UnicodeDecodeError:
        print(f"跳过文件: {f}，因为存在编码错误。")
    except Exception as e:
        print(f"处理文件 {f} 时遇到错误: {e}")

save_filename = PATH + 'ns_set.txt'
with open(save_filename, 'w') as f:
    for i in extract_set:
        i = i.rstrip('.')
        f.write(i)
        f.write('\n')


'''
在读取文件时，用try...except块包裹pd.read_csv(f)。
捕获UnicodeDecodeError异常，打印出错误信息并跳过当前文件。
捕获其他可能的异常，打印错误信息，防止脚本因其他意外情况终止。
'''