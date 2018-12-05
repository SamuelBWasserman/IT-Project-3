import threading
import sys
import socket as mysoc

def populate_DNS_dict():
    dns_table = {}
    with open(sys.argv[3], 'r') as input_file:
        lines = input_file.read().splitlines()
        for line in lines:
            words = line.split()
            word_list = []
            for word in words:
                word_list.append(word)
            dns_table[word_list[0]] = (word_list[1], word_list[2])
    return dns_table


""" Returns the apropriate TS server given com or edu."""
def get_ts_server_name(dns_dict, type):
    for key in dns_dict.keys():
        flag = dns_dict[key][1]
        if flag == "NS":
            if type == "com":
                if "com" in key:
                    return key
            else:
                if "edu" in key:
                    return key

def print_dict(dict):
    for key in dict.keys():
        print ("key: " + key)
        print ("value: " + str(dict[key]))

def root_server():
    # Create three sockets. One for client, TLDS1 and TLDS2
    try:
        ts1_socket = mysoc.socket(mysoc.AF_INET, mysoc.SOCK_STREAM)
        print("Socket ts1 Created")
    except mysoc.error as err:
        print('{} \n'.format("socket open error ", err))
    try:
        ts2_socket = mysoc.socket(mysoc.AF_INET, mysoc.SOCK_STREAM)
        print("Socket ts2 Created")
    except mysoc.error as err:
        print('{} \n'.format("socket open error ", err))
    try:
        root_socket = mysoc.socket(mysoc.AF_INET, mysoc.SOCK_STREAM)
        print("Socket root Created")
    except mysoc.error as err:
        print('{} \n'.format("socket open error ", err))

    # Get the IP of this host
    my_ip = mysoc.gethostbyname(mysoc.gethostname())
    print("My address: " + my_ip)

    # Bind to port 5009
    root_socket.bind(('', 5009))
    print("Listening on port: 5009")

    # Listen for incoming connections
    root_socket.listen(1)
    root_sock_id, addr = root_socket.accept()
    print("Connection received from " + str(addr))

    # Create the DNS dictionary
    dns_dict = populate_DNS_dict()

    ts1_port = 5007
    ts2_port = 5008
    # Receive host names from client
    is_com_connected = False
    is_edu_connected = False
    while 1:
        host_name = root_sock_id.recv(100).decode('utf-8')
        print "Received " + host_name
	try:
            # query the dictionary and return the resultant string
            entry = dns_dict[host_name]
            return_string = host_name + " " + entry[0] + " " + entry[1]
            print ("Found:" + return_string)
	    root_sock_id.send(return_string.encode('utf-8')) 
            # host name not found. Try and find it in a TS server
        except KeyError:
	    print host_name + " not found in dictionary here"
            if "com" in host_name:
		if not is_com_connected:
                	com_server_addr = mysoc.gethostbyname(sys.argv[1])
                	print ("Connection to: " + str(com_server_addr))
                	ts_server_binding = (com_server_addr, ts1_port)
                	ts1_socket.connect(ts_server_binding)
                	is_com_connected = True
		# Send the host name for lookup in ts server
                ts1_socket.send(host_name.encode('utf-8'))
                host_info = ts1_socket.recv(100)
		if host_info:
			print host_info
			root_sock_id.send(host_info.encode('utf-8'))
            elif "edu" in host_name:
                if not is_edu_connected:
			edu_server_addr = mysoc.gethostbyname(sys.argv[2])
                	print("Connection to: " + str(edu_server_addr))
                	ts_server_binding = (edu_server_addr, ts2_port)
                	ts2_socket.connect(ts_server_binding)
                	is_edu_connected = True
		# Send the host name for lookup in ts server
                ts2_socket.send(host_name.encode('utf-8'))
                host_info = ts2_socket.recv(100)
		if host_info:
			print host_info
			root_sock_id.send(host_info.encode('utf-8'))
	    else:
		error_string = "Hostname - Error:HOST NOT FOUND"
		root_sock_id.send(error_string.encode('utf-8'))


thread = threading.Thread(name='root_server', target=root_server)
thread.start()
exit()
