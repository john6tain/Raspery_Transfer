# Raspery_Transfer
Quick Python 3 script that helps you to transfer and sync files to Raspberry
## Seteps to run it 
### Install all dependencies with pip3
### Run the piSync.py
## There are 2 was to run the script with or without params
### 1.Without params ./piSync.py
#### The application will ask you to manualy enter all teh params with input prompt
### 2.Wtith params: python3 ./piSync.py remote_host remote_user remote_pass local_directory_path remote_directory_path keep_log
#### remote_host - Ip address of the Raspberry with enabled SSH
#### remote_user - SSH username (WARNING!! the user must in the SUDO group to restart the HDD and the PI on FAIL)
#### remote_pass - user's password
#### local_directory_path - The main direcotry with the files that you want to transfer on the local machine(Warning!! all the files from the dir will be transferred) 
#### remote_directory_path - The remote direcotry on the Raspberry that will receive the files 
#### keep_log - To enable logging of transferred files in pi_log.txt (Unstable feture)