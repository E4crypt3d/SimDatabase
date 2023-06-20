import re
from stringcolor import cs
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import NameResolutionError
from utils import headers, get_db


def is_number_valid(number):
    cc_pattern = r'^92\d{10}$'
    lc_pattern = r'^03\d{9}$'
    cc_match = re.match(cc_pattern, number)
    lc_match = re.match(lc_pattern, number)
    if cc_match:
        return bool(cc_match)
    elif lc_match:
        return bool(lc_match)
    else:
        print(
            cs("Invalid Number - Number must be in '923[0-9]' or '03[0-9]' format.\n", 'red'))
        exit()


def get_sim_datebase(number):
    db = get_db()
    try:
        response = requests.post(
            db, data={'cnnum': number}, headers=headers)
    except NameResolutionError:
        print(cs("\nPlease Make sure you are connected to the Internet or Try again Later.\n", "red"))
        exit()

    soup = BeautifulSoup(response.content, "html.parser")
    souped_content = soup.find(class_='tg')
    if souped_content:
        sim_data_td = souped_content.find_all('td')
        sim_data_list = [a.text for a in sim_data_td]
        sim_data = {}

        for i in range(0, len(sim_data_list), 2):
            key = sim_data_list[i]
            if key == "CNIC":
                check_value = sim_data_list[i+1] if i + \
                    1 < len(sim_data_list) else None
                value = check_value.split(" ")[0]
            else:
                value = sim_data_list[i+1] if i + \
                    1 < len(sim_data_list) else None
            sim_data[key] = value

        return sim_data
    else:
        print(cs(f"No Records Found for {number}\n", 'red'))
        exit()
