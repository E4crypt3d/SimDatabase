from sim_utils import is_number_valid, get_sim_datebase
from cnic_utils import validate_cnic, get_cnic_details
from stringcolor import cs
import sys


if '__main__' == __name__:
    print(cs("\nCreated By E4CRYPT3D\n", "yellow").bold())
    if len(sys.argv) != 3:
        print(
            "Invalid arguments. Usage: python program.py -n <phone_number> or -c <cnic_id>")
    else:
        option = sys.argv[1]
        value = sys.argv[2]

        if option == "-n":
            if is_number_valid(value):
                print(cs("Valid phone number", "green"))
                data = get_sim_datebase(value)
                print(cs(f"\nData Found on {value}", 'yellow'))
                print(cs("\n Key        | Value      |", 'yellow'))
                print("+---------------+------------+")
                for k, d in data.items():
                    print(f" {k:<10} | {d:<10} |")
                print("+---------------+------------+------------+\n")

        elif option == "-c":
            if validate_cnic(value):
                print(cs("Valid CNIC number", "green"))
                data = get_cnic_details(value)
                print(
                    cs(f"\nTotal {len(data)} Data Found on {value}", 'yellow'))
                print(cs("\n Key        | Value      |", 'yellow'))
                print("+---------------+------------+")
                for no in data:
                    for k, d in no.items():
                        print(f" {k:<10} | {d:<10} |")
                    print(cs("+---------------+------------+------------+\n", 'yellow'))
        else:
            print(cs("Invalid option:", option), 'red')
