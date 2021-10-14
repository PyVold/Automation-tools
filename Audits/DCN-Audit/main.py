#!/usr/bin/env python
import sys, os, time, filecmp, telnetlib, csv, re, readline, getpass
import consol_get


def main_menu():
    while True:
        print("\n\nDo you want to audit one or multiple DCN devices?\n"
              "1- One device\n"
              "2- List of devices\n"
              "3- Exit\n")
        try:
            choice = input("Please enter your choice: ")
            if choice in range(1, 4):
                break
            else:
                print("\n\nERROR!\n"
                      "please chose a number from the list\n")
                continue
        except:
            print("\n\nERROR!\n"
                  "You have to chose either 1 or 2\n")
            continue
    return choice

def main_function():
    choice = main_menu()
    if choice == 1:
        pattern = "([a-zA-Z0-9]+)-([a-zA-Z0-9]+)-(r)(\d+)"
        hostname = raw_input("Write the name of the node ex. sngp-eqx-r7: ")
        file = hostname + ".csv"
        csvfile = open(file, 'w')
        username, password, enablepass = request_login_info()
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        header = ['Node', 'Interface', 'Mode', 'IP', 'Mask', 'Vlan', 'MAC address', 'description']
        writer.writerow(header)
        get_interfaces_list(hostname, username, password, enablepass, writer)
        csvfile.close()
        isrouter = re.compile(pattern)
        if isrouter.match(hostname):
            consol_get.computeDP(hostname, username, password)

    elif choice == 2:
        hostlist = raw_input("please write the device list path ex. /home/devices/list.txt:  ")
        hostnames = open(hostlist, 'r')
        username = raw_input("What is your idxxxx for DCN: ")
        password = getpass.getpass("Enter your DCN password: ")
        enablepass = getpass.getpass("Enter the enable password: ")
        for hostname in hostnames:
            pattern = "([a-zA-Z0-9]+)-([a-zA-Z0-9]+)-(r)(\d+)"
            hostname = hostname.strip()
            file = hostname + ".csv"
            csvfile = open(file, 'w')
            writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            header = ['Node', 'Interface', 'Mode', 'IP', 'Mask', 'Vlan', 'MAC address', 'description']
            writer.writerow(header)
            get_interfaces_list(hostname, username, password, enablepass, writer)
            csvfile.close()
            isrouter = re.compile(pattern)
            if isrouter.match(hostname):
                consol_get.computeDP(hostname, username, password)
    elif choice == 3:
        sys.exit()


def request_login_info():
    username = raw_input("What is your idxxxx for DCN: ")
    password = getpass.getpass("Enter your DCN password: ")
    enablepass = getpass.getpass("Enter the enable password: ")
    return username, password, enablepass

def telnet_fun(command, hostname, username, password, enablepass):
    name_pattern = "([0-9a-zA-Z]+)-([0-9a-zA-Z]+)-(r|h)(\d+)"
    #print('TRYING TO LOGIN')
    try:
        showlist = []
        upinterface = []
        tn = telnetlib.Telnet(hostname)
        connection_request = tn.expect(["Username:", "Connection refused", "Unknown host", "No route to host"])
        #print(connection_request)
        if connection_request[0] == 0:
            tn.write(username + "\n")
            tn.expect(["Password:"])
            tn.write(password + "\n")
            check_hostname = tn.expect([name_pattern+">"], timeout=4)
            if check_hostname[0] != -1:
                tn.write("enable\n")
            else:
                print("Authentication failed")
                sys.exit()
            tn.expect(["password:"])
            tn.write(enablepass + "\n")
            check_hostname_enable = tn.expect([name_pattern+"#"], timeout=4)
            if check_hostname_enable[0] == 0:
                tn.write("terminal length 0\n")
                tn.write(command + "\n")
                tn.write("exit\n")
                # read all output from the device
                showintdes = tn.read_all()
            else:
                print("Enable secret/password is wrong, can't continue executing the script!")
                sys.exit()
        else:
            print("Connection refused or timed out!")
            sys.exit()
        #return output to the recalled function
        return showintdes, hostname
    except IOError:
        print('ERRRORR')
        sys.exit()

def get_interfaces_list(hostname, username, password, enablepass,writer):
    upinterface = []
    showintdes = telnet_fun("show int des", hostname, username, password, enablepass)
    hostname = showintdes[1]
    showlist = showintdes[0].split("\n")
    for item in showlist:
        item = str(item)
        if item.find("admin down") == -1 and item.find("up") > 0:
            item = item.replace(" ", "")
            if item.find("upup") >= 0:
                item = item.replace("upup", ",")
                upinterface.append(item)
            elif item.find("updown") >=0:
                item = item.replace("updown", ",")
                upinterface.append(item)
    #print(upinterface)
    for interface in upinterface:
        inlist = []
        inlist = interface.split(",")
        if "Tu" not in inlist[0]:
            data = get_interface_config(inlist[0], hostname, username, password, enablepass)
            #write the collected data in a csv file new row
            #print(data)
            writer.writerow(data)
        else:
            data = get_tunnel_config(inlist[0], hostname, username, password, enablepass)
            writer.writerow(data)
def get_interface_config(intname, hostname, username, password, enablepass):
    description = "NA"
    mode = "NA"
    ipadd = "NA"
    smask = "NA"
    intvlan = "NA"
    show_run_config_all = telnet_fun("show run int " + intname, hostname, username, password, enablepass)
    data = []
    data.append(hostname)
    show_run_config = show_run_config_all[0].split("\n")
    checkrouter=("").join(show_run_config_all[0])
    if (checkrouter.find("dot1Q") == -1):
        for eachline in show_run_config:
            #print(eachline)]
            if eachline.find("description") >= 0:
                description = eachline.split(" ")
                description = (" ").join(description[2:])
            elif eachline.find("no ip address") >= 0:
                ipadd = "NA"
                smask = "NA"
                intvlan = "NA"
                description = "NA"
                mode = "802.1Q"
            elif eachline.find("ip address") >= 0:
                el = eachline.split(" ")
                ipadd = el[-2]
                smask = el[-1]
                mode = "L3"
                intvlan="NA"
            elif eachline.find("switchport access vlan") >= 0:
                el = eachline.split(" ")
                intvlan = el[-1]
                mode = "Access"
                ipadd = "NA"
                smask = "NA"
            elif eachline.find("trunk") >= 0:
                mode = "TRUNK"
                intvlan = "NA"
                ipadd = "NA"
                smask = "NA"
            else:
                continue
    else:
        for eachline in show_run_config:
            if eachline.find("description") >= 0:
                description = eachline.split(" ")
                description = (" ").join(description[2:])
            elif eachline.find("dot1Q") >= 0:
                el = eachline.split(" ")
                intvlan = el[-1]
                mode = "dot1Q"
            elif eachline.find("no ip address") >= 0:
                ipadd = "NA"
                smask = "NA"
                intvlan = "NA"
                description = "NA"
                mode = "802.1Q"
            elif eachline.find("ip address") >= 0:
                el = eachline.split(" ")
                ipadd = el[-2]
                smask = el[-1]

    if intname.find('Lo') >= 0 or intname.find('Se') >=0 or intname.find('CT') >=0:
        mac_address = ['NA', 'NA']
    elif intname.find('Di') >=0:
        mac_address = ['NA', 'NA']
        ipadd = "unnumbered"
        smask = "unnumbered"
    else:
        show_int_mac = telnet_fun("show int " + intname, hostname, username, password, enablepass)
        show_int_mac = show_int_mac[0].split("\n")
        mac_address_regex = re.compile(r'[0-9a-fA-F]{4}[\.][0-9a-fA-F]{4}[\.][0-9a-fA-F]{4}')
        mac_address = re.findall(mac_address_regex, show_int_mac[3])
    data.append(intname)
    data.append(mode)
    data.append(ipadd)
    data.append(smask)
    data.append(intvlan)
    data.append(mac_address[0])
    data.append(description)
    print(data)
    return data



def get_tunnel_config(intname, hostname, username, password, enablepass):
    description = "NA"
    tunnel_source = "NA"
    tunnel_destination = "NA"
    ipadd = "NA"

    show_run_config_all = telnet_fun("show run int " + intname, hostname, username, password, enablepass)
    data = []
    data.append(hostname)
    show_run_config = show_run_config_all[0].split("\n")
    checkrouter=("").join(show_run_config_all[0])
    for eachline in show_run_config:
        if eachline.find("description") >= 0:
            description = eachline.split(" ")
            description = (" ").join(description[2:])
        elif eachline.find("no ip address") >= 0:
            ipadd = "no ip address"
            mode = "802.1Q"
        elif eachline.find("ip address") >= 0:
            el = eachline.split(" ")
            ipadd = el[-2]
        elif eachline.find("tunnel source") >= 0:
            tunnel_source = eachline
        elif eachline.find("tunnel destination") >= 0:
            tunnel_destination = eachline
        else:
            continue

    data.append(intname)
    data.append("NA")
    data.append(ipadd)
    data.append("NA")
    data.append("NA")
    data.append("NA")
    data.append(description)
    data.append(tunnel_source)
    data.append(tunnel_destination)
    print(data)
    return data
main_function()
