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
