# Correcting WiFi Issues on Initial Boot
I persistently ran into an issue where, no matter what my Raspberry Pis would not connect to my WiFi network. I found that the Country Code had a trailing space in the initial boot file that the Raspberry Pi Imager v1.9.4 would create. 

## Update `firstrun.sh`
After you create your image on your SD card, eject it from your windows machine and the plug it back in. 

Through Windows File Explorer find the `fristrun.sh` file. Open it in a text editor. 

Search for `country=`. In my file the closing `"` would be on a new line. I made sure all the spots that had country= looked like `country=US` and any quote marks were on the same line, not on a new line. 

Save your file and eject your SD card. Install the SD card on your Pi and you should be good to go. 

Return to the [setup instructions](setup_instructions.MD).