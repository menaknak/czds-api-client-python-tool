import json
import sys
import cgi
import os
import datetime
import time
import requests

from do_authentication import authenticate
from do_http_get import do_get

# 用于记录进度的检查点文件
CHECKPOINT_FILE = "checkpoint.txt"

# 最大重试次数
MAX_RETRIES = 5
# 每次重试之间的延迟时间（秒）
RETRY_DELAY = 60

##############################################################################################################
# 第一步：从config.json文件获取配置数据
##############################################################################################################

try:
    if 'CZDS_CONFIG' in os.environ:
        config_data = os.environ['CZDS_CONFIG']
        config = json.loads(config_data)
    else:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
except Exception as e:
    sys.stderr.write(f"加载config.json文件出错: {e}\n")
    exit(1)

# config.json文件必须包含以下数据
username = config['icann.account.username']
password = config['icann.account.password']
authen_base_url = config['authentication.base.url']
czds_base_url = config['czds.base.url']

DATE = time.strftime('%Y%m%d', time.localtime())

working_directory = config.get('working.directory', '.') + DATE + "/"  # 默认当前目录加上今天的日期
target_tld_list = config.get('target.tld.list', '.')

if not username:
    sys.stderr.write("'icann.account.username' 参数未在config.json文件中找到\n")
    exit(1)

if not password:
    sys.stderr.write("'icann.account.password' 参数未在config.json文件中找到\n")
    exit(1)

if not authen_base_url:
    sys.stderr.write("'authentication.base.url' 参数未在config.json文件中找到\n")
    exit(1)

if not czds_base_url:
    sys.stderr.write("'czds.base.url' 参数未在config.json文件中找到\n")
    exit(1)


##############################################################################################################
# 第二步：验证用户以获取access_token
# 注意，access_token在之后的所有REST API调用中是全局的
##############################################################################################################

print("验证用户 {0}".format(username))
access_token = authenticate(username, password, authen_base_url)


##############################################################################################################
# 第三步：获取下载区域文件的链接
##############################################################################################################

# 获取区域文件链接的函数定义
def get_zone_links(czds_base_url):
    global access_token

    links_url = czds_base_url + "/czds/downloads/links"
    links_response = do_get(links_url, access_token)

    status_code = links_response.status_code

    if status_code == 200:
        zone_links = links_response.json()
        print("{0}: 要下载的区域文件数量为 {1}".format(datetime.datetime.now(), len(zone_links)))
        return zone_links
    elif status_code == 401:
        print("access_token 已过期。重新验证用户 {0}".format(username))
        access_token = authenticate(username, password, authen_base_url)
        return get_zone_links(czds_base_url)
    else:
        sys.stderr.write("从 {0} 获取区域链接失败，错误代码 {1}\n".format(links_url, status_code))
        return None


# 获取区域链接
zone_links = get_zone_links(czds_base_url)
if not zone_links:
    exit(1)


##############################################################################################################
# 第四步：下载区域文件
##############################################################################################################

def save_checkpoint(tld):
    with open(CHECKPOINT_FILE, 'w') as f:
        f.write(tld)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return f.read().strip()
    return None

# 下载一个区域文件的函数定义
def download_one_zone(url, output_directory):
    print("{0}: 从 {1} 下载区域文件".format(str(datetime.datetime.now()), url))

    global access_token
    retries = 0
    while retries < MAX_RETRIES:
        try:
            download_zone_response = do_get(url, access_token)

            status_code = download_zone_response.status_code

            if status_code == 200:
                # 尝试从头部获取文件名
                _, option = cgi.parse_header(download_zone_response.headers['content-disposition'])
                filename = option.get('filename')

                # 如果无法从头部获取文件名，则生成一个类似[tld].txt.gz的文件名
                if not filename:
                    filename = url.rsplit('/', 1)[-1].rsplit('.')[-2] + '.txt.gz'

                # 这是区域文件将被保存的位置
                path = '{0}/{1}'.format(output_directory, filename)

                with open(path, 'wb') as f:
                    for chunk in download_zone_response.iter_content(1024):
                        f.write(chunk)

                print("{0}: 完成下载区域文件 {1}".format(str(datetime.datetime.now()), path))
                return True

            elif status_code == 401:
                print("access_token 已过期。重新验证用户 {0}".format(username))
                access_token = authenticate(username, password, authen_base_url)
            elif status_code == 404:
                print("未找到 {0} 的区域文件".format(url))
                return False
            else:
                sys.stderr.write('从 {0} 下载区域文件失败，错误代码 {1}\n'.format(url, status_code))
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"连接错误：{e}。重试中...（{retries + 1}/{MAX_RETRIES}）")
            retries += 1
            time.sleep(RETRY_DELAY)
    print(f"下载失败：超过最大重试次数 {MAX_RETRIES}")
    return False

# 下载所有区域文件的函数定义
def download_zone_files(urls, working_directory):

    # 区域文件将保存在一个子目录中
    output_directory = working_directory

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 加载检查点
    checkpoint = load_checkpoint()
    skip = bool(checkpoint)
    count = 0

    # 一个一个地下载区域文件
    for link in urls:
        tld = link.split('/')[-1].split('.')[0]
        if skip:
            if tld == checkpoint:
                skip = False
            continue

        if tld in target_tld_list:
            print(link)
            if download_one_zone(link, output_directory):
                save_checkpoint(tld)
        count += 1
    print('目前已申请成功的TLD zonfile数量：', count)

# 最后，下载所有区域文件
start_time = datetime.datetime.now()
download_zone_files(zone_links, working_directory)
end_time = datetime.datetime.now()

print("{0}: 完成所有区域文件的下载。耗时：{1}".format(str(end_time), (end_time - start_time)))


'''
1.重试机制:

增加了MAX_RETRIES和RETRY_DELAY参数，分别控制最大重试次数和每次重试之间的延迟时间。
在download_one_zone函数中，使用while循环实现重试机制，如果捕捉到requests.exceptions.ConnectionError错误，会进行重试。

2.错误处理:

在每次重试失败后，程序会等待一段时间（由RETRY_DELAY控制）再进行下一次尝试。
如果重试次数超过MAX_RETRIES，则会输出下载失败的消息，并停止下载。
这样，当网络出现问题时，脚本会自动进行重试，提高了下载的可靠性和鲁棒性。
'''