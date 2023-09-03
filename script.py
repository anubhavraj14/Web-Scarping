import requests
from bs4 import BeautifulSoup
import csv
import json
import pandas as pd

url = 'https://fame2.heavyindustries.gov.in/ModelUnderFame.aspx'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table', class_='rifine-search_forFront')

columns = [
    'Manufacturer', 'xEV Model Name', 'Variant Name', 'Vehicle Type & Segment',
    'Vehicle CMVR Category', 'Incentive Amount (In INR)', 'Status', 'Links', 'JSON Data'
]
models=[]
td=[]
for row in table.findAll('tr'):
    if(len(row)==3):

        table_data = row.findAll('td')
        # print(len(table_data))  => 0 once => for empty row and no columns
        # that's why bool used 
        if(bool(table_data)):

            # to return b tag under itemplate  then we will get b tag => its next sibling is our text 
            #and then strip => to remove any whitwspace or next lne characters

            oem_name = table_data[0].select_one('itemtemplate b').next_sibling.strip()

            #from [1:]=> exclude 1st one as it will be headers only
            t= table_data[0].find('table', class_='main_table').find_all('tr')[1:]
            length= len(t)

            for row in range (0,length):
                td_tags = t[row].find_all('td')
                data_list = [td.get_text(strip=True) for td in td_tags]
                # print(data_list)
                # ['2', 'TATA TIGOR EV - XM', 'TATA TIGOR EV - XM', 'Four Wheeler ( e-4W )', 'M1', '162000', 'EXPIRED', 'View']
                
                #remove last element
                data_list.pop()

                #adding oem name
                data_list[0]=oem_name

                #now for link
                link_l=td_tags[7]
                # print(link_l)
                link_tag = link_l.find('a', id='btnShow')
                str1="https://fame2.heavyindustries.gov.in/"
                link = str1+link_tag['href']
                data_list.append(link)


                #now for json 
                response2 = requests.get(link)
                soup2 = BeautifulSoup(response2.text, "html.parser")
                table2 = soup2.find('table', class_='custom_table')
                rows2 = table2.find_all('tr')
                data = {}
                for row in rows2:
                    cells = row.find_all('td')
                    if len(cells) == 2:
                        label = cells[0].text.strip()
                        value = cells[1].text.strip()
                        data[label] = value
                json_data = json.dumps(data)
                data_list.append(json_data)

                
                #final data
                print(data_list)
                models.append(data_list)

df = pd.DataFrame(models, columns=columns)

df.to_csv('output.csv', index=False)
