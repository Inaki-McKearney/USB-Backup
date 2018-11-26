import os
import string
import time
from zipfile import ZipFile
import shutil
import stat
import config


def get_drives(devices):
    # Returns drive letters of connected storage devices selected to be backed up and backup names
    drive_list = [l + ':/' for l in string.ascii_uppercase if os.path.exists(f'{l}:/')]
    return zip([l for l in drive_list if os.stat(l).st_dev in devices.keys()], devices.values())


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
        folder = des + os.path.split(os.path.splitdrive(path)[1])[0]
        target = os.path.join(folder, os.path.split(path)[1])

        if not os.path.exists(folder):
            os.makedirs(folder)

        # Checks if the file exists and if it was modified
        if os.path.exists(target):
            file_synced = os.stat(path).st_mtime <= os.stat(target).st_mtime
        else:
            file_synced = False

        try:
            if not file_synced:
                shutil.copy2(path, folder)
        except PermissionError:
            # Removes Read-Only permission, overwrites file (with original's permissions)
            os.chmod(target, stat.S_IWRITE)
            shutil.copy2(path, folder)


def main():
    devices = config.DEVICES
    des_dir = config.BACKUP_DIRECTORY

    for drive, name in get_drives(devices):

        # TODO: Check if contents have been updated before zipping
        if config.ZIP:
            start_time = time.time()
            zip_it(drive, des_dir + name + '.zip')
            print(f'drive {drive} zipped in {time.time()-start_time} seconds')

        if config.COPY:
            start_time = time.time()
            copy_it(drive, des_dir + name)
            print(f'drive {drive} copied in {time.time()-start_time} seconds')

    if not config.CLOSE:
        input()


if __name__ == "__main__":
    main()
