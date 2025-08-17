# Enabling Autostart with Crontab

To automatically run your script when the system boots, you can use the `crontab`'s `@reboot` feature. Follow these steps:

1. **Open the crontab editor:**
You may be prompted to select your text editor.

   ```sh
   crontab -e
   ```

2. **Add the following line to the end of the file:**

   ```
   @reboot /home/user/heat_project/env/bin/python /home/user/heat_project/src/capture_data.py > /home/user/heat_project/logs/cron.log 2>&1
   ```

   - This command will run `capture_data.py` using your virtual environment's Python interpreter every time the system starts.
   - Output and errors will be logged to `cron.log` in your project directory.

3. **Save and exit the editor.**

Your script will now automatically run.

Run `sudo reboot` to restart from the terminal. 

## Troublshooting
* **Permission:** Make sure your user has the correct permissions to run the file. 
* **Virtual Environment:** Check your Python interpreter path within the virtual environment is correct. Open terminal, activate your virtual environment, and type `which python`. This will return your virtual environment. We use `home/user/heat_project/env/bin/python`. 
* **Logging:** When in doubt, check the log file `cron.log`. It should collect all of the errors or output. 


If necessary, you can `kill` the tasks by running `pgrep -f capture_data.py`. This will return the Process ID (PID). Next run the following command to kill that process. 
```bash
kill <PID>
```