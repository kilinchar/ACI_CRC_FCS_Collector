# Use this file to store your credentials for the code samples if you want.
# All code samples assume the config.py file is located in the same directory as the code.
# In order to store password, windows environment variables is utilised. Check for details on Corey Schafer's video ( https://www.youtube.com/watch?v=IolxqkL7cD8 )
import os
controller = "10.66.51.90"
controller2 = "10.122.189.163"
controller3 = "10.98.44.151"
controllerhcsank = "172.19.10.7"
controllerhcsist = "172.19.24.7"
username = "admin"
password = "cisco!123"
# password = os.environ.get("ACI_PASS")
username_hcs = os.environ.get("HCS_ACI_USER")
password_umk = os.environ.get("UMK_ACI_PASS")
password_hcs = os.environ.get("HCS_ACI_PASS")
dbuser = "postgres"
dbpass = "cisco!123"