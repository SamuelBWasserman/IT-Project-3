import threading
import sys
import socket as mysoc
import hmac

def client():
    # Open sockets for auth, tlds1, tlds2
    try:
        auth_socket = mysoc.socket(mysoc.AF_INET, mysoc.SOCK_STREAM)
        print("Socket Created")
    except mysoc.error as err:
        print('{} \n'.format("socket open error ", err))
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

    # Get the IP address of the auth server and use Port 5009
    auth_server_addr = mysoc.gethostbyname(mysoc.gethostname())
    root_port = 5009

    # Get the IP address of the two TLDS servers

    # connect to the root server
    auth_server_binding = (auth_server_addr, root_port)
    auth_socket.connect(auth_server_binding)

    # Open output file
    output_file = open("RESOLVED.txt", "w")

    ts1_port = 5011
    ts2_port = 5011

    # Open text file and read line by line
    with open("PROJ3-HNS.txt", 'r') as input_file:
        lines = input_file.read().splitlines()
        for line in lines:
            words = line.split()
            word_list = []
            for word in words:
                word_list.append(word)
            # Send the key and digest to the auth server
            key = word_list[0]
            challenge = word_list[1]
            host = word_list[2]
            print "key is" + key
            print "challenge is " + challenge
            print "host is " + host
            auth_socket.send(challenge.encode('utf-8'))
            digest = hmac.new(key.encode(), challenge.encode("utf-8"))
            auth_socket.send(str(digest.hexdigest()))

            # Receive tlds server to call for info retrieval
            tlds_server = auth_socket.recv(100).decode('utf-8')

            # Send each line from the text file to the root Server
            host_information = ""

            print "Sending " + host
            if tlds_server == "TLDS1":
                # Connect to tlds1
                tlds1_addr = mysoc.gethostbyname("cpp.cs.rutgers.edu")
                print ("Connection to: " + str(tlds1_addr))
                ts1_server_binding = (tlds1_addr, ts1_port)
                ts1_socket.connect(ts1_server_binding)
                ts1_socket.send(host.encode('utf-8'))
                host_information = ts1_socket.recv(100)
            elif tlds_server == "TLDS2":
                # Connect to tlds2
                tlds2_addr = mysoc.gethostbyname("java.cs.rutgers.edu")
                print ("Connection to: " + str(tlds2_addr))
                ts2_server_binding = (tlds2_addr, ts2_port)
                ts2_socket.connect(ts2_server_binding)
                ts2_socket.send(host.encode('utf-8'))
                host_information = ts2_socket.recv(100)

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