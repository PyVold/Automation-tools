import create_topology, delete_topology, check_existing, create_connections ## importing the modules of the project
import sys, traceback, re ## system imports
from tabulate import  tabulate ## formating imports


# create a dictionary to print in tabulate
# function to extract data from orders and format in dictionary

def create_dict(order_done):
    order_table = {}
    for element in order_done:
        element_list = []
        element_list.append(element.ipadd)
        element_list.append(element.model)
        element_list.append(element.status)
        element_list.append(element.owner)
        order_table[element.name] = element_list
    return order_table

# main menu function
def main_menu():
    order_done = ""
    print("\n")
    print("           ************Welcome to VRNET LAB for automation}**************")
    while True:
        try:
            choice = input("""
                            1- Create new topology
                            2- Create a connection
                            3- Delete topology
                            4- Delete a connection
                            5- Exit
                            
                            what is your choice: """)
            if choice == "5":
                sys.exit()
            elif choice == "1":
                while True:
                    devices_count = input("""
                            How many routers to create: """)
                    try:
                        int(devices_count)
                        if int(devices_count) >= 5:
                            print("""
                            Max allowed unit count is 4""")
                            continue
                        else:
                            name_prefix = input("""
                            What is the topology/routers name prefix: """)
                            order_done = create_topology.main_function(devices_count, name_prefix)
                            break
                    except:
                        traceback.print_exc()
                        print("""
                            You have to enter numbers only!""")
            elif choice =="2":
                while True:
                    routers = check_existing.get_names()
                    routers = routers[:-1]
                    if len(routers) == 0:
                        print("""
                            No routers to connect""")
                        break
                    i = 0
                    #print(routers)
                    for router in routers:
                        i = i + 1
                        print("""
                            {} - {}""".format(i,router))

                    linkA = input("""
                            Chose link A side: """)
                    rid = int(linkA) - 1
                    routerA = routers[rid]
                    linkPA = input("""
                            which port on A side(1,2,3,4,5): """)
                    linkB = input("""
                            Chose Router side B: """)
                    rid = int(linkB) - 1
                    routerB = routers[rid]
                    linkPB = input("""
                            which port on B side(1,2,3,4,5): """)
                    linkD = input("""
                            Link name: """)
                    try:
                        order_done = create_connections.main(routerA, routerB, linkPA, linkPB, linkD )
                        if order_done == 'success':
                            print('Connection was created succesfully!')
                    except:
                        print("connection error! please try again")
                    else:
            elif choice =="3":
                while True:
                    name_prefix = input("""
                            What is the topology/routers name prefix: """)
                    order_done = delete_topology.main_function(name_prefix)
                    break
            elif choice =="4":
                while True:
                    break
            if order_done == "":
                print("""
                        JOB FAILED PLEASE CONTACT ADMIN!\n""")
            else:
                order_table = create_dict(order_done)
                print(tabulate(order_table, headers='keys', showindex=['IP', 'Model', 'Status', 'Owner']))
                break
        except:
            traceback.print_exc()
            sys.exit()

main_menu()