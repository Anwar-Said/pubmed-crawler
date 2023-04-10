import requests
from bs4 import BeautifulSoup
import csv
import sys
import time

# search_terms = ['lpin1', 'hmox', 'acp1', 'Card11', 'Snca', 'Adgrg1', 'Adgrg5', 'odc1', 'Ciita', 'ccl2']
search_query = sys.argv[1]
# search_query = 'fexuprazan'
# search_query = '(' + ' OR '.join(search_terms) + ')'
base_url = 'https://pubmed.ncbi.nlm.nih.gov/?term='
# base_url = sys.argv[2]
query_url = base_url + search_query
# print(query_url)
retmax = 100  
page = 1 
file_name = search_query
file_name = file_name.replace(" ","_")
# output_name = sys.argv[2]
params = {"q":query_url,"retmax": retmax, "page": page}
file = open(file_name+'.csv', mode='w', newline='')
writer = csv.writer(file)
sleep_counter= 0
print("processing search results for query ", search_query)
print("please enclose your query in quotes ('query') if there are more than one words. ")
base_url = query_url
while(True):
    # print(query_url)
    try:
        response = requests.get(query_url)
    except:
        print("server not responding! waiting for 3 seconds and trying again")
        time.sleep(3)
        sleep_counter +=1
        if sleep_counter>5:
            print("server didn't respond! closing the connection")
            break
        continue
    # print(response.content)
    soup = BeautifulSoup(response.content, 'html.parser')
    paper_summaries = soup.find_all('article', {'class': 'full-docsum'})
    for summary in paper_summaries:
        paper = summary.find('a', {'class': 'docsum-title'})
        attr = paper.attrs
        # print(attr)
        article_id = attr.get('data-article-id')
        pmid = attr.get('href').split('/')[-2]
        # pmid = summary.find('a', {'class': 'docsum-link'}).get('href').split('/')[-1]
        abstract_url = 'https://pubmed.ncbi.nlm.nih.gov/' + pmid + '/?format=abstract'
        # Send GET request to abstract URL and parse HTML response
        abstract_response = requests.get(abstract_url)
        abstract_soup = BeautifulSoup(abstract_response.content, 'html.parser')
        heading_title = abstract_soup.find('h1',{'class':'heading-title'}).text.strip()
        abstract = abstract_soup.find('div', {'class': 'abstract'}).text.strip().replace("\n","").replace("                          ",":")
        to_write = [article_id,heading_title,abstract]
        writer.writerow(to_write)
        file.flush()
    
    page += 1 
    params["page"] = page

    # print(params)
    print("page {} processed!".format(page))
    next_btn = soup.find("button", class_="button-wrapper next-page-btn")
    # print(next_btn.attrs)
    if next_btn.has_attr('disabled') or len(paper_summaries)==0 or page==50:
        print('data processed successfully!')
        break
    else:
        query_url = base_url+'&page='+str(page)
file.close()
