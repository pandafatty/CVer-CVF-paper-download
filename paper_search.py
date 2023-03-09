import requests
from bs4 import BeautifulSoup
import re
import time
from tqdm import tqdm
import pandas as pd

# CVF 首页
cvf_url = "https://openaccess.thecvf.com"

# 创建一个空的DataFrame
data = pd.DataFrame(columns=['i', 'paper_title', 'paper_head_url', 'pdf_url', 'abstract'])


# 会议链接列表
urls = ["https://openaccess.thecvf.com/WACV2023",
        "https://openaccess.thecvf.com/CVPR2022?day=all",
        "https://openaccess.thecvf.com/WACV2022",
        "https://openaccess.thecvf.com/ICCV2021?day=all",
        "https://openaccess.thecvf.com/CVPR2021?day=all",
        "https://openaccess.thecvf.com/WACV2021",
        "https://openaccess.thecvf.com/CVPR2020?day=2020-06-16",
        "https://openaccess.thecvf.com/CVPR2020?day=2020-06-17",
        "https://openaccess.thecvf.com/CVPR2020?day=2020-06-18",
        "https://openaccess.thecvf.com/WACV2020"]
# 待搜索的关键字列表
keywords = ["point", "avder", "out of distribution"]

for url in urls:
    print('正在检索的会议：', url)
    try:
        # 获取会议页面的HTML文档
        head_response = requests.get(url, verify=True)
        head_response = head_response.content.decode("iso-8859-1")
        head_soup = BeautifulSoup(head_response, "html.parser")

        i = 0
        print("开始检索符合要求的论文。")
        for paper in tqdm(head_soup.find_all("dt")):
            time.sleep(0.1)
            # print('本会议中符合要求的第 %d 篇论文！' % i)
            
            # 搜索论文的url
            match_url = re.search(r'<a href="(.+?)">', str(paper))
            if match_url: 
                paper_url = match_url.group(1)
                # print("paper_url:", paper_url)
                
            # 搜索论文的标题
            match_title = re.search(r'<a href=".+?">(.+?)</a>', str(paper))
            if match_title: 
                paper_title = match_title.group(1)
                # print("paper_title:", paper_title)
                
            # 搜索论文的摘要 pdf
            if paper_url is not None and paper_title is not None:
                paper_head_url = cvf_url + paper_url
                # print("paper_head_url:", paper_head_url)
                paper_head_response = requests.get(paper_head_url, verify=True)
                paper_head_response = paper_head_response.content.decode("iso-8859-1")
                paper_head_soup = BeautifulSoup(paper_head_response, "html.parser")

                abstract = paper_head_soup.find("div", {"id": "abstract"}).text # 摘要内容
                # print("abstract:", abstract)
                
                for down in paper_head_soup.find_all("dd"):
                    if "pdf" in str(down):
                        match_pdf = re.search(r'<a href="(.*?.pdf)">pdf</a>', str(down))
                        if match_pdf:
                            pdf_url = cvf_url + match_pdf.group(1)
                            # print("pdf_url:", pdf_url)
                            
            if any(keyword in paper_title.lower() or keyword in abstract.lower() for keyword in keywords):
                i = i + 1
                print('本会议中符合要求的第 %d 篇论文！' % i)
                print("paper_title:", paper_title)
                print("paper_head_url:", paper_head_url)
                print("pdf_url:", pdf_url)
                print("abstract:", abstract)
                
                 # 将信息添加到DataFrame中
                data.loc[len(data)] = [i, paper_title, paper_head_url, pdf_url, abstract]

                
                # 下载pdf文件
                file_name = paper_title + '.pdf'
                file_path = '/mnt/data/zhaowenyu/paper_download/' + file_name
                # 发送GET请求到URL
                pdf_down = requests.get(pdf_url, verify=True)
                # 将响应内容写入文件
                with open(file_path, 'wb') as f:
                    f.write(pdf_down.content)
                
            # if i == 1:
            #     break
        
        # 将DataFrame保存为Excel表格
        data.to_excel('papers_list.xlsx', index=False)
            
            
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Connection Error:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Error:", err)
        
print("检索完毕！")