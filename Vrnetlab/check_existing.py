import subprocess


def get_names():
    routers = []
    command = "sudo docker ps"
    send_command = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    send_command.wait()
    output, err = send_command.communicate()
    output = output.decode()
    output = output.split("\n")[1:]
    for instance in output:
        if "xcon" in instance:
            pass
        else:
            router = instance.split(" ")[-1]
            routers.append(router)
    return routers