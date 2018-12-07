import threading
import socket as mysoc

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

def auth_server():
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
        auth_socket = mysoc.socket(mysoc.AF_INET, mysoc.SOCK_STREAM)
        print("Socket root Created")
    except mysoc.error as err:
        print('{} \n'.format("socket open error ", err))

    # Get the IP of this host
    my_ip = mysoc.gethostbyname(mysoc.gethostname())
    print("My address: " + my_ip)

    # Bind to port 5009
    auth_socket.bind(('', 5009))
    print("Listening on port: 5009")

    # Listen for incoming connections
    auth_socket.listen(1)
    auth_sock_id, addr = auth_socket.accept()
    print("Connection received from " + str(addr))

    ts1_port = 5007
    ts2_port = 5008

    # Connect to tlds1
    tlds1_addr = mysoc.gethostbyname("cpp.cs.rutgers.edu")
    print ("Connection to: " + str(tlds1_addr))
    ts1_server_binding = (tlds1_addr, ts1_port)
    ts1_socket.connect(ts1_server_binding)

    # Connect to tlds2
    tlds2_addr = mysoc.gethostbyname("java.cs.rutgers.edu")
    print ("Connection to: " + str(tlds2_addr))
    ts2_server_binding = (tlds2_addr, ts2_port)
    ts2_socket.connect(ts2_server_binding)

    # Receive key + challenge + host_name strings from client
    while 1:
        # Receive challenge from client and send to both TLDS servers
        challenge = auth_sock_id.recv(100).decode('utf-8')
        print "challenge is " + challenge
        digest = auth_sock_id.recv(100).decode('utf-8')
        print "digest is " + digest

        # Send challenge to TLDS1 and receive digest
        ts1_socket.send(challenge.encode('utf-8'))
        digest_TLDS1 = ts1_socket.recv(100).decode('utf-8')
        print "Received digest from TLDS1: " + digest_TLDS1

        # Send challenge to TLDS2 and receive digest
        ts2_socket.send(challenge.encode('utf-8'))
        digest_TLDS2 = ts2_socket.recv(100).decode('utf-8')
        print "Received digest from TLDS2: " + digest_TLDS2

        # Compare digests and send the correct one back to the client
        if digest == digest_TLDS1:
            auth_sock_id.send("TLDS1".encode('utf-8'))
        elif digest == digest_TLDS2:
            auth_sock_id.send("TLDS2".encode('utf-8'))
        else:
            print "No digest matched the given digest"


thread = threading.Thread(name='auth_server', target=auth_server)
thread.start()
exit()