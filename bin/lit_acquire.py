import requests
from lxml import etree
import time
import re

def get_results(term):
    url = f'https://pubmed.ncbi.nlm.nih.gov/?term={term}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",

    }
    r = requests.get(url, headers=headers)
    r.encoding = 'utf-8'
    tree = etree.HTML(r.text)
    results = tree.xpath('//div[@class="results-amount"]/span/text()')
    if len(results) !=0:
        new_results = str(results[0]).replace("\n","")
        print(f"Found {new_results} results")
        end_results = int(new_results.replace(",",""))#字符串中含有，号无法转换成数字，我们用空来替代它
        if end_results % 10 == 0:
            pages = end_results / 10
        else:
            pages = int(end_results/10)+1
        print(f"Total of {str(pages)} papes")
    else:
        print("No result found!")
        pages = 0
    return pages

def get_links(term,pages):
    total_list = []
    for i in range(pages):
        url = f'https://pubmed.ncbi.nlm.nih.gov/?term={term}&page={str(i+1)}'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",

        }
        r = requests.get(url,headers=headers)
        r.encoding='utf-8'
        tree =etree.HTML(r.text)
        links = tree.xpath('//div[@class="docsum-content"]/a/@href')
        for link in links:
            #构造单个文献的链接
            new_link = 'https://pubmed.ncbi.nlm.nih.gov' + link
            total_list.append(new_link)
        time.sleep(3)
    return total_list


def get_message(total_list):
    title_list = []
    doi_list = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    }
    for url in total_list:
        r = requests.get(url, headers=headers)
        r.encoding = 'utf-8'
        tree = etree.HTML(r.text)
        title = tree.xpath('//h1[@class="heading-title"]/text()')[0]
        new_title = str(title).replace("\n", "")
        doi = tree.xpath('//span[@class="citation-doi"]/text()')
        if len(doi) == 0:
            print("There is no doi for paper '%s'"%new_title[26:])
        else:
            new_dois = str(doi[0]).replace(" ", "")
            new_doi = new_dois[5:-2]
            title_list.append(new_title[26:])
            doi_list.append(new_doi)
            print(f"{new_doi} is the doi for paper %s"%new_title[26:])
    return doi_list, title_list


def get_content(dois,titles):
    for i in range(len(dois)):
        doi = dois[i]
        til = titles[i]
#    for doi in dois:
        urls = f'https://sci.bban.top/pdf/{doi}.pdf#view=FitH'
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
        }
        r = requests.get(urls, headers=headers)
        if r.status_code == 404:
            print("Doi %s cannot be found on sci-hub, title is %s"%(doi,til))
        else:
            title = re.findall("(.*?)/",doi)
            with open(f"{title[0]}.pdf",'wb')as f:
                f.write(r.content)
                time.sleep(2)

if __name__ == '__main__':
    term = input("Please input your key terms for the search: ")
    print("Searching....")
    if get_results(term) != 0:
        page = int(input("Please input how many pages of articles you want to download, each page has 10 articles："))
        print("正在下载文献，注意只能下载含doi号的文献 (downloading the ones with a doi)")
        total_list = get_links(term,page)
        doi_list,title_list = get_message(total_list)
        get_content(doi_list,title_list)
        print("Downloading finished")
    else:
        print("Sorry, there is no paper can be downloaded")
