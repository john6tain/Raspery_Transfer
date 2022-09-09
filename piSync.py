import paramiko
from scp import SCPClient
import os
import sys
from colorama import Fore
from colorama import Style
import time
import subprocess
from getpass import getpass

transfered_list=[]
error_counter=0

def progress(filename, size, sent):
    sys.stdout.write("%s\'s progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100) )

def ssh_client(host,username,password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    return client

def get_file():
    if keep_log is True and os.path.isfile('pi_log.txt') is True:
        skiped_files = open('pi_log.txt', 'r')
        skiped_files = list(filter(lambda score: score !='',skiped_files.read().split('\n')))
        #print(skiped_files)
    else:
        skiped_files=[]
    dict_values = dict()
    dict_values['directory_name'] = local_directory_path
    dict_values['my_file_list'] = sync_lists(os.listdir(dict_values['directory_name']),skiped_files)
    return dict_values

def exec_hdd_restart():
    stdin, stdout, stderr = ssh.exec_command('sudo service mount-hdd restart')
    stdin.write(remote_pass+'\n')
    stdin.flush()
    #ssh.close()
    for line in stdout:
        print(line.strip('\n'))
    transfer_files(sync_lists(get_file()['my_file_list'],transfered_list))

def exec_full_restart():
    global ssh
    stdin, stdout, stderr = ssh.exec_command('sudo reboot')
    stdin.write(remote_pass+'\n')
    stdin.flush()
    #ssh.close()
    time.sleep(90)
    ssh.close()
    ssh= ssh_client(remote_host, remote_user, remote_pass)
    transfer_files(sync_lists(get_file()['my_file_list'],transfered_list))

def transfer_files(my_file_list):
    my_file_list.sort()
    has_error=False
    global error_counter
    for index,file in enumerate(my_file_list):
        local_file = get_file()['directory_name']+file
        remote_file = remote_directory_path+file
        if check_existing_files(local_file,remote_file) is not True:
            try:
                with SCPClient(ssh.get_transport(), progress = progress) as scp:
                    scp.put(local_file, remote_file)
                    print(f"({index}/{len(get_file()['my_file_list'])}) {Fore.GREEN}File {file} tranftered OK!{Style.RESET_ALL}")
                    transfered_list.append(file)
                    error_counter=0
            except Exception as e:
                print(f"ERROR ({error_counter}) {e}")
                has_error=True
                error_counter+=1
                break
            finally:
                if error_counter > 5:
                    print("Wating Full Restart!!")
                    exec_full_restart()
                elif has_error is True:
                    print("Wating HDD Restart!!")
                    exec_hdd_restart()
        else:
            if keep_log is True:
                log_file = open("pi_log.txt","a")
                log_file.write(file+"\n")
                log_file.close()
            print(f"({index}/{len(get_file()['my_file_list'])}) {Fore.RED}File {file} already exists!{Style.RESET_ALL}")

def sync_lists(original,transfered):
    original.sort()
    transfered.sort()
    result=list(set(original) - set(transfered))
    result.sort()
    return result

def check_existing_files(local_file, remote_file):
    local_result = subprocess.run(['cksum', local_file], stdout=subprocess.PIPE).stdout.decode('utf-8').split()[0]
    stdin, stdout, stderr=ssh.exec_command('cksum '+remote_file)
    remote_result = stdout.readlines()
    remote_result = remote_result[0].split()[0] if len(remote_result) > 0  else -1
    #print('LOCAL ',local_result)
    #print('REMOTE ',remote_result)
    return local_result == remote_result

def get_user_details():
    global remote_host
    global remote_user 
    global remote_pass
    global local_directory_path
    global remote_directory_path
    global ssh
    global keep_log
    
    if len(sys.argv) >=6:
        remote_host=sys.argv[1]
        remote_user=sys.argv[2]
        remote_pass=sys.argv[3]
        local_directory_path=sys.argv[4]
        remote_directory_path=sys.argv[5]
        keep_log=True if len(sys.argv)>6 and sys.argv[6] == 'Y' else False
    else:
        remote_host=input('Enter remote IP: ')
        remote_user=input('Enter remote username: ')
        remote_pass=getpass('Enter remote password: ')
        local_directory_path=input('Enter local directory path: ')
        remote_directory_path=input('Enter remote directory path: ')
        keep_log=True if input('Do you want to enable pi_log.txt helper(Y/N): ')== 'Y' else False 
    
    if keep_log is True and os.path.isfile('pi_log.txt') is True:
        subprocess.run(['rm', 'pi_log.txt'], stdout=subprocess.PIPE)
        
    ssh= ssh_client(remote_host, remote_user, remote_pass)    
    transfer_files(get_file()['my_file_list'])
   
    
get_user_details()
ssh.close()
