import subprocess, getpass, json, ast, paramiko, sys, os, time, readline, socket

all_devices = []
class Device:
    def __init__(self, Router_Name):
        self.name = Router_Name
        self.ipadd = ''
        self.model = ''
        self.status = 'Not configured'
        self.owner = ''
        self.index = 0

def main_function(devices_count, name_prefix):
    devices_count = int(devices_count)
    indexing = 0
    for i in range(devices_count):
        router_name = "{}-{}".format(name_prefix, i+1)
        all_devices.append(Device(router_name))
        command = "sudo docker run -d --privileged --name {}  vrnetlab/vr-sros:20.10.R1".format(router_name)
        send_command = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
        # get the output as a string
        output = send_command.stderr.read()
        if b"Conflict" in output:
            all_devices[indexing].status = "Already exists"
        get_ipaddress_command = "sudo docker inspect {}".format(router_name)
        get_image = "sudo docker inspect {} | grep vrnetlab/".format(router_name)
        send_command = subprocess.Popen(get_ipaddress_command, shell=True, stdout=subprocess.PIPE)
        send_command.wait()
        output, err = send_command.communicate()
        output = output.split(b"\"IPAddress\": \"")
        ipaddress = output[1].split(b"\",")
        all_devices[indexing].ipadd = ipaddress[0].decode()
        key_regen_command = "ssh-keygen -f ~/.ssh/known_hosts -R {}".format(ipaddress[0].decode())
        send_command = subprocess.Popen(key_regen_command, shell=True, stdout=subprocess.PIPE)
        output, err = send_command.communicate()
        send_command = subprocess.Popen(get_image, shell=True, stdout=subprocess.PIPE)
        send_command.wait()
        output, err = send_command.communicate()
        output = output.split(b"/")
        output = output[1].split(b"\"")
        all_devices[indexing].model = output[0].decode()
        all_devices[indexing].owner = getpass.getuser()
        all_devices[indexing].index = indexing
        print("Device created: " + all_devices[indexing].name)
        print("IP Address: " + all_devices[indexing].ipadd)
        print("Model: " + all_devices[indexing].model)
        print("Status: " + all_devices[indexing].status)
        print("Owner: " + all_devices[indexing].owner)
        indexing = indexing + 1
    ssh_function_loop()
    return all_devices

def ssh_function_loop():
    status = "not completed"
    completed = []
    while status == "not completed":
        for device in all_devices:
            if len(completed) == len(all_devices):
                print("Job is Complete")
                status = "completed"
                break
            if device.status == "Already exists":
                #print("\nRouter with name {} {}\n".format(device.name, device.status))
                if device.name in completed:
                    pass
                else:
                    completed.append(device.name)
                continue
            if device.status == "Ready":
                if device.name in completed:
                    pass
                else:
                    completed.append(device.name)
                continue
            hostname = device.name
            ipadd = device.ipadd
            username = 'admin'
            password = 'admin'
            port = 22
            if "sros" in device.model:
                script_dir = os.path.dirname(__file__)
                rel_path = "INIT_Nokia2010.txt"
                comfile_location = os.path.join(script_dir, rel_path)
                comfile = open(comfile_location)
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print('Now trying connecting to {}'.format(hostname))
            paramiko.util.log_to_file("main_paramiko_log.txt", level="INFO")
            try:
                client.connect(ipadd, port=port, username=username, password=password, banner_timeout=15)
            except paramiko.ssh_exception.SSHException:
                #print('Error reading SSH protocol banner for router {}'.format(hostname))
                time.sleep(10)
                break
            except paramiko.ssh_exception.NoValidConnectionsError as e:
                print('SSH transport is not ready... for router {}'.format(hostname))
                break
            except socket.timeout:
                print("Socket Timeout...")
                break
            chan = client.invoke_shell()
            chan.send('configure system name {}'.format(hostname))
            for eachline in comfile:
                chan.send(eachline)
                time.sleep(1)
                print(chan.recv(1000))
            device.status = 'Ready'
            print('\nDevice {} is configured and ready ...\n'.format(hostname))
            completed.append(device.name)
            client.close()
            comfile.close()