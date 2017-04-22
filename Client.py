import socket
import time

import Message


class Client:
    def __init__(self, socket, address, client, sql):
        self.socket = socket
        self.address = address
        self.username = None
        self.has_public_key = False
        self.listen = True
        self.me = client
        self.sql = sql
        self.run(self.me)

    def run_command(self, command, string, client):
        received = Message.Message()
        me = client
        if command == received.MESSAGE:
            self.sql.add_message(me.clients_current_chat(self.address[0]), me.user_address_to_id(self.address[0]), string, "")
            print (self.username if self.username is not None else str(self.address[0])) + " sent: " + string
        elif command == received.PUBLIC_KEY:
            print time.time(), ": Received public key from ", self.address[0]
            self.sql.add_to_user(self.address[0], "publicKey", string)
            me.add_public_key(self.address[0], string)
            self.has_public_key = True
            me.send_information(ip=self.address[0])
        elif command == received.USERNAME:
            print time.time(), ": Received username from ", self.address[0]
            self.sql.add_to_user(self.address[0], "userName", string)
            me.add_username(self.address[0], string)
            self.username = string
        elif command == received.PROFILE_PICTURE:
            print time.time(), ": Received profile picture location from ", self.address[0]
            self.sql.add_to_user(self.address[0], "profileLocation", string)
            me.add_profile_picture_location(self.address[0], string)
        elif command == received.REQUEST_INFO:
            me.send_information(ip=self.address[0])
        elif command == received.REQUEST_PUBLIC_KEY:
            print time.time(), ": Received request for public key from ", self.address[0]
            me.send_public_key(ip=self.address[0])
        elif command == received.JOIN_CHAT_NAME:
            print time.time(), ": Received chat name from", self.address[0]
            details = str(string).split("'")
            details = [details[1], details[3]]
            me.construct_chat(self.address[0], details[0], name=details[1])
        elif command == received.JOIN_CHAT_PPL:
            print time.time(), ": Received chat profile picture location from", self.address[0]
            details = str(string).split("'")
            details = [details[1], details[3]]
            me.construct_chat(self.address[0], details[0], ppl=details[1])
        elif command == received.JOIN_CHAT_USERS:
            print time.time(), ": Received chat users from", self.address[0]
            print "\treceived string:\t" + str(string)
            details = [str(string).split("'")[1]]
            print "\tdissected string:\t" + str(str(string).split("', [")[1][:-2])
            details.append(str(string).split("', [")[1][:-2])
            if details[1].__contains__(","):
                details[1] = details[1].split("'")
                temporary_store = []
                for detail in details[1]:
                    try:
                        if socket.inet_aton(detail):
                            temporary_store.append(detail)
                    except:
                        pass
                details[1] = temporary_store
            else:
                details[1] = [details[1]]
                print "\tdoesn't contain ','\t" + str([details[1]])
            me.construct_chat(self.address[0], details[0], users=details[1])
        elif command == received.JOIN_CHAT_BANNED_USERS:
            print time.time(), ": Received banned chat users from", self.address[0]
            details = [str(string).split("'")[1]]
            details.append(str(string).split("', [")[1][:-2])
            if details[1].__contains__(","):
                details[1] = details[1].split("'")
                temporary_store = []
                for detail in details[1]:
                    try:
                        if socket.inet_aton(detail):
                            temporary_store.append(detail)
                    except:
                        pass
                details[1] = temporary_store
            else:
                details[1] = [details[1]]
            me.construct_chat(self.address[0], details[0], banned=details[1])
        elif command == received.CONNECT_CHAT:
            me.user_rejoin_chat(self.address[0], string)
        elif command == received.FILE:
            me.construct_file(self.address[0], string)
        elif command == received.FILE_NAME:
            me.construct_file(self.address[0], string)
        elif command == received.REQUEST_CURRENT_CHAT:
            me.send_current_chat(self.address[0])
        elif command == received.CURRENT_CHAT:
            me.set_remote_user_chat(self.address[0], string)
        elif command == received.DISCONNECT:
            print time.time(), ": Received disconnect from ", self.address[0]
            me.remove_by_address(self.address[0])
            print "removed socket from connections"
            self.close()
            print "closed socket"
            self.listen = False
            return

    def run(self, client):
        while self.listen:
            me = client
            rsa = me.rsa
            received = Message.Message()
            try:
                transmission = self.socket.recv(1024)
                if len(transmission) is not 0:
                    if self.has_public_key:
                        if len(transmission) > 256:
                            length_of_transmission = len(transmission)
                            number_of_messages = length_of_transmission / 256
                            for x in range(1, number_of_messages + 1):
                                command, string = received.decode(str(rsa.decrypt(transmission[(x-1) * 256:x*256]).decode()))
                                self.run_command(command, string, client)
                        else:
                            command, string = received.decode(str(rsa.decrypt(transmission).decode()))
                            self.run_command(command, string, client)
                    else:
                        command, string = received.decode(str(transmission).decode())
                        self.run_command(command, string, client)
                else:
                    pass
            except socket.error, exc:
                print "Error receiving data from socket with ip address " + str(self.address[0])
                print "Socket Error = " + str(exc)
                me.remove_by_address(self.address[0])
                self.close()
                print "Closed socket and removed Client from connected clients list"
                self.listen = False
                return

    def close(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
        self.listen = False
