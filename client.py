import threading
import sys
import socket as mysoc

def client():
    # Open one socket for the root server
    try:
        root_socket = mysoc.socket(mysoc.AF_INET, mysoc.SOCK_STREAM)
        print("Socket Created")
    except mysoc.error as err:
        print('{} \n'.format("socket open error ", err))

    # Get the IP address of the root server and use Port 5009
    root_server_address = mysoc.gethostbyname(sys.argv[1])
    root_port = 5009

    # connect to the root server
    root_server_binding = (root_server_address, root_port)
    root_socket.connect(root_server_binding)

    # Open output file
    output_file = open("RESOLVED.txt", "w")
    
    # Open text file and read line by line
    with open(sys.argv[2], 'r') as input_file:
        host_name_list = input_file.read().splitlines()
        for host in host_name_list:
            # Send each line from the text file to the root Server
            print "Sending " + host
	    root_socket.send(host.encode('utf-8'))
            host_information = root_socket.recv(100)
            if not host_information:
		print "Error with " + host
                continue
            else:
		print "Writing " + host_information + " to file"
		output_file.write(host_information + "\n")

    input_file.close()
    output_file.close()
    exit()


thread = threading.Thread(name='client', target=client)
thread.start()
