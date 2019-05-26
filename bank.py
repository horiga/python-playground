#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

from __future__ import print_function

import sys
import requests
import json
import argparse
from bs4 import BeautifulSoup
from six import PY2


ZENGIN_URL="https://zengin.ajtw.net"
ZIP_CODE_URL="https://postsearch.hikak.com"
SP="/-\\|"


def get_bank_data(abg, progress=False):
    index = 0
    bank_data = []

    payload = {'abg': abg}
    response = requests.get("%s/linkmeisai.php" % (ZENGIN_URL), params=payload)
    if progress:
        print("* Scraping '%s'." % (response.url))
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("div", attrs={"class", "ln61"})

    for link in links:
        alink = "%s/%s" % (ZENGIN_URL, link.a.get("href"))
        shop_html = requests.get(alink).content
        shop_soup = BeautifulSoup(shop_html, "html.parser").find_all("td", attrs={"class", "b54"})

        shop_address = shop_soup[6].text.strip().rstrip(u" ［郵便番号］［地図表示］")
        shop_zip_code_url = shop_soup[6].a

        shop_data = {
                'bank_name': shop_soup[0].text.strip(),
                'bank_name_kana': shop_soup[1].text.strip(),
                'bank_code': shop_soup[2].text.strip(),
                'shop_name': shop_soup[3].text.strip(),
                'shop_name_kana': shop_soup[4].text.strip(),
                'shop_code': shop_soup[5].text.strip(),
                'shop_address': shop_address if shop_address != u"-" else u"",
                'shop_zip_code': get_zip_code(shop_zip_code_url.get("href")) if shop_zip_code_url else u"",
                'shop_telephone': shop_soup[7].text.strip()
                }

        bank_data.append(shop_data)
        if progress:
            index += 1
            EOP = index == len(links)
            print(u"\r%s (%d/%d)%s" % ("DONE" if EOP else SP[index%4],
                index, len(links), "\n" if EOP else ""), end="")
            sys.stdout.flush()

    return bank_data


def get_zip_code(url):
    if not url and not url.startswith(ZIP_CODE_URL):
        return u""

    zip_code_html = requests.get(url).content
    zip_code_soup = BeautifulSoup(zip_code_html, "html.parser")
    zip_code = zip_code_soup.find("div", attrs={"class", "a26"})

    return zip_code.text.strip().lstrip(u"〒") if zip_code else u""


def main():
    parser = argparse.ArgumentParser(description='金融機関コード・銀行コード・支店コード スクレイパー')
    parser.add_argument('abg', help='金融機関コード')
    parser.add_argument('-f', '--format', default='sql', choices=['sql', 'json'], help="output format (Default: sql)")
    parser.add_argument('-o', '--output', help="output filepath (None: stdout)")
    parser.add_argument('-s', '--silent', action='store_true', help="silent progress info")
    args = parser.parse_args()

    bank_data = get_bank_data(args.abg, progress=not args.silent)

    if args.format == 'sql':
        queries = []
        for bank_item in bank_data:
            queries.append(u"insert into bank(`bank_code`,`shop_code`,`bank_name_kana`,`bank_name`,`shop_name_kana`,`shop_name`,`shop_zip_code`,`shop_address`,`shop_telephone`) values('%(bank_code)s','%(shop_code)s','%(bank_name_kana)s','%(bank_name)s','%(shop_name_kana)s','%(shop_name)s','%(shop_zip_code)s','%(shop_address)s','%(shop_telephone)s')" % bank_item)
        output = "\n".join(queries)
    else:
        output = json.dumps(bank_data, indent=4, ensure_ascii=False)

    if args.output:
        with open(args.output, 'w') as file:
            if PY2:
                file.write(output.encode('utf-8'))
            else:
                file.write(output)
    else:
        if PY2:
            print(output.encode('utf-8'))
        else:
            print(output)


if __name__ == "__main__":
    main()
