# coding: UTF-8
from urllib import request
from bs4 import BeautifulSoup

url = "https://zengin.ajtw.net/linkmeisai.php?abg=0137"
html = request.urlopen(url).read().decode('utf-8')
soup = BeautifulSoup(html,"html.parser")
links = soup.find_all("div", attrs={"class", "ln61"})

for link in links:
	bank_data = {}
	alink = "https://zengin.ajtw.net/" + link.a.get("href")
	shop_html = request.urlopen(alink).read().decode('utf-8')
	shop_parser = BeautifulSoup(shop_html,"html.parser")
	values = shop_parser.find_all("td", attrs={"class", "b54"})
	bank_data['bank_name'] = values[0].text.strip()
	bank_data['bank_name_kana'] = values[1].text.strip()
	bank_data['bank_code'] = values[2].text.strip()
	bank_data['shop_name'] = values[3].text.strip()
	bank_data['shop_name_kana'] = values[4].text.strip()
	bank_data['shop_code'] = values[5].text.strip()
	bank_data['shop_address'] = values[6].text.strip().rstrip(" ［郵便番号］［地図表示］")
	if bank_data['shop_address'] == "-":
		bank_data['shop_address'] = ""
	shop_zip_code = ""
	if values[6].a is not None:
		zip_code_search_url = values[6].a.get("href")
		if zip_code_search_url is not None and zip_code_search_url.startswith("https://postsearch.hikak.com"):
			zip_code_html = request.urlopen(zip_code_search_url).read().decode('utf-8')
			zip_code_parser = BeautifulSoup(zip_code_html, "html.parser")
			tmp = zip_code_parser.find("div", attrs={"class", "a26"})
			if tmp is not None:
				shop_zip_code = tmp.text.lstrip("〒")
	bank_data['shop_zip_code'] = shop_zip_code
	bank_data['shop_telephone'] = values[7].text.strip()
	if bank_data['shop_telephone'] == "-":
		bank_data['shop_telephone'] = ""
	print(bank_data)
