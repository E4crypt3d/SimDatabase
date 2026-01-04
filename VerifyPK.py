from typing import Dict, List, Optional, Union
import re
import sys
import argparse
import requests
import json
import os
from bs4 import BeautifulSoup
from stringcolor import cs
from requests.exceptions import RequestException
from utils import get_headers, get_db, analyze_cnic


class VerifyPK:
    def __init__(self, option: str, value: str):
        self.option = option
        self.value = value
        self.cache_file = "cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self.cache, f, indent=4)
        except:
            pass

    def _get_cache_key(self, val: str) -> str:
        clean = re.sub(r"[\s+]", "", val)
        if clean.startswith("03") and len(clean) == 11:
            return "92" + clean[1:]
        return clean

    def is_number_valid(self) -> bool:
        self.value = re.sub(r"[\s+]", "", self.value)
        if self.value.startswith("92") and len(self.value) == 12:
            pass
        elif self.value.startswith("03") and len(self.value) == 11:
            pass
        elif len(self.value) == 10 and self.value.startswith("3"):
            self.value = "92" + self.value
        else:
            print(cs("Invalid Number - Format must be '92...' or '03...'\n", "red"))
            return False

        patterns = [r"^92\d{10}$", r"^03\d{9}$"]
        if any(re.match(pattern, self.value) for pattern in patterns):
            print(cs(f"Phone number '{self.value}' is valid.", "green"))
            return True
        print(cs("Invalid Number - Format must be '92...' or '03...'\n", "red"))
        return False

    def validate_cnic(self) -> bool:
        pattern = r"^\d{5}-?\d{7}-?\d{1}$"
        if re.match(pattern, self.value):
            print(cs(f"CNIC '{self.value}' is valid.", "green"))
            return True
        print(cs("Invalid CNIC Number - Provide a valid CNIC.\n", "red"))
        return False

    def _make_request(self) -> Optional[requests.Response]:
        db = get_db()
        headers = get_headers()
        for attempt in range(3):
            try:
                response = requests.post(
                    db, data={"cnnum": self.value}, headers=headers, timeout=10
                )
                response.raise_for_status()
                return response
            except RequestException:
                print(
                    cs(
                        f"Attempt {attempt + 1}: Connection Error. Retrying...\n",
                        "yellow",
                    )
                )
                if attempt == 2:
                    print(
                        cs(
                            "Failed to connect after 3 attempts. Check your connection or DNS (1.1.1.1).\n",
                            "red",
                        )
                    )
                    return None
        return None

    def process_response(self, response: requests.Response) -> Dict[str, str]:
        soup = BeautifulSoup(response.content, "html.parser")
        tg_content = soup.find(class_="tg")
        if tg_content:
            tds = tg_content.find_all("td")
            data = {}
            for i in range(0, len(tds), 2):
                key = tds[i].text.strip()
                val = tds[i + 1].text.strip()
                if key == "CNIC":
                    val = val.split(" ")[0]
                data[key] = val
            return data
        print(cs(f"No Records Found for {self.value}\n", "red"))
        return {}

    def process_cnic_response(
        self, response: requests.Response
    ) -> List[Dict[str, str]]:
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")
        if tables:
            records = []
            for table in tables:
                rows = table.find_all("tr")
                data = {}
                for row in rows:
                    tds = row.find_all("td")
                    if len(tds) >= 2:
                        key = tds[0].text.strip()
                        val = tds[1].text.strip()
                        if key == "CNIC":
                            val = val.split(" ")[0]
                        data[key] = val
                if data:
                    records.append(data)
            return records
        print(cs(f"No Records Found for {self.value}\n", "red"))
        return []

    def extract_and_analyze_cnic(self, data: Dict[str, str]) -> Optional[Dict]:
        cnic = data.get("CNIC")
        if not cnic:
            return None

        cnic = re.sub(r"\s+", "", cnic)

        if len(cnic) == 13 and cnic.isdigit():
            cnic = f"{cnic[:5]}-{cnic[5:12]}-{cnic[12]}"

        return analyze_cnic(cnic)

    def run(self):
        print(cs("\nVerifyPK - Sim Database Tool\n", "yellow").bold())
        try:
            cache_key = self._get_cache_key(self.value)

            if self.option == "-n":
                if not self.is_number_valid():
                    return

                cache_key = self._get_cache_key(self.value)
                if cache_key in self.cache:
                    print(cs(f"Data found in cache for {self.value}.", "cyan"))
                    data = self.cache[cache_key]
                else:
                    formats = []
                    if self.value.startswith("03"):
                        formats = [self.value, "92" + self.value[1:]]
                    elif self.value.startswith("92"):
                        formats = ["0" + self.value[2:], self.value]

                    data = {}
                    for fmt in formats:
                        self.value = fmt
                        response = self._make_request()
                        if response:
                            data = self.process_response(response)
                            if data:
                                self.cache[cache_key] = data
                                self._save_cache()
                                break
                            if fmt == formats[0]:
                                print(
                                    cs(
                                        f"No records found for {fmt}. Trying fallback format {formats[1]}...",
                                        "yellow",
                                    )
                                )

                if data:
                    print(cs(f"\nData Found for {self.value}:", "yellow"))

                    cnic_analysis = self.extract_and_analyze_cnic(data)
                    if cnic_analysis and "error" not in cnic_analysis:
                        self.print_cnic_analysis(cnic_analysis)
                        print()

                    self.print_data(data)
            elif self.option == "-c":
                if not self.validate_cnic():
                    return

                cnic_analysis = analyze_cnic(self.value)

                if cache_key in self.cache:
                    print(cs(f"Data found in cache for {self.value}.", "cyan"))
                    data = self.cache[cache_key]
                else:
                    response = self._make_request()
                    if response:
                        data = self.process_cnic_response(response)
                        if data:
                            self.cache[cache_key] = data
                            self._save_cache()
                    else:
                        data = []

                if data:
                    print(
                        cs(
                            f"\nTotal {len(data)} record(s) found for {self.value}:",
                            "yellow",
                        )
                    )

                    self.print_cnic_analysis(cnic_analysis)
                    print()

                    for record in data:
                        self.print_data(record)
            else:
                print(cs("Invalid option specified.", "red"))
        except Exception as e:
            print(cs(f"An error occurred: {e}\n", "red"))

    def print_cnic_analysis(self, analysis: dict):
        if "error" in analysis:
            print(cs(f"CNIC Analysis Error: {analysis['error']}", "red"))
            return

        print(cs("CNIC DETAILED ANALYSIS:", "yellow").bold())

        table_data = {
            "Input CNIC": analysis.get("Input CNIC", "N/A"),
            "Normalized CNIC": analysis.get("Normalized CNIC", "N/A"),
            "Province / Territory": analysis.get("Province / Territory", "N/A"),
            "Division": analysis.get("Division", "N/A"),
            "Family Number": analysis.get("Family Number", "N/A"),
            "Gender": analysis.get("Gender", "N/A"),
        }

        max_key_len = max(len(k) for k in table_data.keys())
        max_val_len = max(len(str(v)) for v in table_data.values())

        border = "+" + "-" * (max_key_len + 2) + "+" + "-" * (max_val_len + 2) + "+"

        print(cs(border, "cyan"))

        for k, v in table_data.items():
            key_color = (
                "green"
                if k in ["Input CNIC", "Normalized CNIC"]
                else (
                    "cyan"
                    if k in ["Province / Territory", "Division"]
                    else "blue" if k == "Family Number" else "magenta"
                )
            )

            print(
                f"| {cs(k, key_color):<{max_key_len}} | {cs(str(v), 'white'):<{max_val_len}} |"
            )

        print(cs(border, "cyan"))

    @staticmethod
    def print_data(data: Dict[str, str]):
        if not data:
            return

        max_key_len = max(len(k) for k in data.keys())
        # Use str(v) in case there are non-string values
        max_val_len = max(len(str(v)) for v in data.values())

        border = "+" + "-" * (max_key_len + 2) + "+" + "-" * (max_val_len + 2) + "+"
        header = f"| {'Key':<{max_key_len}} | {'Value':<{max_val_len}} |"

        print(cs(border, "green"))
        print(cs(header, "green"))
        print(cs(border, "green"))

        for k, v in data.items():
            print(f"| {k:<{max_key_len}} | {str(v):<{max_val_len}} |")

        print(cs(border, "green"))
        print("")


def main():
    parser = argparse.ArgumentParser(
        description="Verify phone numbers or CNICs in Pakistan."
    )
    parser.add_argument("-n", "--phone", type=str, help="Phone number to verify")
    parser.add_argument("-c", "--cnic", type=str, help="CNIC to verify")

    args = parser.parse_args()

    if args.phone and args.cnic:
        print(cs("Error: Specify either -n or -c, not both.\n", "red"))
        sys.exit(1)

    if args.phone:
        verifier = VerifyPK("-n", args.phone)
    elif args.cnic:
        verifier = VerifyPK("-c", args.cnic)
    else:
        print(cs("Error: No arguments provided. Use -n <phone> or -c <cnic>.\n", "red"))
        sys.exit(1)

    verifier.run()


if __name__ == "__main__":
    main()
