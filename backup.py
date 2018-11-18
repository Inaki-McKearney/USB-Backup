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
    # print(datetime.utcfromtimestamp(list(devices.values())[0]).strftime('%Y-%m-%d %H:%M:%S'))


def get_paths(directory):
    # Returns list of file paths to back up
    paths = []
    for root, directories, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            paths.append(path)
    return paths


def zip_it(src, dest):
    with ZipFile(dest, 'w') as zip:
        # writing each file one by one
        for file in get_paths(src):
            try:
                zip.write(file)
            except ValueError as e:
                print(str(e) + ' ' + file)


def copy(src, dest):
    # Copies files while deleting empty folders
    paths = get_paths(src)

    for path in paths:
        folder = dest + os.path.split(os.path.splitdrive(path)[1])[0]
        if not os.path.exists(folder):
            os.makedirs(folder)
        # print(path, folder, sep='   -   ')
        try:
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
        start_time = time.time()
        # zip_it(drive, backup_directory + str(datetime.now().date()) + '.zip')
        # copy_it('J:/', backup_directory + str(datetime.now().date()))
        copy(drive, backup_directory + str(datetime.now().date()))
        print(f'drive {drive} zipped in {time.time()-start_time} seconds')


if __name__ == "__main__":
    main()
