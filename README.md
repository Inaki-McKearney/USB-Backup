# USB-Backup
Script to zip and/or copy any selected drive's contents to a specified directory.  
Designed for personal use but contains a config file for user convenience.

## Usage
The script can be ran manually or scheduled.  
e.g. I schedule the script to be ran via a USB inserted trigger.

## Config
The config is a YAML file and allows changes to suit most use cases
```YAML
# Directory for backups to be saved to
BACKUP_DIRECTORY : D:/Documents/USB Backup/

# Enable to copy drive content as one folder
COPY : Y

# Enable to compress drive content as one zip
ZIP : Y

# Enable to close when finished
# Disable to view times/errors
CLOSE : Y

# Enable to print bell code upon script completion
NOTIFY : Y

# Devices to be backed up
DEVICES :
    # DeviceID : BackupName
    3662415509 : School
    4053802026 : Work

```
