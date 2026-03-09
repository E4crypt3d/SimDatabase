#!/usr/bin/env python3
from typing import Dict, List, Optional
import re, sys, argparse, requests, json, os, time
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from utils import (
    get_headers,
    get_db,
    get_alt_source_a_endpoint,
    get_alt_source_a_base_url,
    get_alt_source_b_endpoint,
    analyze_cnic,
    cs,
    bold,
)


class VerifyPK:
    def __init__(self, option: str, value: str):
        self.option = option
        self.value = value
        self.cache_file = "cache.json"
        self.cache = self._load_cache()
        self.session = requests.Session()
        print(
            cs(
                "⚠️  Use only for authorized lookups. Compliance with PECA Act is user responsibility.\n",
                "yellow",
            )
        )

    def _random_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        """Add random delay between requests to mimic human behavior"""
        import random

        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

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
        return (
            "92" + clean[1:] if clean.startswith("03") and len(clean) == 11 else clean
        )

    def _normalize_mobile(self, number: str) -> str:
        number = re.sub(r"\D", "", number)
        if number.startswith("92") and len(number) == 12:
            return "0" + number[2:]
        if number.startswith("0") and len(number) == 11:
            return number
        if len(number) == 10 and number.startswith("3"):
            return "0" + number
        return number

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
        if any(re.match(p, self.value) for p in [r"^92\d{10}$", r"^03\d{9}$"]):
            print(cs(f"Phone number '{self.value}' is valid.", "green"))
            return True
        print(cs("Invalid Number\n", "red"))
        return False

    def validate_cnic(self) -> bool:
        if re.match(r"^\d{5}-?\d{7}-?\d{1}$", self.value):
            print(cs(f"CNIC '{self.value}' is valid.", "green"))
            return True
        print(cs("Invalid CNIC Number\n", "red"))
        return False

    def _make_request(self) -> Optional[requests.Response]:
        db = get_db()
        headers = get_headers("primary")
        self._random_delay(0.3, 1.0)
        for attempt in range(3):
            try:
                response = self.session.post(
                    db, data={"cnnum": self.value}, headers=headers, timeout=10
                )
                response.raise_for_status()
                return response
            except RequestException as e:
                print(
                    cs(
                        f"Primary source attempt {attempt+1}: {e}. Retrying...\n",
                        "yellow",
                    )
                )
                time.sleep(1 + attempt)
        return None

    def _make_simowners_request(self, mobile: str) -> Optional[requests.Response]:
        url = get_alt_source_a_endpoint()
        track_num = self._normalize_mobile(mobile)
        payload = {"action": "fetch_simdata", "nonce": "3273a52bbf", "track": track_num}
        headers = get_headers("alt_source_a")
        self._random_delay(0.5, 1.5)
        try:
            response = self.session.post(url, data=payload, headers=headers, timeout=15)
            response.raise_for_status()
            return response
        except RequestException as e:
            print(cs(f"Alternative source #1 request failed: {e}\n", "yellow"))
            return None

    def _make_freshsims_request(self, mobile: str) -> Optional[requests.Response]:
        url = get_alt_source_b_endpoint()
        number = mobile.lstrip("0") if mobile.startswith("0") else mobile
        headers = get_headers("alt_source_b")
        self._random_delay(0.5, 1.5)
        try:
            response = self.session.post(
                url, data={"numberCnic": number}, headers=headers, timeout=15
            )
            response.raise_for_status()
            return response
        except RequestException as e:
            print(cs(f"Alternative source #2 request failed: {e}\n", "yellow"))
            return None

    def _parse_simowners_json(self, json_data: dict) -> List[Dict[str, str]]:
        records = []
        if not json_data.get("success") or "data" not in json_data:
            return records
        data = json_data["data"]
        for key in ["Mobile", "CNIC"]:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    if isinstance(item, dict):
                        record = {
                            k.upper() if k.lower() != "cnic" else "CNIC": str(v).strip()
                            for k, v in item.items()
                        }
                        records.append(record)
                break
        return records

    def _parse_alt_source_b_html(self, html: str) -> List[Dict[str, str]]:
        records = []
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", class_=lambda x: x and "table" in x)
        if not table:
            return records

        tbody = table.find("tbody")
        rows = tbody.find_all("tr") if tbody else table.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 4:
                network_cell = cells[4] if len(cells) > 4 else None
                network = ""
                if network_cell:
                    img = network_cell.find("img")
                    if img and img.get("src"):
                        network = img["src"].replace(".png", "").title()

                record = {
                    "NUMBER": cells[0].get_text(strip=True),
                    "NAME": cells[1].get_text(strip=True),
                    "CNIC": cells[2].get_text(strip=True),
                    "ADDRESS": cells[3].get_text(strip=True),
                    "NETWORK": network,
                }
                records.append(record)
        return records

    def _parse_html_form_response(self, html: str) -> List[Dict[str, str]]:
        records = []
        soup = BeautifulSoup(html, "html.parser")
        result_items = soup.find_all("div", class_="result-item")

        for item in result_items:
            record = {}
            ps = item.find_all("p")
            for p in ps:
                text = p.get_text(strip=True)
                if "Name:" in text:
                    record["NAME"] = text.replace("Name:", "").strip()
                elif "Mobile:" in text:
                    record["MOBILE"] = text.replace("Mobile:", "").strip()
                elif "CNIC:" in text:
                    record["CNIC"] = text.replace("CNIC:", "").strip()
                elif "Address:" in text:
                    record["ADDRESS"] = text.replace("Address:", "").strip()
            if record:
                records.append(record)
        return records

    def _make_html_form_request(
        self, query: str, query_type: str = "mobile"
    ) -> Optional[requests.Response]:
        url = get_alt_source_a_base_url()
        headers = get_headers("alt_source_a")
        if query_type == "cnic":
            data = {"s": query}
        else:
            data = {"s": query}

        try:
            response = self.session.post(url, data=data, headers=headers, timeout=15)
            response.raise_for_status()
            return response
        except RequestException as e:
            print(cs(f"HTML form request failed: {e}\n", "yellow"))
            return None

    def _fetch_from_simowners(self, number: str) -> Dict[str, str]:
        response = self._make_simowners_request(number)
        if response:
            try:
                json_resp = response.json()
                records = self._parse_simowners_json(json_resp)
                return records[0] if records else {}
            except json.JSONDecodeError:
                print(cs("Failed to parse JSON from alternative source #1\n", "red"))
        return {}

    def _fetch_from_alt_source_b(self, number: str) -> Dict[str, str]:
        response = self._make_freshsims_request(number)
        if response:
            try:
                data = self._parse_alt_source_b_html(response.text)
                return data[0] if data else {}
            except Exception as e:
                print(
                    cs(f"Failed to parse alternative source #2 response: {e}\n", "red")
                )
        return {}

    def process_response(self, response: requests.Response) -> Dict[str, str]:
        soup = BeautifulSoup(response.content, "html.parser")
        tg_content = soup.find(class_="tg")
        if tg_content:
            tds = tg_content.find_all("td")
            data = {}
            for i in range(0, len(tds), 2):
                if i + 1 < len(tds):
                    key = tds[i].text.strip()
                    val = tds[i + 1].text.strip()
                    if key == "CNIC":
                        val = val.split(" ")[0]
                    data[key] = val
            return data
        return {}

    def process_cnic_response(
        self, response: requests.Response
    ) -> List[Dict[str, str]]:
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")
        if tables:
            records = []
            for table in tables:
                data = {}
                for row in table.find_all("tr"):
                    tds = row.find_all("td")
                    if len(tds) >= 2:
                        key, val = tds[0].text.strip(), tds[1].text.strip()
                        if key == "CNIC":
                            val = val.split(" ")[0]
                        data[key] = val
                if data:
                    records.append(data)
            if records:
                return records
        try:
            json_resp = response.json()
            return self._parse_simowners_json(json_resp)
        except:
            pass
        print(cs(f"No Records Found for {self.value}\n", "red"))
        return []

    def extract_and_analyze_cnic(self, data: Dict[str, str]) -> Optional[Dict]:
        cnic = data.get("CNIC") or data.get("cnic")
        if not cnic:
            return None
        cnic = re.sub(r"\s+", "", str(cnic))
        if len(cnic) == 13 and cnic.isdigit():
            cnic = f"{cnic[:5]}-{cnic[5:12]}-{cnic[12]}"
        return analyze_cnic(cnic)

    def print_cnic_analysis(self, analysis: dict):
        if "error" in analysis:
            print(cs(f"CNIC Analysis Error: {analysis['error']}", "red"))
            return
        print(bold(cs("CNIC DETAILED ANALYSIS:", "yellow")))
        print()
        for key, value in analysis.items():
            kc = (
                "green"
                if key in ["Input CNIC", "Normalized CNIC"]
                else ("cyan" if key in ["Province / Territory", "Division"] else "blue")
            )
            print(f"{cs(key, kc)}: {cs(str(value), 'white')}")

    @staticmethod
    def print_data(data: Dict[str, str]):
        if not data:
            return
        for k, v in data.items():
            print(f"{cs(k, 'green')}: {cs(str(v), 'white')}")
        print()

    def run(self):
        print(bold(cs("\nVerifyPK - Sim Database Tool\n", "yellow")))
        try:
            cache_key = self._get_cache_key(self.value)

            if self.option == "-n":
                if not self.is_number_valid():
                    return

                if cache_key in self.cache:
                    print(cs(f"✓ Data found in cache for {self.value}.", "cyan"))
                    data = self.cache[cache_key]
                else:
                    formats = [self.value]
                    if self.value.startswith("03"):
                        formats.append("92" + self.value[1:])
                    elif self.value.startswith("92"):
                        formats.append("0" + self.value[2:])

                    data = {}
                    for fmt in formats:
                        self.value = fmt

                        print(cs(f"→ Querying primary source for {fmt}...", "blue"))
                        response = self._make_request()
                        if response:
                            data = self.process_response(response)
                            if data:
                                print(
                                    cs("✓ Data retrieved from primary source", "green")
                                )
                                break

                        print(
                            cs(f"→ Trying alternative source #1 for {fmt}...", "yellow")
                        )
                        data = self._fetch_from_simowners(fmt)
                        if data:
                            print(
                                cs(
                                    "✓ Data retrieved from alternative source #1",
                                    "green",
                                )
                            )
                            break

                        print(
                            cs(f"→ Trying alternative source #2 for {fmt}...", "yellow")
                        )
                        data = self._fetch_from_alt_source_b(fmt)
                        if data:
                            print(
                                cs(
                                    "✓ Data retrieved from alternative source #2",
                                    "green",
                                )
                            )
                            break

                        time.sleep(1)

                    if data:
                        self.cache[cache_key] = data
                        self._save_cache()

                if data:
                    print(cs(f"\n📋 Data Found for {self.value}:", "yellow"))
                    cnic_analysis = self.extract_and_analyze_cnic(data)
                    if cnic_analysis and "error" not in cnic_analysis:
                        self.print_cnic_analysis(cnic_analysis)
                        print()
                    self.print_data(data)
                else:
                    print(cs(f"\n✗ No records found for {self.value}", "red"))

            elif self.option == "-c":
                if not self.validate_cnic():
                    return
                cnic_analysis = analyze_cnic(self.value)
                if cache_key in self.cache:
                    print(cs(f"✓ Data found in cache for {self.value}.", "cyan"))
                    data = self.cache[cache_key]
                else:
                    data = None
                    response = self._make_request()
                    if response:
                        data = self.process_cnic_response(response)
                    if not data:
                        print(
                            cs(
                                "→ Trying alternative source for CNIC lookup...",
                                "yellow",
                            )
                        )
                        sim_resp = self._make_simowners_request(self.value)
                        if sim_resp:
                            try:
                                json_resp = sim_resp.json()
                                data = self._parse_simowners_json(json_resp)
                                if data is None:
                                    data = []
                            except Exception:
                                data = None
                        if not data:
                            print(
                                cs(
                                    "→ Trying HTML form lookup...",
                                    "yellow",
                                )
                            )
                            html_resp = self._make_html_form_request(self.value, "cnic")
                            if html_resp:
                                try:
                                    data = self._parse_html_form_response(
                                        html_resp.text
                                    )
                                    if not data:
                                        data = []
                                except Exception:
                                    pass
                    if not data:
                        print(
                            cs(
                                "→ Trying second alternative source...",
                                "yellow",
                            )
                        )
                        alt2_resp = self._make_freshsims_request(self.value)
                        if alt2_resp:
                            try:
                                parsed = self._parse_alt_source_b_html(alt2_resp.text)
                                if parsed:
                                    data = parsed
                            except Exception:
                                pass
                    if data:
                        self.cache[cache_key] = data
                        self._save_cache()
                    else:
                        data = []

                if data:
                    print(
                        cs(
                            f"\n📋 Total {len(data)} record(s) found for {self.value}:",
                            "yellow",
                        )
                    )
                    self.print_cnic_analysis(cnic_analysis)
                    print()
                    for i, record in enumerate(data, 1):
                        print(cs(f"--- Record #{i} ---", "bright_cyan"))
                        self.print_data(record)
                else:
                    print(cs(f"\n✗ No records found for CNIC {self.value}", "red"))
            else:
                print(cs("Invalid option. Use -n <phone> or -c <cnic>", "red"))

        except KeyboardInterrupt:
            print(cs("\n\nOperation cancelled by user.", "yellow"))
        except Exception as e:
            print(cs(f"\n✗ Error: {e}\n", "red"))


def main():
    parser = argparse.ArgumentParser(
        description="Verify Pakistan phone numbers or CNICs"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--phone", type=str, help="Phone number")
    group.add_argument("-c", "--cnic", type=str, help="CNIC")
    args = parser.parse_args()
    if args.phone:
        VerifyPK("-n", args.phone).run()
    elif args.cnic:
        VerifyPK("-c", args.cnic).run()


if __name__ == "__main__":
    main()
