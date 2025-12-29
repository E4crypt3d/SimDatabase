import re
from bs4 import BeautifulSoup
from utils import fetch_data

def is_number_valid(number):
    cc_pattern = r'^92\d{10}$'
    lc_pattern = r'^03\d{9}$'
    return bool(re.match(cc_pattern, number) or re.match(lc_pattern, number))

def get_sim_datebase(number):
    content = fetch_data(number)
    if not content:
        return None

    soup = BeautifulSoup(content, "html.parser")
    souped_content = soup.find(class_='tg')
    if souped_content:
        sim_data_td = souped_content.find_all('td')
        sim_data_list = [a.text.strip() for a in sim_data_td]
        sim_data = {}

        for i in range(0, len(sim_data_list), 2):
            if i + 1 < len(sim_data_list):
                key = sim_data_list[i]
                value = sim_data_list[i+1]
                if key == "CNIC":
                    value = value.split(" ")[0]
                sim_data[key] = value
        return sim_data
    return None
