This document will walk you through installation of a Raspberry Pi and setting it up for our heat mapping project.

Before you begin, it is helpful to download [**Raspberry Pi Imager**](https://www.raspberrypi.com/software/), [**PuTTY**](https://www.putty.org/), and [**VNC Viewer**](https://www.realvnc.com/en/connect/download/viewer/?lai_vid=3BnGRKjX1C6KJ&lai_sr=0-4&lai_sl=l&lai_p=1&lai_na=713940).

## Quick Note

There are options for initial setup. The official documentation can be found [here](https://www.raspberrypi.com/documentation/computers/getting-started.html) and is great. You can install with keyboard and mouse, but I like to do the headless install. If you choose to do this make sure you when you image your SD card, you enter your WiFi credentials and enable SSH.

To be consistent, I have been using the following user name and password.

**USER: user**

**PASSWORD: user**

# Raspberry Pi Initial Setup

## Install OS on boot device (SD Card)

Launch Raspberry Pi Imager

Select your Raspberry Pi Device (_Raspberry Pi 3_), Operating System (I chose the recommended option, _Raspberry Pi OS (64-bit)_) and Storage Device (_SD Card_).


Connect to Raspberry Pi using PuTTY.

Check for Updates - *This will take a while*.

```sh
sudo apt update
Sudo apt upgrade
```

Open Raspberry Pi Software Configuration Tool 

In the termianl type 
```bash
raspi-config
```

Enable VNC (to access it remotely through VNC Viewer), I<sup>2</sup>C (two-wire serial communication protocol used to connect temp and humidity sensors), and Serial (serial interface for GPS).

Create our directory

```bash
mkdir heat_project
```
Create a virtual environment.
```bash
python3 -m venv env
```

This will take a minute, but will create a new virtual environment (env), or container, to store python packages. If you run the command ls you will see a new folder called env.

You can activate your virtual env by running the command

```bash
source env/bin/activate
```

You will notice your environment out infront of your user@sensorname:

You can deactivate the virtual environment by running the command `deactive` in the terminal, but keep it **activate** for now.

Install circuit python libraries – Credit to <https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi>

cd ~

pip3 install --upgrade adafruit-python-shell

wget <https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py>

sudo -E env PATH=$PATH python3 raspi-blinka.py

Y to reboot

pip install RPi.GPIO # for some reason RPi.GPIO does not install and is needed.

Check I2C and SPI

ls /dev/i2c\* /dev/spi\*

you should see

/dev/i2c-1 /dev/i2c-2 /dev/spidev0.0 /dev/spidev0.1

Blinka Test

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

Check the status of the samba service.
``` 
Need to come back to enter code. 
```
To save your file from `nano` hit ctrl+???
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

# Connecting Sensors

To start working with sensors we need to

## Connecting Temperature Sensor

## Connecting GPS Module

Next check to make sure serial is enabled. 

```bash
ls /dev/serial0  
```

`dev/serial0` is a good response. 


Now you can see the raw data the GPS module is passing over serial.

```bash
sudo cat /dev/serial0
```

To process that serial data, you need to install some software that understand the serial data.

Install gpsd

```bash
sudo apt-get install gpsd gpsd-clients
```
`Y`  to continue

We need to stop gpsd sockets and then disable them.

```bash
sudo systemctl stop gpsd.socket
sudo systemctl disable gpsd.socket
```

After disabling the service, now we want to run it manually.
```bash
sudo gpsd /dev/serial0 -F /var/run/gpsd.sock
```
Now you can run the following command to get data.

```bash
gps -s
```

`Ctrl + C` to exit.

And now we want this to start automatically on boot. So we must create an override file for the gpsd service.

```bash
sudo systemctl edit gpsd.service
```

Copy the following at the top of the file between two comments that say below this and above that.

```
\[Service\]
ExecStart= ExecStart=/usr/sbin/gpsd /dev/serial0 -F /var/run/gpsd.sock
Restart=on-failure
RestartSec=10
User=gpsd
Group=dialout
```

Now we need to stop any running gpsd instances to prevent any conflicts.

```bash
sudo systemctl stop gpsd.service
sudo systemctl stop gpsd.socket
sudo killall gpsd # Stronger kill, just in case
```
Now disable gpsd.socket
```bash
sudo systemctl disable gpsd.socket
```
Enable gpsd.service
```bash
sudo systemctl enable gpsd.service
```
Start gpsd.service to test
```bash
sudo systemctl start gpsd.service
```
Check the status
```bash
sudo systemctl status gpsd.service
```
If issues arise examine the journal logs for gpsd.service
```bash
journalctl -xeu gpsd.service
```
Reboot the machine
```bash
sudo reboot
```
Reconnect using PuTTY

Now you should be able to run `cgps -s` when you are logged back in. If your GPSModule is flashing once every ~15 seconds, it has a gps fix. If you do not see any data in your terminal there may be an issue.

Finally we need to make some changes to make sure we can parse the data with python.

Reboot the machine
```bash
sudo reboot
```
Activate your virtual environment
```bash
cd heat_project
source env/bin/activate
pip install gpsd-py3
```
Now we can proceed to data logging.

# Datalogging

# Executing Scripts

# Helpful Linux/RasberryPi Command Line Interface (CLI) commands
```bash
ls

mkdir

sudo raspi-config

sudo # super user do

sudo reboot # reboot

date # gets date

nmtui # NetworkManager TUI

cd # change directory

i2cdetect -y 1 # Check to see what address I^2^C devices are using.

hostname -I # this will get your ip address.
```