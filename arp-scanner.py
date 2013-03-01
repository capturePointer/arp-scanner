#!/usr/bin/env python
import multiprocessing
import subprocess
import sys
import socket
import os
from netaddr import *
from netifaces import interfaces, ifaddresses, AF_INET

listone = []
def get_ip_list(ip_network):
	ip_list = []
	for ip in ip_network.iter_hosts():
		ip_list.append(str(ip))
	
	return ip_list

def call_arping(ip):
	try:
		arping_output = subprocess.check_output(["/usr/sbin/arping", "-r", "-c1", ip])
	except subprocess.CalledProcessError:
		return

	try:
		hostname = socket.gethostbyaddr(ip)[0]
	except socket.herror:
		hostname = ""

	for mac_string in arping_output.splitlines():
		mac = EUI(mac_string)
	
		try:
			vendor = mac.oui.registration().org

		except NotRegisteredError:
			vendor = ""

		sys.stdout.write("| %14s | %17s | %40s | %34s |\n" %(ip, str(mac), vendor, hostname))

if not os.geteuid()==0:
	sys.exit("\nOnly root can run this script")


for ifaceName in interfaces():
	if ifaddresses(ifaceName).has_key(AF_INET) and not ifaceName == "lo":
		for ipinfo in ifaddresses(ifaceName)[AF_INET]:
			sys.stdout.write("|------------------------------------------------- Interface %5s --------------------------------------------------|\n" %(ifaceName))
			address = ipinfo['addr']
			netmask = ipinfo['netmask']

			ip = IPNetwork('%s/%s' % (address, netmask))

			pool = multiprocessing.Pool(len(ip))
			rval = pool.map_async(call_arping, get_ip_list(ip))
			rval.get()
			pool.close()
			sys.stdout.write("|--------------------------------------------------------------------------------------------------------------------|\n")
			exit


	else:
		continue

