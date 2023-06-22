from sim_utils import is_number_valid, get_sim_datebase
from cnic_utils import validate_cnic, get_cnic_details
from stringcolor import cs
import sys
import subprocess
import re
import shutil


def check_for_updates():
    # Retrieve the latest tag
    tag_output = subprocess.check_output(
        ['git', 'ls-remote', '--tags', 'origin'], universal_newlines=True).strip()
    print("Tag output", tag_output)
    latest_tag = tag_output.split('\n')[-1].split('\t')[1].split('/')[-1]

    # Compare with the current tag
    current_tag = subprocess.check_output(
        ['git', 'describe', '--tags', '--abbrev=0'], universal_newlines=True).strip()
    print(current_tag, latest_tag)
    if latest_tag != current_tag:
        print("An update is available. Cloning the latest version...")

        # Clone the updated version into a temporary directory
        temp_directory = '../temp_clone'
        subprocess.run(['git', 'clone', '--depth', '1', '--branch',
                       latest_tag, 'https://github.com/E4crypt3d/SimDatabase.git', temp_directory])

        # Replace the existing directory with the updated version
        # shutil.rmtree('/')
        shutil.move(temp_directory, '/SimDatabase')

        print("Update completed!")
    else:
        print("No updates available.")


check_for_updates()

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
