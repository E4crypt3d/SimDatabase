import sys
import argparse
from stringcolor import cs
from columnar import columnar
from sim_utils import is_number_valid, get_sim_datebase
from cnic_utils import validate_cnic, get_cnic_details

def print_banner():
    banner = """
    *****************************************
    *          SIM DATABASE TOOL            *
    *         Created By E4CRYPT3D          *
    *****************************************
    """
    print(cs(banner, "yellow").bold())

def display_table(data, title):
    if not data:
        print(cs(f"\n[!] No records found for {title}.", "red"))
        return

    print(cs(f"\n[+] Results for {title}:", "cyan").bold())
    
    if isinstance(data, dict):
        headers = ['Field', 'Value']
        rows = [[k, v] for k, v in data.items()]
    elif isinstance(data, list):
        headers = list(data[0].keys())
        rows = [[item.get(h, '') for h in headers] for item in data]
    else:
        print(cs("[!] Error: Unexpected data format.", "red"))
        return

    table = columnar(rows, headers, no_borders=False)
    print(table)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="SimDatabase Tool - Lookup SIM and CNIC details")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-n", "--number", help="Phone number to lookup (e.g., 03XXXXXXXXX or 923XXXXXXXXX)")
    group.add_argument("-c", "--cnic", help="CNIC to lookup (e.g., 12345-1234567-1 or 1234512345671)")
    
    args = parser.parse_args()

    if args.number:
        if is_number_valid(args.number):
            print(cs(f"[*] Searching for phone number: {args.number}...", "yellow"))
            result = get_sim_datebase(args.number)
            display_table(result, args.number)
        else:
            print(cs(f"[!] '{args.number}' is not a valid phone number format.", "red"))
            sys.exit(1)

    elif args.cnic:
        if validate_cnic(args.cnic):
            print(cs(f"[*] Searching for CNIC: {args.cnic}...", "yellow"))
            result = get_cnic_details(args.cnic)
            display_table(result, args.cnic)
        else:
            print(cs(f"[!] '{args.cnic}' is not a valid CNIC format.", "red"))
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(cs("\n[!] Operation cancelled by user.", "red"))
        sys.exit(0)
    except Exception as e:
        print(cs(f"\n[!] An unexpected error occurred: {e}", "red"))
        sys.exit(1)
