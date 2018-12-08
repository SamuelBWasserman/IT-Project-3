import threading
import socket as mysoc
import hmac

def make_dic():
    dns_table = {}
    with open("PROJ3-TLDS2.txt", 'r') as input_file:
        lines = input_file.read().splitlines()
        for line in lines:
            words = line.split()
            word_list = []
            for word in words:
                word_list.append(word)
            dns_table[word_list[0]] = (word_list[1], word_list[2])
    return dns_table

def read_key():
    with open('PROJ3-KEY2.txt','r') as input_file:
        lines = input_file.read().splitlines()
        return lines[0]

def ts_server():
    try:
        ts_soc = mysoc.socket(mysoc.AF_INET, mysoc.SOCK_STREAM)
        print("[S]: Server socket created")
    except mysoc.error as err:
        print('{} \n'.format("socket open error ", err))
    try:
        client_sock = mysoc.socket(mysoc.AF_INET, mysoc.SOCK_STREAM)
        print("[S]: Server socket created")
    except mysoc.error as err:
        print('{} \n'.format("socket open error ", err))


    ts_soc.bind(('', 5008))
    ts_soc.listen(1)

    client_sock.bind(('', 5011))
    client_sock.listen(1)

    host = mysoc.gethostname()
    print("[S]: Server host name is: ", host)
    localhost_ip = (mysoc.gethostbyname(host))
    print("[S]: Server IP address is  ", localhost_ip)
    ts_sockid, addr = ts_soc.accept()
    print ("[S]: Got a connection request from a auth server at", addr)
    client_sock_id, client_addr = "", ""

    #load data to dictionary
    dns_table = make_dic()

    # Read the key specified for this server
    key = read_key()
    print "key is " + key

    is_client_connected = False
    while 1:
        # Receive challenge from auth server and return a digest
        challenge = ts_sockid.recv(100).decode('utf-8')
        print "challenge is " + challenge
        digest = hmac.new(key.encode(), challenge.encode("utf-8"))
        print "digest is " + str(digest.hexdigest())
        # Send the digest back to the auth server
        ts_sockid.send(str(digest.hexdigest()))

        flag = ts_sockid.recv(100).decode('utf-8')
        if flag == "ts2":
            print "This server will be called"
            if is_client_connected == False:
                print "Waiting for client to connect"
                client_sock_id, client_addr = client_sock.accept()
                print ("[S]: Got a connection request from a client at", client_addr)
                is_client_connected = True
            hostname = client_sock_id.recv(100).decode('utf-8')
            print hostname

            #check the dictonary for match
            try:
                print "checking table for hostname"
                data = dns_table[hostname]
                print data
                print "Found Host"
                #the string to return if there is a match
                match_string = hostname + " " + data[0] + " " + data[1]
                print match_string
                #send the string to the client
                client_sock_id.send(match_string.encode('utf-8'))
            except KeyError:
                print "Host not found"
                msg = "Hostname - Error:HOST NOT FOUND"
                client_sock_id.send(msg.encode('utf-8'))


t1 = threading.Thread(name='ts_server', target=ts_server)
t1.start()
exit()