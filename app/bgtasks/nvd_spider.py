import operator
import re
from functools import reduce
import pymongo
import requests
from bs4 import BeautifulSoup

from app.core.celery_app import celery_app
from app.core.config import settings


def get_matching_records(product, vendor=None, version='-'):
    url = 'https://nvd.nist.gov/vuln/search/results'
    try:
        if vendor:
            params = {
                "query": f"cpe:2.3:a:{vendor}:{product}:{version}:*:*:*:*:*:*:*",
                "startIndex": 0
            }
        else:
            params = {
                "query": f"cpe:2.3:a::{product}:{version}:*:*:*:*:*:*:*",
                "startIndex": 0
            }
        r = requests.get(url, params=params)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        r.close()
        matching_records = soup.find('strong', attrs={'data-testid': 'vuln-matching-records-count'}).get_text()
        matching_records = matching_records.replace(',', '')
        matching_records = int(matching_records)
        # 匹配漏洞过多时进行裁剪 爬取页数太多会严重影响爬取速度
        if matching_records > 100:
            matching_records = 100
        return matching_records
    except Exception as err:
        print('running in get_matching_records err')
        print(err)
        print('Failed')
        return None


def get_one_page(index, product, vendor=None, version='-'):
    url = 'https://nvd.nist.gov/vuln/search/results'
    try:
        cve_info = []
        if vendor:
            params = {
                "query": f"cpe:2.3:a:{vendor}:{product}:{version}:*:*:*:*:*:*:*",
                "startIndex": index
            }
        else:
            params = {
                "query": f"cpe:2.3:a::{product}:{version}:*:*:*:*:*:*:*",
                "startIndex": index
            }
        r = requests.get(url, params=params)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        r.close()
        trs = soup.find_all('tr', attrs={'data-testid': re.compile(r'vuln-row-(\d+)?')})
        """
        text
        \n\nCVE-2020-6498\n\n\nIncorrect implementation in user interface in Google Chrome on iOS prior to 83.0.4103.88
         allowed a remote attacker to perform domain spoofing via a crafted HTML page.
         \nPublished:\nJune 03, 2020; 07:15:12 PM -04:00\n\n\n\nV3.1: 6.5 MEDIUM\n\n\n\xa0\xa0\xa0\xa0V2: 4.3 MEDIUM\n\n\n'
        """
        for tr in trs:
            tr = tr.get_text()
            tr = tr.replace('\n', '').replace('\xa0', '')
            # print(tr)
            find = (
                re.search(r'(?P<cve>CVE-\d{4}-\d{4,5})(?P<summary>.*?)(?P<published>Published:.*?)(?P<level>V.*)', tr)
            )
            find_dict = find.groupdict()
            if 'HIGH' in find_dict['level'] or 'CRITICAL' in find_dict['level']:
                # V3.1: 6.5 MEDIUMV2: 4.3 MEDIUM
                score = level = None
                str_list = find_dict['level'].split('V')
                # ['', '3.1: 6.5 LOW', '2: 4.3 CRITICAL']
                try:
                    if 'HIGH' in str_list[1] or 'CRITICAL' in str_list[1]:
                        level_score = str_list[1].split()
                        score = level_score[1]
                        level = level_score[2]
                    else:
                        level_score = str_list[2].split()
                        score = level_score[1]
                        level = level_score[2]
                except IndexError:
                    pass
                tmp = {
                    'cve': find_dict.get('cve'),
                    'summary': find_dict.get('summary'),
                    'published': find_dict.get('published'),
                    'level': level,
                    'score': score,
                    'detail': f'https://nvd.nist.gov/vuln/detail/{find_dict.get("cve")}',
                }
                cve_info.append(tmp)
        return cve_info
    except Exception as err:
        print('running in get_one_page err')
        print(err)
        print('Failed')
        return []


def get_all_page(start_indexes, app):
    res = []
    for start_index in start_indexes:
        print(f'start_index: {start_index}')
        res.append(get_one_page(start_index, **app))
    # res = [get_one_page(start_index, **app) for start_index in start_indexes]
    # with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    #     res.extend(executor.map(partial(get_one_page, **app), start_indexes))
    res = reduce(operator.add, res)
    return res


def handle_app_info(app):
    handled_app = {}
    product = app.get('product')
    version = app.get('version')
    vendor = app.get('vendor')
    handled_app['product'] = product
    handled_app['version'] = version
    handled_app['vendor'] = vendor
    product_list = []
    vendor_list = []
    if product:
        product_list = product.split(' ')
    if vendor:
        vendor_list = vendor.split(' ')

    if product and len(product_list) > 1:
        for item in product_list:
            if item in ['版本', 'version', 'Version', '-', '–']:
                product_list.remove(item)

        handled_app['product'] = '_'.join(product_list)

        for index, item in enumerate(product_list):
            if item.count('.') >= 1 and item != '.NET' and index >= 1:
                if index == 1:
                    handled_app['product'] = product_list[0]
                else:
                    handled_app['product'] = '_'.join(product_list[:index])
                handled_app['version'] = item.strip('Vv()')
                break
        # 特殊应用处理
        if 'Chrome' in product or 'chrome' in product:
            handled_app['product'] = 'chrome'

    if vendor and len(vendor_list) > 1:
        handled_app['vendor'] = None

    if version and version == '':
        handled_app['version'] = '-'

    print(f'after handle app info: {handled_app}')
    return handled_app


def get_one_app(app, update):
    client = pymongo.MongoClient(host=settings.MONGO_HOST)
    try:
        db = client.cves
        collection = db.app_spider
        # 应用名称、版本确定唯一一条数据
        query = {'product': app.get('product'), 'version': app.get('version'), 'vendor': app.get('vendor')}
        res = collection.find_one(query)
        # print(f'get_one_app res: {res}')
        if res is None or update:
            # 没有记录，启动爬虫
            print("=================================================================================>Running in spider")
            # 对app信息进行NVD查询友好性处理
            handled_app = handle_app_info(app)
            matching_records = get_matching_records(**handled_app)
            print(f'NVD matching records: {matching_records}')
            if matching_records:
                pages = matching_records // 20 + 1
                start_indexes = []
                for i in range(pages):
                    start_indexes.append(i * 20)
                res = {'vendor': app.get('vendor'), 'product': app.get('product'),
                       'version': app.get('version'),
                       'cves': get_all_page(start_indexes, handled_app)}
                print('*' * 40)
                print(f'Get one product res len: {len(res["cves"])}')
                print('*' * 40)
            else:
                # NATIONAL VULNERABILITY DATABASE没有收录此版本信息 cve为None
                res = {'vendor': app.get('vendor'), 'product': app.get('product'),
                       'version': app.get('version'), 'cves': None}
                print('*' * 40)
                print('Get one product res len: 0')
                print('*' * 40)
            # 数据入库
            if update:
                new = {"$set": res}
                collection.update_one(query, new, upsert=True)
            else:
                collection.insert_one(res)
            # print(f'{res["product"]} spider res: {res}')
            print('======================================================================================>Running over')
            return res
        else:
            # apps库中有记录直接返回 或者查看更新标志是否需要更新数据
            print(f"{app.get('product')} has a record")
            return res
    except Exception as err:
        # 爬取过程中报错 返回None
        print('running in get_one_app err')
        print(err)
        print('Failed')
        return {"vendor": app.get('vendor'), "product": app.get('product'),
                "version": app.get('version'), 'cves': None}
    finally:
        client.close()


def get_all_app(apps, update):
    res = []
    for app in apps:
        print(f'before handle app info: {app}')
        res.append(get_one_app(app, update))
    # with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    #     res.extend(executor.map(get_one_app, apps))
    return res


@celery_app.task(acks_late=True)
def spider(data):
    # 爬取数据
    # 更新数据到postgreSQL
    # 失败自动重试
    print('Total apps nums ', len(data['apps']))
    length = len(data['apps'])
    update = data['update']
    start = 0
    end = 20
    res = {"apps": []}
    while length > 0:
        tmp = data.get('apps')[start:end]
        res['apps'].extend(get_all_app(tmp, update))
        start = end
        end += 20
        length -= 20

