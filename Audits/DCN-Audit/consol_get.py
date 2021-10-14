#!/usr/bin/python

######################################################################
# Read me:
# Program arguments : nameprogram.py resultfile logfile.
# Looking for asynch port of each terminal server that are connected 
# to a port console of a router.
# Log file : 
# - port ok : the asynch port is connected to a console port
# - time out : no response from server
# - connection refused
# Result file:
# - host ; telnet host port 
######################################################################


import re
import sys, time
import signal, os
import pexpect
import telnetlib, socket
import errno, csv

def general_vars():
	# config directory and dcnrouters file
	confdir = '/data/marvin/configs/conf/'
	dcnrf = '/data/marvin/etc/dcnrouters.txt'
	# default port
	dp = 2000

	# Async port
	hi = 256
	mi = 16
	lo = 1

	# dictionary of device => list{port}
	hostPortDict = {}
	hostIpDict = {}

	pattern = "([a-zA-Z0-9]+)-([a-zA-Z0-9]+)-(r|h)(\d+)"
	patternSucces = ">$"
	return confdir, dcnrf, dp, hi, mi, lo, hostPortDict, hostIpDict, pattern, patternSucces

def computeDP(hostname, username, password):

	consol_file = hostname + ".csv"
	consol_csv = open(consol_file, 'a+')
	consol_writer = csv.writer(consol_csv, quoting=csv.QUOTE_NONNUMERIC)
	consol_writer.writerow([])
	consol_writer.writerow([])
	consol_header = ['Node', 'remote Node', 'console port', 'console interface']
	consol_writer.writerow(consol_header)
	confdir, dcnrf, dp, hi, mi, lo, hostPortDict, hostIpDict, pattern, patternSucces=  general_vars()
	# print(confdir)
	# get the device name
	device = hostname
	# host = device
	ip = None
	username = username
	password = password
	# check if the file containt Async ports
	f = open(confdir + hostname +'.intdcn.bc.conf', 'r')
	for l in f:
		# the file containt at least an Async port
		if 'Async' in l:
			# compute the port from the readed line if it exist
			port, asport = getPortFromLine(l)
			if port is not None:

				# check if the port is the console port
				res = isPortConsole(device, port, username, password)
				if isinstance(res, str):  # res equals to 1
					addPort(res, device, port)
					consol_data = [hostname, res, port, asport]
					consol_writer.writerow(consol_data)

				elif res == -1:
					ip = getDeviceIpAddress(device)
					if ip is None:
						break

					res = isPortConsole(ip, port, username, password)

					if isinstance(res, str):
						addPort(res, ip, port)
						consol_data = [hostname, res, port, asport]
						consol_writer.writerow(consol_data)
					device = ip

	f.close()


# computation of the port from the asynch port

def getPortNumber(asyncPort):
	confdir, dcnrf, dp, hi, mi, lo, hostPortDict, hostIpDict, pattern, patternSucces = general_vars()
	# split the async port to get the 3 number
	nbrs = asyncPort.split('/')

	# computation method => 2000 + (256*i) + (16*j) + (1*t)
	n1 = int(nbrs[0])
	n2 = int(nbrs[1])
	n3 = int(nbrs[2])

	port = dp + (hi * n1) + (mi * n2) + (lo * n3)
	print(port)
	return port


# get the device name from the file name
def getDeviceName(fName):
	# split the string line to get the device name
	splits = fName.split('.')

	# get the device name
	device = splits[0]

	return device


# look for the ip address of the device if needed
def getDeviceIpAddress(host):
	# return the ip if it already known
	if host in hostIpDict:
		return hostIpDict[host]

	# use the ip address if the hostname does not work
	ip = None
	f = open(dcnrf, 'r')
	for l in f:
		if host in l:
			spl = l.split(';')
			ip = spl[1]
			break

	hostIpDict[host] = ip

	# close the file
	f.close()

	return ip


# addtion of the port to the result file
def addPort(host, ip, port):
	line = host + ':telnet ' + str(ip) + ' ' + str(port) + '\n'
	print(line)


# check if the connection port is the port console
# return : 1 if the port is console port; 0 if the port is not console port or if the connection is refused; -1 if the hostname/ip make an error
def isPortConsole(host, PORT, username, password):
	# print '=========================> ' + str(host) + ' ' + str(PORT)
	# generate a telnet child application to simulate a connection if there is an host
	confdir, dcnrf, dp, hi, mi, lo, hostPortDict, hostIpDict, pattern, patternSucces=  general_vars()
	try:
		t = telnetlib.Telnet(host, PORT)
		i = t.expect(["Username:", "Connection refused", "Unknown host", "No route to host"])
		if i[0] == 0:
			t.write(username + '\n')
			t.expect(["Password:"])
			t.write(password + '\n')

			try:
				t.expect(["(Signon successful.)+"])
				t.write("\r")

				r = t.expect([pattern], timeout=2)
				if r[0] != -1:
					# fetch the host console from the string
					split = r[2].split('\n')
					res = split[-1].split(' ')

					t.close()
					return res[-1]
				else:
					print("not ok")

			except EOFError:  # pexpect.TIMEOUT, KeyboardInterrupt:
				t.close()
				return 0


	except socket.timeout:
		print("TIMEOUT")
		# close the spawned child
		t.close()
		return -1

	except socket.error as serr:
		if errno.ECONNREFUSED == serr[0]:
			# connection refused
			return 0
		else:
			return -1


# compute asynch ports of a device that are connected to a console port



# compute a port from the asynch port of a line
def getPortFromLine(l):
	confdir, dcnrf, dp, hi, mi, lo, hostPortDict, hostIpDict, pattern, patternSucces = general_vars()
	res = re.search('Async(\d*/\d*/\d*)', l)
	if res:
		asport = res.group(1)

		# convert Async port number to real port number
		port = getPortNumber(asport)

		return port, asport

	return None

