import os
import string
from datetime import datetime
import time
from zipfile import ZipFile
import shutil
import stat


def get_drives(devices):
    # Stores list of drive letters of connected storage devices
    drive_list = [l + ':/' for l in string.ascii_uppercase if os.path.exists(f'{l}:/')]

    # Clears the drive_list of unwanted volumes and updates devices dictionary with last modification date
    for l in drive_list[:]:
        dev = os.stat(l)
        if dev.st_dev in devices.keys():
            devices[dev.st_dev] = dev.st_mtime
        else:
            drive_list.remove(l)

    return drive_list


def get_paths(directory):
    # Returns list of file paths to back up
    paths = []
    for root, directories, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            paths.append(path)
    return paths


def zip_it(src, des):
    with ZipFile(des, 'w') as zippy:
        for file in get_paths(src):
            try:
                zippy.write(file)
            except ValueError as e:
                print(str(e), file, sep=': ')


def copy_it(src, des):
    # Copies files ignoring empty folders and up-to-date files
    paths = get_paths(src)

    for path in paths:
        print(path)
        folder = des + os.path.split(os.path.splitdrive(path)[1])[0]
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Checks if the file exists and if it is the latest version
        if os.path.exists((os.path.join(folder, os.path.split(path)[1]))):
            file_synced = os.stat(path).st_mtime <= os.stat(os.path.join(folder, os.path.split(path)[1])).st_mtime
        else:
            file_synced = False

        try:
            if not file_synced:
                shutil.copy2(path, folder)
        except PermissionError:
            # Removes Read-Only permission, overwrites file (with original's permissions)
            os.chmod(os.path.join(folder, os.path.split(path)[1]), stat.S_IWRITE)
            shutil.copy2(path, folder)


def main():
    # TODO: Replace with config
    devices = {3662415509: 0}
    backup_directory = 'D:/Documents/USB Backup/'

    for drive in get_drives(devices):
        # start_time = time.time()
        # zip_it(drive, backup_directory + str(datetime.now().date()) + '.zip')
        # print(f'drive {drive} zipped in {time.time()-start_time} seconds')

        start_time = time.time()
        copy_it(drive, backup_directory + str(datetime.now().date()))
        print(f'drive {drive} copied in {time.time()-start_time} seconds')


if __name__ == "__main__":
    main()
