import re
from stringcolor import cs
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import NameResolutionError
from utils import headers, get_db


def validate_cnic(cnic):
    pattern1 = r"^[0-9]{5}-[0-9]{7}-[0-9]{1}$"
    pattern2 = r"^[0-9]{5}[0-9]{7}[0-9]{1}$"
    if re.match(pattern1, cnic):
        return True
    elif re.match(pattern2, cnic):
        return True
    else:
        print(
            cs("Invalid CNIC Number - Provide a Valid CNIC Number\n", 'red'))
        exit()


def get_cnic_details(cnic):
    db = get_db()
    try:
        response = requests.post(db, data={"cnnum": cnic}, headers=headers)
    except NameResolutionError:
        print(cs("\nPlease Make sure you are connected to the Internet or Try again Later.\n", "red"))
        exit()
    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all('table')
    if tables:
        cnic_data_list = []
        for table in tables:
            data_dict = {}
            rows = table.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if cells[0].text.strip() == "CNIC":
                    value = cells[1].text.split(" ")[0]
                else:
                    value = cells[1].text.strip()
                field = cells[0].text.strip()

                data_dict[field] = value

            cnic_data_list.append(data_dict)
        return cnic_data_list

    else:
        print(cs(f"No Records Found on {cnic}\n", 'red'))
        exit()
