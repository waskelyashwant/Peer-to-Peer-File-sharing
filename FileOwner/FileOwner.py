import os.path
from os import path
import sys
import socket
from sys import argv
from pathlib import Path
from _thread import *

list_peer = {}
master_DB = {}
port_DB = {}

class Constants:
    LIST = "LIST"
    NAME = "NAME"
    REQUEST = "REQUEST"
    DATA = "DATA"
    REGISTER = "REGISTER"
    PEER = "PEER"
    CLOSE = "CLOSE"
    BRACE_OPEN = "["
    CONNECTION_ESTABLISHED = "] connection established from " 
    PEER_LIST = "[Owner] Peer list:" 
    PEER_U_D = "[Owner] Transmitting Upload/Download peers" 
    OWNER_UP_RUN = "[Owner] Owner is up and running:" 
    OWNER_GETS_MESSAGE = "[Owner] gets message (" 
    FROM = ") from " 
    ERROR_OCCURED = "Error Occurred" 
    FILE_OWNER = "File Owner" 
    WAITING_PEER = " is waiting for peers..."
    CONFIG = "CONFIG" 
    OWNER_DIR = "OwnerDir" 
    OWNER_DIR_1 = "OwnerDir/" 
    BLOCK = "Block -->" 
    BYTES = " bytes" 
    OWNER_TOTAL = "[Owner] Total " 
    BLOCKS = " Blocks" 
    EQUALS = " = " 
    SPACE = " " 


# This class contains all the methods required by the File Owner.
class OwnerProcess:
    # protected ObjectOutputStream object_output_stream
    # protected ObjectInputStream input_stream
    peer_name = 0
    _current_block = {}
    file_name = ""
    peer_id = 0
    port = 0

    # Creates the owner process that communicates with peers for all the transactions
    # file chunks
    # socket class that accepts connections from peer clients
    # ObjectOutputStream that writes to the specified OutputStream
    # deserialize

    def __init__(self, block, file_name, con, addr, peer_port, thread_number, peer_id, port):
        # print("Inside init of OwnerProcess")
        self._current_block = block
        self.file_name = file_name
        self.con = con
        self.addr = addr
        self.clientId = peer_port
        self.peer_name = thread_number
        self.peer_id = peer_id
        self.port= port
        print(Constants.BRACE_OPEN + "Thread-" + str(self.peer_name) + Constants.CONNECTION_ESTABLISHED + str(addr[1]))

    # Communicates with peer for transferring messages
    # msg message to be transferred

    def transferMessageToPeer(self, msg):
        try:
            self.con.send(msg.encode())
        except:
            print("Exception in transferMessageToPeer function")

    _clientId = -1

    # sends reponse to every peer

    # message message to be transferred
    # x

    def __replyToIndividualPeerRequest(self,message, x):
        if message == Constants.LIST:
            self.__performListOperation()
        elif message == Constants.NAME:
            print(self.file_name)
            self.transferMessageToPeer(str(self.file_name))
        elif message == Constants.REQUEST:
            self.__performRequestOperation(x)
        elif message == Constants.DATA:
            x = int(self.con.recv(1024).decode())
            chunk = self.con.recv(1024)
        elif message == Constants.REGISTER:
            self.__performRegisterOperation()
        elif message == Constants.PEER:
            self.__performPeerOperation()
        elif message == Constants.CLOSE:
            self.__performCloseOperation()

    # List all the blocks

    def __performListOperation(self):
        y = len(self._current_block)
        arrayList = []
        for i in range(0, y):
            if i in self._current_block.keys():
                arrayList.append(i)

        arrayList = str(arrayList)
        arrayList = arrayList.encode()
        self.con.send(arrayList)


    # sends download and upload neighbour to individual peer

    def __performPeerOperation(self):
        print(Constants.PEER_LIST)
        self.con.send(("abc").encode())
        peer_id = self.con.recv(1024)
        for peer in list_peer.keys():
            print(peer , " ")

        self.con.send(("abc").encode())
        peer_port = int(self.con.recv(1024).decode())
        self.con.send(("abc").encode())
        download_port = int(self.con.recv(1024).decode())
        print(peer_port , " " , download_port)
        print(Constants.PEER_U_D)
        self.con.send(str(list_peer).encode())
        self.con.recv(1024)
        download_neighbor_id=0
        if download_port in master_DB.keys():
            download_neighbor_id = master_DB[download_port]
        self.transferMessageToPeer(str(download_neighbor_id))
        self.con.recv(1024)
        upload_neighbor_id = self.getUploadNeighbor(peer_port)
        self.transferMessageToPeer(str(upload_neighbor_id))


    # Gets the upload neighbor of a peer
    def getUploadNeighbor(self, peer_port):
        upload_neighbor_id = 0
        for i in port_DB.keys():
            if port_DB[i].getDownload_port() == peer_port:
                peer_id = port_DB[i].getPeer_port()
                upload_neighbor_id = master_DB[peer_id]
                break
        return upload_neighbor_id

    def __performCloseOperation(self):
        self.con.close()
        list_peer.pop(self.clientId)

    def __performRequestOperation(self,x):
        self.con.send(bytes("yashwant", 'utf-8'))
        x = int(self.con.recv(1024).decode())
        self.transferMessageToPeer(str(x))
        self.con.recv(1024).decode()
        self.con.send(self._current_block[x])


    def __performRegisterOperation(self):
        peer = self.peer_id
        list_peer[self.peer_id] = self.port
        print(peer)
        print(list_peer)
        port = self.port
        print(port)
        self.transferMessageToPeer(str(peer))
        self.con.recv(1024).decode()
        self.transferMessageToPeer(str(port))

    def __initiate_run(self):
        print(Constants.OWNER_UP_RUN)
        input_from_peer = ""
        while True:
            try:
                input_from_peer = self.con.recv(1024)
                break
            except:
                print("Exception at __initiate_run() in OwnerProcess class")
                exit()
                break

        msg = str(input_from_peer.decode())
        print(Constants.OWNER_GETS_MESSAGE + msg + Constants.FROM + str(self.clientId))
        return msg


    # If this thread was constructed using a separate
    # run object, then that
    # objects method is called
    def run(self):
        # print("Hello")
        while True:
            # try:
                message = self.__initiate_run()
                print(Constants.OWNER_GETS_MESSAGE + message + Constants.FROM + str(self.clientId))
                x = -1
                self.__replyToIndividualPeerRequest(message, x)
            # except:
            #     print(Constants.ERROR_OCCURED)
            #     print("Error in run() function in OwnerProcess class")
            #     list_peer.pop(self.clientId)
            #     return


# Class maintaining download and upload ports of different peers
class PortDB:
    __peer_port = 0
    __download_port = 0

    def __init__(self, peer_port, download_port):
        self.__peer_port = peer_port
        self.__download_port = download_port

    def getDownload_port(self):
        return self.__download_port

    def getPeer_port(self):
        return self.__peer_port




# Class containing all the methods required by a FileOwner.
class FileOwner:
    thread_number = -1
    __file_name = ""
    __owner_port = 0
    # ServerSocket = socket.socket()
    ServerSocket=socket.socket()
    peer_id = 0
    port = 0

    # peer configs
    FILE_MAX_SIZE = 1024 * 100
    read_buffer_size = 1024

    # chunk_id and chunk
    file_block_list = {}
    peerName = Constants.FILE_OWNER

    # Creates the FileOwner that distributes the file chunks to different peers.
    # _owner_port
    # _file_name

    def __init__(self, owner_port, file_name):
        # print("constructor")
        if file_name != None and path.exists(file_name):
            self.__file_name = file_name

        self.__owner_port = int(owner_port)

        try:
            # host = socket.gethostname()
            host = "localhost"
            self.ServerSocket.bind((host, self.__owner_port))
            self.ServerSocket.listen(5)
        except:
            print("program exited")
            sys.exit(1)

        # Init file chunk list
        self.__divideFileIntoChunks()

    # Initiates the file owner process

    def initiateOwner(self):
        #try:
            while True:
                self.thread_number+=1
                print(self.peerName + Constants.WAITING_PEER)
                con, addr = self.ServerSocket.accept()
                print("A new connection request has been accepted")
                message_from_client = con.recv(1024).decode()
                con.send(("124").encode())
                print("message from client :: " + message_from_client)
                if message_from_client.upper().startswith(Constants.CONFIG):
                    split_string = message_from_client.split(" ")
                    id = int(split_string[1])
                    peer_port = int(split_string[2])
                    download_port = int(split_string[3])
                    self.peer_id = id
                    self.port = peer_port
                    self.__createDB(id, peer_port, download_port)

                print(self.__file_name)
                op = OwnerProcess(self.file_block_list, self.__file_name, con, addr, self.port, self.thread_number, self.peer_id, self.port)
                start_new_thread(op.run,())

        # except:
        #     print("An exception occured")


    # creates Master database which stores different peers and their ports.
    # id peer id
    # peer_port peer port
    # download_port port of download neighbour
    def __createDB(self, id, peer_port, download_port):
        master_DB[peer_port] = id
        port_DB[id] = PortDB(peer_port, download_port)


    def _chunk_file(self, file, extension):
        current_chunk_size = 0
        current_chunk = 0
        print(Constants.BLOCK + str(current_chunk) + Constants.EQUALS + "102400" + Constants.BYTES)
        location = "OwnerDir/" + str(current_chunk)
        done_reading = False
        while not done_reading:
            bfr1=None
            with open(f'{location}{extension}.chk', 'ab') as chunk:
                while True:
                    bfr = file.read(self.read_buffer_size)
                    if bfr1==None:
                        bfr1=bfr
                    else:
                        bfr1+=bfr
                    if not bfr:
                        done_reading = True
                        self.file_block_list[current_chunk] = bfr1
                        print(str(current_chunk) + " : ", len(self.file_block_list[current_chunk]))
                        break

                    chunk.write(bfr)
                    current_chunk_size += len(bfr)

                    if current_chunk_size + self.read_buffer_size > self.FILE_MAX_SIZE:
                        self.file_block_list[current_chunk] = bfr1
                        print(str(current_chunk) + " : ", len(self.file_block_list[current_chunk]))
                        current_chunk += 1
                        location = "OwnerDir/" + str(current_chunk)
                        current_chunk_size = 0
                        break

    # Divides the file into various chunks
    def __divideFileIntoChunks(self):
        try:
            sepDir = Constants.OWNER_DIR
            sepDir = os.path.join("D:\Work\ComputerNetwork\P2P\FileOwner/" + sepDir)
            if not path.exists(sepDir):
                os.mkdir(sepDir)

            p = Path.cwd()
            file_to_split = None
            for f in p.iterdir():
                if f.is_file() and f.name == 'test.pdf':
                    file_to_split = f
                    break

            if file_to_split:
                with open(file_to_split, 'rb') as file:
                    self._chunk_file(file, file_to_split.suffix)

        except:
            print("Exception in divide file into chunks")
            exit(1)


    # def __testConfig(self):



if __name__ == "__main__":
    n=len(sys.argv)
    # print(n)
    owner_port = 0
    file_name="test.pdf"
    if n==2:
        owner_port=sys.argv[1]
        print("")
        print("Owner Port: " + owner_port + "   File name: " + file_name)
        f1 = FileOwner(owner_port, file_name)
        f1.initiateOwner()
        # f1.test()
    elif(n==1):
        print("Mention Port number")
    else:
        print("Only one argument is needed, i.e., Port Number")