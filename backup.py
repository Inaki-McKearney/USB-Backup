import os
import string
import time
from zipfile import ZipFile, BadZipFile
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


def zip_modified(src, des):
    # Returns True if the backup is not up to date with the source or if previous compression was aborted
    src_mod_date = max(map(lambda x: os.stat(x).st_mtime, src))
    if os.path.exists(des):
        try:
            with ZipFile(des, 'r') as zippy:
                return src_mod_date > float(zippy.comment.decode())
        except BadZipFile:
            print("\nError retrieving date modified - Previous compression terminated prematurely")
    return True


def zip_it(src, des):
    # Zips files after checking if the contents are up to date
    last_modified = 0
    paths = get_paths(src)

    if not zip_modified(paths, des):
        print("Zip in backup folder is up to date")
        return

    with ZipFile(des, 'w') as zippy:
        file_count = len(paths)
        for file in paths:
            date_modified = os.stat(file).st_mtime
            try:
                zippy.write(file)
                if date_modified > last_modified:
                    last_modified = date_modified
            except ValueError as e:
                print(str(e), file, sep=': ')
            print(f'\r{(paths.index(file)+1)/file_count*100:.2f}% Complete\t', end='')
        # Stores the latest modified time in the zip comment
        zippy.comment = str(last_modified).encode()


def copy_it(src, des):
    # Copies files ignoring empty folders and up-to-date files
    paths = get_paths(src)
    file_count = len(paths)

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

        print(f'\r{(paths.index(path)+1)/file_count*100:.2f}% Complete\t', end='')


def main():
    devices = config.DEVICES
    des_dir = config.BACKUP_DIRECTORY

    for drive, name in get_drives(devices):

        # TODO: Check if contents have been updated before zipping
        if config.ZIP:
            start_time = time.time()
            zip_it(drive, des_dir + name + '.zip')
            print(f'Drive {drive}\tZipped in {time.time()-start_time} seconds', end='\n\n')

        if config.COPY:
            start_time = time.time()
            copy_it(drive, des_dir + name)
            print(f'Drive {drive}\tCopied in {time.time()-start_time} seconds', end='\n\n')

    if config.NOTIFY:
        print('\a')

    if not config.CLOSE:
        input()


if __name__ == "__main__":
    main()
