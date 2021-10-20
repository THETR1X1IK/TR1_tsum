import requests
import json
import time
from threading import Thread
import random
from datetime import datetime
from dhooks import Webhook, Embed
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import json


class TsumMonitor():
    def __init__(self, webhooks, refresh_time):
        self.webhooks = webhooks
        self.refresh_time = refresh_time
        self.latest_status = ""
        self.proxies = []
        self.load_proxies()
        self.products = []
        self.headers = {'Host': 'www.tsum.ru', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
        self.headers_api = {'Host': 'api.tsum.ru', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}

    def log(self, msg):
        print("[{}]: {}".format(datetime.now(), msg))

    def load_proxies(self):
        self.proxies = open("proxies.txt").readlines()

    def get_random_ua(self):
        return random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36"
        ])

    def format_proxy(self, proxy):
        try:
            ip = proxy.split(":")[0]
            port = proxy.split(":")[1]
            userpassproxy = '%s:%s' % (ip, port)
            proxyuser = proxy.split(":")[2].rstrip()
            proxypass = proxy.split(":")[3].rstrip()
            proxies = {'http': 'http://%s:%s@%s' % (proxyuser, proxypass, userpassproxy),
                       'https': 'http://%s:%s@%s' % (proxyuser, proxypass, userpassproxy)}
        except:
            proxies = {'http': 'http://%s' % proxy, 'https': 'http://%s' % proxy}
        return proxies

    def start(self):
        t = Thread(target=self.monitor_thread)
        t.start()

    def monitor_thread(self):
        while True:
            try:
                pids = open("pids.txt").read().split()
                if len(self.proxies) > 0:
                    req = requests.get(
                        'https://www.tsum.ru/catalog/krossovki-19014/?brand=3982509,2030075,2165673&availability=2&sort=date',
                        proxies=self.format_proxy(random.choice(self.proxies)),
                        headers=self.headers)
                else:
                    req = requests.get(
                        'https://www.tsum.ru/catalog/krossovki-19014/?brand=3982509,2030075,2165673&availability=2&sort=date',
                        headers=self.headers)
                soup = BeautifulSoup(req.content, 'html5lib')
                ps = soup.findChildren('p', attrs={'class': 'product__description'},
                                       text=re.compile(
                                           '(\W|^)[Yy][Ee][Ee][Zz][Yy]|[Nn][Ii][Kk][Ee]|[F][f][E][e][A][a][R][r]|[G][g][O][o][D][d](\W|$)'))
                for p in ps:
                    parent_div = p.findParent('div', attrs={'class': ['product-list__item', 'ng-star-inserted']})
                    link = parent_div.findChildren('a', attrs={'class': 'product__info'})[0].get('href')
                    price = parent_div.findChildren('span', attrs={'class': ['product__price', 'ng-star-inserted']})[
                        0].text
                    info = json.loads(requests.get(
                        'https://api.tsum.ru/catalog/item/{}'.format(link.split('/')[len(link.split('/')) - 2]),
                        headers=self.headers_api,
                        timeout=10).text)
                    img = info['photos'][0]['middle']
                    name = info['title']
                    pid = info['code_vnd']
                    sizes = list(filter(lambda x: x['availabilityInStock'], info['skuList']))
                    sizes_str1 = ''
                    sizes_str2 = ''
                    sizes_str3 = ''
                    if len(sizes) == 0:
                        status = 'OUT OF STOCK'
                    else:
                        if len(sizes) < 7:
                            for size in sizes:
                                size_num = size['size_vendor_name']
                                size_pid = size['id']
                                sizes_str1 = sizes_str1 + '[{}](https://tr1.com/pages/tsum?v={})'.format(size_num,
                                                                                                         size_pid) + "\n"
                        if (len(sizes) < 13) & (len(sizes) > 6):
                            b1 = round(len(sizes) / 2)
                            qwe1 = sizes[:b1]
                            qwe2 = sizes[b1:]
                            for size in qwe1:
                                size_num = size['size_vendor_name']
                                size_pid = size['id']
                                sizes_str1 = sizes_str1 + '[{}](https://tr1.com/pages/tsum?v={})'.format(size_num,
                                                                                                         size_pid) + "\n"
                            for size in qwe2:
                                size_num = size['size_vendor_name']
                                size_pid = size['id']
                                sizes_str2 = sizes_str2 + '[{}](https://tr1.com/pages/tsum?v={})'.format(size_num,
                                                                                                         size_pid) + "\n"
                        if len(sizes) > 12:
                            b1 = round(len(sizes) / 3)
                            b3 = b1 + b1
                            qwe1 = sizes[:b1]
                            qwe2 = sizes[b1:b3]
                            qwe3 = sizes[b3:]
                            for size in qwe1:
                                size_num = size['size_vendor_name']
                                size_pid = size['id']
                                sizes_str1 = sizes_str1 + '[{} uk](https://tr1.com/pages/tsum?v={})'.format(size_num,
                                                                                                            size_pid) + "\n"
                            for size in qwe2:
                                size_num = size['size_vendor_name']
                                size_pid = size['id']
                                sizes_str1 = sizes_str1 + '[{} uk](https://tr1.com/pages/tsum?v={})'.format(size_num,
                                                                                                            size_pid) + "\n"
                            for size in qwe3:
                                size_num = size['size_vendor_name']
                                size_pid = size['id']
                                sizes_str1 = sizes_str1 + '[{} uk](https://tr1.com/pages/tsum?v={})'.format(size_num,
                                                                                                            size_pid) + "\n"
                        status = 'IN STOCK'
                    product = {'name': name, 'link': link, 'pid': pid, 'price': price, 'sizes': sizes,
                               'sizes1': sizes_str1, 'sizes2': sizes_str2, 'sizes3': sizes_str3, 'img': img,
                               'status': status}
                    buff_product = list([x for x in self.products if link in x.values()])
                    if info['id'] not in pids:
                        if len(buff_product) == 0:
                            self.products.append(product)
                            self.send_to_discord(product, 'ITEM')
                            self.log('new item {}'.format(product['name']))
                        else:
                            if buff_product[0]['status'] != product['status']:
                                self.products.remove(buff_product[0])
                                self.products.append(product)
                                self.send_to_discord(product, 'STOCK')
                                self.log('new stock {}'.format(product['name']))
                            if buff_product[0]['sizes'] != product['sizes']:
                                self.products.remove(buff_product[0])
                                self.products.append(product)
                                self.send_to_discord(product, 'STOCK')
                                self.log('new stock {}'.format(product['name']))
            except Exception as e:
                self.log("Error: " + str(e))
            time.sleep(self.refresh_time)

    def send_to_discord(self, product, kind):
        embed = Embed(
            title="{} on Tsum.ru".format(product['name']),
            url='https://www.tsum.ru' + product['link'],
            color=2544107,
            timestamp='now'
        )

        embed.add_field(name='**Status**', value='NEW ' + kind, inline=True)
        embed.add_field(name='**Stock Status**', value=product['status'], inline=False)
        embed.add_field(name='**Pid**', value=product['pid'], inline=True)
        embed.add_field(name='**Price**', value=product['price'], inline=False)
        if product['status'] != 'OUT OF STOCK': embed.add_field(name='**Sizes**', value=product['sizes1'],
                                                                inline=(product['sizes2'] != ''))
        if product['sizes2'] != '': embed.add_field(name='**Sizes**', value=product['sizes2'],
                                                    inline=(product['sizes2'] != ''))
        if product['sizes3'] != '': embed.add_field(name='**Sizes**', value=product['sizes3'],
                                                    inline=(product['sizes2'] != ''))
        embed.add_field(name='**Useless links**',
                        value='[Orders](https://www.tsum.ru/personal/orders) \n[Cart](https://www.tsum.ru/cart/) \n[Checkout](https://www.tsum.ru/checkout/) \n',
                        inline=False)
        embed.set_thumbnail(product['img'])

        embed.set_footer(text="THETR1XIK",
                         icon_url="https://sun9-16.userapi.com/impg/_6R59Fdndj2Pf-Iah-luprDvUMoLmpTJNJuwtQ/JD07kUgPelg.jpg?size=640x800&quality=96&proxy=1&sign=1f9b9db79ebf30a3a4e3aff1054925ff&type=album")

        for webhook in self.webhooks:
            try:
                hook = Webhook(webhook)
                hook.username = "Tsum Monitor"
                hook.avatar_url = "https://sun9-16.userapi.com/impg/_6R59Fdndj2Pf-Iah-luprDvUMoLmpTJNJuwtQ/JD07kUgPelg.jpg?size=640x800&quality=96&proxy=1&sign=1f9b9db79ebf30a3a4e3aff1054925ff&type=album"
                hook.send(embed=embed)
                self.log("Posted status update to Discord webhook {}".format(webhook))
            except Exception as e:
                self.log("Error sending to Discord webhook {}".format(e))
