from typing import Dict, List, Optional, Union
import re
import sys
import argparse
import requests
from bs4 import BeautifulSoup
from stringcolor import cs
from requests.exceptions import RequestException
from utils import get_headers, get_db


class VerifyPK:
    def __init__(self, option: str, value: str):
        self.option = option
        self.value = value

    def is_number_valid(self) -> bool:
        patterns = [r'^92\d{10}$', r'^03\d{9}$']
        if any(re.match(pattern, self.value) for pattern in patterns):
            print(cs(f"Phone number '{self.value}' is valid.", 'green'))
            return True
        print(cs("Invalid Number - Format must be '92...' or '03...'\n", 'red'))
        return False

    def validate_cnic(self) -> bool:
        pattern = r"^\d{5}-?\d{7}-?\d{1}$"
        if re.match(pattern, self.value):
            print(cs(f"CNIC '{self.value}' is valid.", 'green'))
            return True
        print(cs("Invalid CNIC Number - Provide a valid CNIC.\n", 'red'))
        return False

    def _make_request(self) -> Optional[requests.Response]:
        db = get_db()
        headers = get_headers()
        for attempt in range(3):
            try:
                response = requests.post(
                    db, data={'cnnum': self.value}, headers=headers, timeout=10)
                response.raise_for_status()
                return response
            except RequestException:
                print(cs(f"Attempt {attempt + 1}: Connection Error. Retrying...\n", 'yellow'))
                if attempt == 2:
                    print(cs("Failed to connect after 3 attempts. Check your connection or DNS (1.1.1.1).\n", 'red'))
                    return None
        return None

    def process_response(self, response: requests.Response) -> Dict[str, str]:
        soup = BeautifulSoup(response.content, "html.parser")
        tg_content = soup.find(class_='tg')
        if tg_content:
            tds = tg_content.find_all('td')
            data = {}
            for i in range(0, len(tds), 2):
                key = tds[i].text.strip()
                val = tds[i+1].text.strip()
                if key == "CNIC":
                    val = val.split(" ")[0]
                data[key] = val
            return data
        print(cs(f"No Records Found for {self.value}\n", 'red'))
        return {}

    def process_cnic_response(self, response: requests.Response) -> List[Dict[str, str]]:
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all('table')
        if tables:
            records = []
            for table in tables:
                rows = table.find_all('tr')
                data = {}
                for row in rows:
                    tds = row.find_all('td')
                    if len(tds) >= 2:
                        key = tds[0].text.strip()
                        val = tds[1].text.strip()
                        if key == "CNIC":
                            val = val.split(" ")[0]
                        data[key] = val
                if data:
                    records.append(data)
            return records
        print(cs(f"No Records Found for {self.value}\n", 'red'))
        return []

    def run(self):
        print(cs("\nVerifyPK - Sim Database Tool\n", "yellow").bold())
        try:
            if self.option == "-n":
                if not self.is_number_valid():
                    return
                response = self._make_request()
                if response:
                    data = self.process_response(response)
                    if data:
                        print(cs(f"\nData Found for {self.value}:", 'yellow'))
                        self.print_data(data)
            elif self.option == "-c":
                if not self.validate_cnic():
                    return
                response = self._make_request()
                if response:
                    data = self.process_cnic_response(response)
                    if data:
                        print(cs(f"\nTotal {len(data)} record(s) found for {self.value}:", 'yellow'))
                        for record in data:
                            self.print_data(record)
            else:
                print(cs("Invalid option specified.", 'red'))
        except Exception as e:
            print(cs(f"An error occurred: {e}\n", 'red'))

    @staticmethod
    def print_data(data: Dict[str, str]):
        if not data:
            return
        
        max_key_len = max(len(k) for k in data.keys())
        max_val_len = max(len(v) for v in data.values())
        
        border = "+" + "-" * (max_key_len + 2) + "+" + "-" * (max_val_len + 2) + "+"
        header = f"| {'Key':<{max_key_len}} | {'Value':<{max_val_len}} |"
        
        print(cs(border, 'cyan'))
        print(cs(header, 'cyan'))
        print(cs(border, 'cyan'))
        
        for k, v in data.items():
            print(f"| {k:<{max_key_len}} | {v:<{max_val_len}} |")
        
        print(cs(border, 'cyan'))
        print("")


def main():
    parser = argparse.ArgumentParser(
        description='Verify phone numbers or CNICs in Pakistan.')
    parser.add_argument('-n', '--phone', type=str, help='Phone number to verify')
    parser.add_argument('-c', '--cnic', type=str, help='CNIC to verify')

    args = parser.parse_args()

    if args.phone and args.cnic:
        print(cs("Error: Specify either -n or -c, not both.\n", 'red'))
        sys.exit(1)
    
    if args.phone:
        verifier = VerifyPK("-n", args.phone)
    elif args.cnic:
        verifier = VerifyPK("-c", args.cnic)
    else:
        print(cs("Error: No arguments provided. Use -n <phone> or -c <cnic>.\n", 'red'))
        sys.exit(1)

    verifier.run()


if __name__ == '__main__':
    main()
