import requests
import json
from bs4 import BeautifulSoup

def billJSON_to_title(bill_json:str) -> str:
    try:
        return bill_json['title']
    except KeyError as e:
        return ''

def billJSON_to_ID(bill_json:str) -> str:
    try:
        return bill_json['packageId']
    except KeyError as e:
        return ''

def billJSON_to_str(bill_json:str,key) -> str:
    try:
        url = bill_json['download']['txtLink']
        text = requests.get(url + '?api_key=' +key).text
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text()
    except KeyError as e:
        return ''

def billJSON_to_sponsors(bill_json:str) -> str:
    try:
        string = ""
        members = bill_json['members']
        for member in members:
            string += member['memberName'] + "\t" + member['party'] + "\t" + member['state'] + "\t" + member['role'] + '\n'
        return string
    except KeyError as e:
        return ''
def get_billUrls_on_page(url:str,key:str):
    print(url)
    response = requests.get(url + '&api_key=' +key)
    data = response.json()
    try:
        bills = data['packages']
    except KeyError as e:
        return []
    billUrls = []
    for bill in bills:
        billUrls.append(bill['packageLink'])
        print(bill['packageLink'])
    return billUrls
    

def get_all_pages(start_url:str,key:str) -> list:
    pages = []
    url = start_url
    while True:
        print(url)
        pages.append(url)
        response = requests.get(url + '&api_key=' +key)
        data = response.json()
        if 'nextPage' not in data:
            pages.append(url)
            break
        url = data['nextPage']
    return pages

def make_bills_txt(start_url:str,key:str) -> None:
    pages = get_all_pages(start_url,key)
    bill_urls = []
    for page in pages[0:]:
        urls = get_billUrls_on_page(page,key)
        bill_urls.extend(urls)
    counter = 0
    for url in bill_urls:
        try:
            response = requests.get(url + '?api_key=' +key)
        except:
            continue
        data = response.json()
        json_to_txt(data,key)
        print(counter / len(url))
        counter += 1

def json_to_txt(summary_json, key):
    title = billJSON_to_title(summary_json)
    sponsors = billJSON_to_sponsors(summary_json)
    text = billJSON_to_str(summary_json, key)

    txt = title + '&&&' + sponsors + '&&&' + text
    with open(billJSON_to_ID(summary_json) + '.txt', 'w') as f:
        f.write(txt)


#===============================================================================================================================================================
if __name__ == "__main__":
    #Using GovInfo API
    key = 'NkkBLpXzxJX7QM440RhZy7G7iQaR3mc9xuSa2qWv'
    start_url = 'https://api.govinfo.gov/collections/BILLS/2021-01-01T00:00:00Z/?offset=0&pageSize=100'
    make_bills_txt(start_url, key)
    
    
        
