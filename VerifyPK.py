import re
import requests
from bs4 import BeautifulSoup
from utils import get_headers, get_db
from requests.exceptions import RequestException
import argparse
import sys
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


class VerifyPK:
    def __init__(self, option, value):
        self.option = option
        self.value = value

    def is_number_valid(self):
        patterns = [r'^92\d{10}$', r'^03\d{9}$']
        if any(re.match(pattern, self.value) for pattern in patterns):
            print(f"{Fore.GREEN}Phone number '{self.value}' is valid.")
            return True
        print(
            f"{Fore.RED}Invalid Number - Number must be in '92[0-9]' or '03[0-9]' format.\n")
        return False

    def get_sim_database(self):
        db = get_db()
        headers = get_headers()
        for attempt in range(3):  # Retry mechanism
            try:
                response = requests.post(
                    db, data={'cnnum': self.value}, headers=headers, timeout=10)
                response.raise_for_status()  # Raise an exception for HTTP errors
                return response
            except RequestException as e:
                print(f"{Fore.RED}{e}")
                print(
                    f"{Fore.YELLOW}Attempt {attempt + 1}: Connection Error. Retrying...\n")
                if attempt == 2:
                    print(
                        f"{Fore.RED}Failed to connect after 3 attempts. Exiting...\n")
                    sys.exit(1)

    def process_response(self, response):
        soup = BeautifulSoup(response.content, "html.parser")
        souped_content = soup.find(class_='tg')
        if souped_content:
            sim_data_td = souped_content.find_all('td')
            sim_data = {
                sim_data_td[i].text: sim_data_td[i + 1].text.split(" ")[0]
                if sim_data_td[i].text == "CNIC" else sim_data_td[i + 1].text
                for i in range(0, len(sim_data_td), 2)
            }
            return sim_data
        print(f"{Fore.RED}No Records Found for {self.value}\n")
        return {}

    def validate_cnic(self):
        pattern = r"^\d{5}-?\d{7}-?\d{1}$"
        if re.match(pattern, self.value):
            print(f"{Fore.GREEN}CNIC '{self.value}' is valid.")
            return True
        print(f"{Fore.RED}Invalid CNIC Number - Provide a valid CNIC Number.\n")
        return False

    def get_cnic_details(self):
        db = get_db()
        headers = get_headers()
        for attempt in range(3):  # Retry mechanism
            try:
                response = requests.post(
                    db, data={"cnnum": self.value}, headers=headers, timeout=10)
                response.raise_for_status()
                return response
            except RequestException as e:
                print(f"{Fore.RED}{e}")
                print(
                    f"{Fore.YELLOW}Attempt {attempt + 1}: Connection Error. Retrying...\n")
                if attempt == 2:
                    print(
                        f"{Fore.RED}Failed to connect after 3 attempts. Exiting...\n")
                    sys.exit(1)

    def process_cnic_response(self, response):
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all('table')
        if tables:
            cnic_data_list = []
            for table in tables:
                rows = table.find_all('tr')
                data_dict = {
                    row.find_all('td')[0].text.strip(): row.find_all('td')[1].text.split(" ")[0]
                    if row.find_all('td')[0].text.strip() == "CNIC" else row.find_all('td')[1].text.strip()
                    for row in rows
                }
                cnic_data_list.append(data_dict)
            return cnic_data_list
        print(f"{Fore.RED}No Records Found for {self.value}\n")
        return []

    def run(self):
        print(f"{Fore.YELLOW}{Style.BRIGHT}\nCreated By E4CRYPT3D\n")
        try:
            if self.option == "-n" and self.is_number_valid():
                response = self.get_sim_database()
                data = self.process_response(response)
                if data:
                    print(f"{Fore.YELLOW}\nData Found for {self.value}:")
                    self.print_data(data)
            elif self.option == "-c" and self.validate_cnic():
                response = self.get_cnic_details()
                data = self.process_cnic_response(response)
                if data:
                    print(
                        f"{Fore.YELLOW}\nTotal {len(data)} record(s) found for {self.value}:")
                    for record in data:
                        self.print_data(record)
            else:
                print(f"{Fore.RED}Invalid option or value.")
                sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}An unexpected error occurred: {e}\n")
            sys.exit(1)

    @staticmethod
    def print_data(data):
        if not data:
            print(f"{Fore.RED}No data to display.")
            return
        print(f"{Fore.CYAN}\n Key        | Value      |")
        print("+-----------+------------+")
        for k, v in data.items():
            print(f" {k:<10} | {v:<10} |")
        print("+-----------+------------+------------+\n")


def main():
    parser = argparse.ArgumentParser(
        description='Verify phone numbers or CNICs.')
    parser.add_argument('-n', '--phone', type=str,
                        help='Phone number to verify')
    parser.add_argument('-c', '--cnic', type=str, help='CNIC to verify')

    args = parser.parse_args()

    if args.phone and args.cnic:
        print(f"{Fore.RED}Error: You can specify only one option at a time. Use -n for phone number or -c for CNIC.\n")
        sys.exit(1)
    elif args.phone:
        option = "-n"
        value = args.phone
    elif args.cnic:
        option = "-c"
        value = args.cnic
    else:
        print(
            f"{Fore.RED}Error: No valid arguments provided. Use -n <phone_number> or -c <cnic_id>.\n")
        sys.exit(1)

    verifier = VerifyPK(option, value)
    verifier.run()


if __name__ == '__main__':
    main()
