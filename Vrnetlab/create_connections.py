def main(routerA, routerB, linkPA, linkPB, linkD):
    command = "sudo docker run -d --privileged --name {name} --link {ra} --link {rb} vrnetlab/vr-xcon --p2p {ra}/{la}--{rb}/{lb} --debug".format(name=linkD, ra=routerA, rb=routerB, la=linkPA, lb=linkPB)
    send_command = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    send_command.wait()
    output, err = send_command.communicate()
    print(output)
    #configure_interfaces(routerA, routerB, linkPA, linkPB, linkD)
    return 'success'