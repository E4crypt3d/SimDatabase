import re
from bs4 import BeautifulSoup
from utils import fetch_data

def validate_cnic(cnic):
    pattern1 = r"^[0-9]{5}-[0-9]{7}-[0-9]{1}$"
    pattern2 = r"^[0-9]{5}[0-9]{7}[0-9]{1}$"
    return bool(re.match(pattern1, cnic) or re.match(pattern2, cnic))

def get_cnic_details(cnic):
    content = fetch_data(cnic)
    if not content:
        return None

    soup = BeautifulSoup(content, "html.parser")
    tables = soup.find_all('table')
    if tables:
        cnic_data_list = []
        for table in tables:
            data_dict = {}
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    field = cells[0].text.strip()
                    value = cells[1].text.strip()
                    if field == "CNIC":
                        value = value.split(" ")[0]
                    data_dict[field] = value
            if data_dict:
                cnic_data_list.append(data_dict)
        return cnic_data_list
    return None
