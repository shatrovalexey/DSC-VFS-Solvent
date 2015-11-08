# dsc
Data storage client

## Appointment
The program is designed for a secure storage in public networks and services.
Currently it supports FTP and IMAP v4 protocol only.

## How it works
The program splits your file into parts, each part separately encrypts the password with its random algorithm AES-256, and sends it to the network.

## Requirements
1. Python version >= 3.4x : https://www.python.org/downloads/
2. win32con: http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/
3. pycrypto: https://pypi.python.org/pypi/pycrypto

## Configuring
Setup your account settings in config/account.gz
It supports DriverFTP and DriverIMAP4 drivers only.
Setup your paths in install.reg file and run it.

## Usage
On Windows' Explorer program you'll have new menu items that are usable to manage your files between different accounts from config/account.gz.

When you ran \_\_init\_\_.py you'll get GUI to manage your remotely stored files and accounts.

## TODO
    From JSON to SQLite data manager migration
    Compress and protect DB
    Remove any OS dependance
    Use cx_freeze to pack it into executable
    Secure data packets distribution with duplicates between many accounts
    Disk driver for Linux systems
    More data storage manage settings like stored files testing and accounts' service speed testing
    More services, more drivers
    Mobile devices implementation

## Author
Shatrov Alexej Sergeevich, http://ashatrov.ru, mail[at]ashatrov.ru.

Your donations are welcome BTC: 3N5sCXgx2rs2bkAQNgoJQtdhsgm3KGDzhG
