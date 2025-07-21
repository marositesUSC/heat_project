## Enable File Sharing with Samba
Samba creates a network share on your Raspberry Pi so we can easily pull data or files from it. To install run this command...

```bash
sudo apt-get install samba samba-common-bin
```
We need to edit the configiguration file. `nano` opens a text editor. It is super handy. You will notice your mouse will not work, and you will have to manouver through the file with your keyboard. 
```bash
sudo nano /etc/samba/smb.conf
```

Paste the follow into the file.

```
[PiShare]
    comment=Pi Share
    path=/home/pi
    browseable=yes
    writeable=yes
    read only=no
    guest ok=no
    valid users=user
    force user=user
    create mask=0664
    directory mask=0775
    # Optional: recycle bin for deleted files
    # vfs objects = recycle
    # recycle:repository = .recycle/%U
    # recycle:keeptree = yes
    # recycle:versions = yes
    # recycle:maxsize = 0
```
To save your file from `nano` hit ctrl+???


Check the status of the samba service.

``` bash
sudo service smbd status
```

Set password and restart. Just match the username and password of the Pi.

```bash
sudo smbpasswd -a user

user

user
```

Restart the Samba Service.

```bash 
sudo systemctl restart smbd nmbd
```

Now you can open file explorer on your windows machine and view all the files in the home directory.
