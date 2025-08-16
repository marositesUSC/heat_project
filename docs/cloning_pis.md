# Clone Rasperry Pi
To clone your Raspberry Pi, use a memory card reader. I used a usb type b to sd card. 

1. Connect to your working Raspberry Pi. 

2. Open the application menu. 

3. Navigate to `Accessories>SD Card Copier`

![SDCardCopier](images/SD_Card_Copier.png)

4. Find your cards name. By clicking the drop down beside `Copy From Device`. There should only be one listed and this will be your current working card. 

5. Insert new card and memory card reader. 

6. Use the drop downs in the window to select your original SD card as the `Copy From Device`, and your fresh SD card as the `Copy To Device`. Click `Start`. 

7. Wait until the operation is complete. This typically takes between 10 and 20 minutes.
![CopyComplete](images/) 

8. Remove the cloned SD card from the reader and insert it into your new Raspberry Pi and boot it up. 

9. Rename new device by opening `Terminal`, type `sudo raspi-config`, click `System Options`, click `S4 Hostname`, `OK`, and enter a new hostname. Click `Ok`, `Finish`, and reboot. 

Please be sure to make sure your device is ready to start capturing data on boot up by following the [autostart instructions](enabling_autostart.md).

