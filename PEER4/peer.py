import time
import logging
import os.path
from os import path
import sys
import socket
from sys import argv
from pathlib import Path
import threading
from _thread import *

event = threading.Event()


class Constants:
    LIST = "LIST"
    REQUEST = "REQUEST"
    ASK = "ASK"
    DATA = "DATA"
    CLOSE = "CLOSE"
    PEER = "PEER"
    DIR = "Dir/"
    BRACE_OPEN = "["
    BRACE_CLOSE = "] get connected from "
    SESSION_ENDED = "]: Session ended."
    RECIEVED_CHUNK = "Received Chunk #"
    IS_LISTENING = "] Peer is listening command:"
    BRACKET_CLOSE = ")"
    RECEIVED_MESSAGE = "] Received message ("
    RECIEVED_BLOCK = "Received Block #"
    FROM_OWNER = " from owner"
    CONFIG = "Config 5 "
    SPACE = " "
    DIR_1 = "Dir"
    CONGO = "CONGO !! ["
    DOWNLOAD_COMPLETION = "] has completed downloading the file!!"
    SUMMARY_FILE = "Dir/summary.txt"
    PEER_LISTENING = "Peer is listening at Port "
    BOOTSTRAP_FINAL = "] Asking for upload/download neighbor:"
    ESTABLISHING_UPLOAD = "Establishing upload..."
    ESTABLISHING_DOWNLOAD = "Establishing download..."
    ESTABLISHED_CONNECTION = "Connection established"
    LOCALHOST = "localhost"
    RECIEVED_BLOCKS = "Received blocks(download neighbor) from peer(port): "
    COMPLETED_PULLING = "] completed pulling from neighbor..."
    INITIATED_PUSHING = "Initiated pushing block list..."
    NAME = "NAME"
    COMPLETED_PUSHING = "] completed pushing!! sleep 1sec."
    REQUEST_PEER = "] REQUEST PEER"
    CHUNK = " Chunk #"
    RECEIVED_CHUNK = "Received Chunk #"
    FROM_PEER = " from Peer "
    NOT_HAVE_CHUNK = " doesn't have Chunk #"
    CLOSE_PEER = "] PEER"
    OUT_PUT_FILE = "Output file is "
    UPLOAD_NEIGHBOUR = "] 's Upload Neighbor "
    DOWNLOAD_NEIGHBOUR = "] 's download Neighbor "
    COLON = ":"
    REGISTER = "REGISTER"
    DOWNLOAD_NEIGHBOR_ID = "Current Download neighbor(ID) Peer: "
    UPLOAD_NEIGHBOR_ID = "Current Upload neighbor(ID) Peer: "

class ClientSocket:
    _peer_id = 0
    Socket = socket.socket()
    con = None
    addr = None

    peerName = 0

    _current_block = {}

    def __init__(self, peer_id, list_block_file):
        self._peer_id = peer_id
        self.peerName = str(peer_id)
        self._current_block = list_block_file

    def __saveChunkFile(self, x, chunk):
        location = "PEER5Dir/" + str(x)
        extension = ".pdf"
        try:
            with open(f'{location}{extension}.chk', 'ab') as chunk_data:
                chunk_data.write(chunk)
        except:
            print("Exception in __saveChunkFile in ClientSocket class")
            exit()

    def intialiseSocket(self, con, addr):
        self.con = con
        self.addr = addr
        print(Constants.BRACE_OPEN + self.peerName + Constants.BRACE_CLOSE + str(addr[1]))

    def run(self):
        while True:
            # try:
                msg = self.__printCommands()
                id = -1
                if msg == Constants.LIST:
                    self.performListOperation()
                elif msg == Constants.REQUEST:
                    self.requestChunk(id)
                elif msg == Constants.ASK:
                    self.askChunk(id)
                elif msg == Constants.DATA:
                    self.saveRecievedData(id)
                elif msg == Constants.CLOSE:
                    print("Connection closed, Inside run() in clientSocket class")
                    self.con.close()
                    return
            # except:
            #     print("Exception in run() of clientSocket class")
            #     print(Constants.BRACE_OPEN + self.peerName + Constants.SESSION_ENDED)
            #     return

    def saveRecievedData(self, id):
        self.con.send(("id bhejio me save karta hu").encode())
        id = int(self.con.recv(1024).decode())
        self.con.send(("chunk bhej ab").encode())
        chunk = self.con.recv(102400)
        if id not in self._current_block.keys():
            self._current_block[id] = chunk
            print(Constants.RECIEVED_CHUNK + str(id))
            self.__saveChunkFile(id, chunk)
            print("chunk file saved")

    def askChunk(self, id):
        # print("Aa gya askChunk me")
        self.con.send(("Bata rha hu ruk").encode())
        key = self.con.recv(1024).decode()
        if key in self._current_block.keys():
            self.con.send(str(1).encode())
        else:
            self.con.send(str(0).encode())

    def requestChunk(self, id):
        self.con.send(("Bhej rha hu ruk").encode())
        id = self.con.recv(1024).decode()
        # send that chunk
        self.con.send(id.encode())
        self.con.recv(1024)
        self.con.send(self._current_block[id])

    def performListOperation(self):
        q = []
        for key in self._current_block.keys():
            q.append(key)
        q = str(q)
        q = q.encode()
        self.con.send(q)

    def __printCommands(self):
        # print("Inside printCommands")
        print(Constants.BRACE_OPEN + self.peerName + Constants.IS_LISTENING)
        msgObj = self.con.recv(1024).decode()
        msg = str(msgObj)
        print(Constants.BRACE_OPEN + self.peerName + Constants.RECEIVED_MESSAGE
              + msg + Constants.BRACKET_CLOSE)

        return msg


class Peer:
    server_port = 0
    peer_port = 0
    download_port = 0
    peer_id = -1
    __port_DL = -1
    __peer_DL = -1
    __port_UL = -1
    __peer_UL = -1
    peer_socket = socket.socket()
    skt_up = socket.socket()
    skt_dwn = socket.socket()
    peer_skt = socket.socket()

    peer_self_port = -2
    peer_name = ""
    MAX_PEER = 4

    merge_file_name = ""

    list_block_file = {}
    block_indx = []
    peer_list = {}

    # Creates a new peer.

    def __init__(self, server_port, peer_port, download_port):
        self.server_port = int(server_port)
        self.peer_port = int(peer_port)
        self.download_port = int(download_port)

    def __getInitialChunksFromServer(self):
        last = int(1.0 * len(self.block_indx) / self.MAX_PEER * ((int(self.peer_id) % self.MAX_PEER) + 1))
        begin = int(1.0 * len(self.block_indx) / self.MAX_PEER * (int(self.peer_id) % self.MAX_PEER))
        print(last, " ", begin)

        for i in range(begin, last):
            self.TransmitMessageToOwner(Constants.REQUEST)
            a = self.peer_socket.recv(1024).decode()
            self.TransmitMessageToOwner(str(self.block_indx[i]))
            f = int(self.peer_socket.recv(1024).decode())
            self.peer_socket.send(bytes("abc", 'utf-8'))
            chunk = self.peer_socket.recv(102400)
            print(Constants.RECIEVED_BLOCK + str(self.block_indx[i]) + Constants.FROM_OWNER)
            self.__saveChunkFile(f, chunk)

        self.toListBlockFile(last, begin)

    def toListBlockFile(self, last, begin):
        for i in range(begin, last):
            file = open("D:\Work\ComputerNetwork\P2P\Peer4\PEER5Dir/" + str(i) + ".pdf.chk", 'rb')
            bfr = file.read(102400)
            self.list_block_file[i] = bfr
            file.close()

    def __getChunkList(self):
        self.TransmitMessageToOwner(Constants.LIST)
        self.block_indx = self.peer_socket.recv(1024).decode('utf-8')
        self.block_indx = eval(self.block_indx)

    def __getBootStrap(self):
        message_to_owner = Constants.CONFIG + str(self.peer_port) + Constants.SPACE + str(self.download_port)
        self.TransmitMessageToOwner(message_to_owner)
        self.peer_socket.recv(1024).decode()
        self.TransmitMessageToOwner(Constants.REGISTER)
        self.peer_id = self.peer_socket.recv(1024).decode()
        self.peer_socket.send(("124").encode())
        self.peer_self_port = self.peer_socket.recv(1024).decode()
        self.peer_name = Constants.PEER + self.peer_id
        print(self.peer_id)
        sepDir = self.peer_name + Constants.DIR_1
        sepDir = os.path.join("D:\Work\ComputerNetwork\P2P/Peer4/" + sepDir)
        if not path.exists(sepDir):
            os.mkdir(sepDir)

        self.__getChunkList()
        self.__getInitialChunksFromServer()

    def getUploadDownloadNeighbor(self):
        while True:
            self.TransmitMessageToOwner(Constants.PEER)
            self.peer_socket.recv(1024)
            self.TransmitMessageToOwner(str(self.peer_id))
            self.peer_socket.recv(1024)
            self.TransmitMessageToOwner(str(self.peer_port))
            self.peer_socket.recv(1024)
            self.TransmitMessageToOwner(str(self.download_port))
            self.peer_list = eval(self.peer_socket.recv(4096).decode())
            self.TransmitMessageToOwner(str(230))

            print(Constants.BRACE_OPEN + self.peer_name + Constants.BOOTSTRAP_FINAL)
            self.__peer_DL = int(self.peer_socket.recv(1024).decode())
            self.TransmitMessageToOwner(str(145))
            self.__peer_UL = int(self.peer_socket.recv(1024).decode())
            print(self.__peer_DL)
            print(self.__peer_UL)

            if self.__peer_DL in self.peer_list.keys():
                self.__port_DL = self.peer_list[self.__peer_DL]
            else:
                self.__port_DL = 0
            if self.__peer_UL in self.peer_list.keys():
                self.__port_UL = self.peer_list[self.__peer_UL]
            else:
                self.__port_UL = 0

            self.__printNeighborStatus()
            event.wait(1)

            if self.__port_DL > 0 and self.__port_UL > 0:
                break

    def __printNeighborStatus(self):
        if self.__port_UL == 0:
            print("Upload Neighbor is still not up")
        else:
            print(Constants.UPLOAD_NEIGHBOR_ID + str(self.__peer_UL) + " is up and running!!")

        if self.__peer_DL == 0:
            print("Download Neighbor is still not up")
        else:
            print(Constants.DOWNLOAD_NEIGHBOR_ID + str(self.__peer_DL) + " is up and running!!")

    def TransmitMessageToOwner(self, msg):
        self.peer_socket.send(msg.encode())

    def __saveChunkFile(self, file_i, chunk_data):
        location = "PEER5Dir/" + str(file_i)
        extension = ".pdf"
        try:
            with open(f'{location}{extension}.chk', 'ab') as chunk:
                chunk.write(chunk_data)
        except:
            print("Exception in __saveChunkFile in OwnerProcess class")
            exit()

    def __performAfterCheckChunk(self):
        file = os.path.join("D:\Work\ComputerNetwork\P2P/Peer4/" + self.merge_file_name)
        if not path.exists(file):
            os.mkdir(file)

    def checkChunk(self):
        for key in self.block_indx:
            if key not in self.list_block_file.keys():
                return False

        try:
            self.__performAfterCheckChunk()
            print(Constants.CONGO + self.peer_name + Constants.DOWNLOAD_COMPLETION)
        except:
            print("Exception in checkChunk function")

        return True

    def __initiatePeer(self, peer, con, addr):
        peer.intialiseSocket(con, addr)
        start_new_thread(peer.run, ())

    def __createBriefForEntireProcess(self, ch):
        return

    def __setConnectionToPeer(self):
        host = "localhost"
        self.peer_skt.bind((host, self.peer_self_port))
        self.peer_skt.listen(5)
        while True:
            peer = ClientSocket(self.peer_id, self.list_block_file)
            #try:
            print(Constants.PEER_LISTENING + str(self.peer_port))
            con, addr = self.peer_skt.accept()
            self.__initiatePeer(peer, con, addr)
            # except:
            #     print("Exception in __setConnectionToPeer in Peer class")


    def executeRun(self):
        print("==================")
        event.wait(10)
        print(Constants.ESTABLISHING_UPLOAD)
        print(Constants.ESTABLISHING_DOWNLOAD)
        print(self.__port_UL)
        print(self.__port_DL)
        host = "localhost"
        self.skt_up.connect((host, self.__port_UL))

        self.skt_dwn.connect((host, self.__port_DL))

        print(Constants.ESTABLISHED_CONNECTION)

        while self.checkChunk() == False:
            self.__processChunk()
            event.wait(1)

    def __processChunk(self):
        print(Constants.RECIEVED_BLOCKS + str(self.__port_DL))
        self.skt_dwn.send((Constants.LIST).encode())
        chunks = []
        chunks = self.skt_dwn.recv(1024).decode()
        chunks = eval(chunks)
        for i in range(0, len(chunks)):
            q = chunks[i]
            if q in self.list_block_file.keys():
                print(str(q) + ":=" + str(q) + " ")
            else:
                print(str(q) + ":= Downloaded ")

        print()
        self.__sendBlocksToPeers()
        self.__pushFileBlock()

    def __pushFileBlock(self):
        print(Constants.BRACE_OPEN + self.peer_name + Constants.COMPLETED_PULLING)
        print(Constants.INITIATED_PUSHING + " (upload neighbor) to Peer(port): " + str(self.__port_UL))

        for block_index in self.block_indx:
            q = block_index
            if q not in self.list_block_file.keys():
                continue

            print(str(q) + Constants.SPACE)
            self.skt_up.send((Constants.DATA).encode())
            print("aaaaaaaaaaaaaa")
            self.skt_up.recv(1024)
            self.skt_up.send((str(q)).encode())
            print("bbbbbbbbbbbbbb")
            self.skt_up.recv(1024)
            self.skt_up.send(self.list_block_file[q])

        print()
        print(Constants.BRACE_OPEN + self.peer_name + Constants.COMPLETED_PUSHING)

    def __sendBlocksToPeers(self):
        for i in range(0, len(self.block_indx)):
            q = self.block_indx[i]
            if q in self.list_block_file.keys():
                continue

            print(Constants.BRACE_OPEN + self.peer_name + Constants.REQUEST_PEER +
                  str(self.__peer_DL) + Constants.CHUNK + str(q))

            self.skt_dwn.send((Constants.ASK).encode())
            self.skt_dwn.recv(1024).decode()
            # print(msg_bata)
            self.skt_dwn.send((str(q)).encode())
            a = int(self.skt_dwn.recv(1024).decode())
            if a == 1:
                self.skt_dwn.send((Constants.REQUEST).encode())
                self.skt_dwn.recv(1024)
                self.skt_dwn.send((str(q)).encode())
                x = int(self.skt_dwn.recv(1024).decode())
                self.skt_dwn.send(("Jaldi bhej").encode())
                chunk = self.skt_dwn.recv(102400)
                self.list_block_file[x] = chunk
                print(Constants.RECEIVED_CHUNK + self.block_indx[i] +
                      Constants.FROM_PEER + str(self.__peer_DL))
            else:
                print(Constants.BRACE_OPEN + self.peer_name + Constants.CLOSE_PEER +
                      str(self.__peer_DL) + Constants.NOT_HAVE_CHUNK + str(q))

    def initialize(self):
        # try:
            host = "localhost"
            self.peer_socket.connect((host, self.server_port))
            print("connected")
            self.__getBootStrap()
            self.__createBriefForEntireProcess(0)
            self.TransmitMessageToOwner(Constants.NAME)
            merge_file_name = self.peer_socket.recv(1024).decode()

            print(Constants.OUT_PUT_FILE + merge_file_name)

            self.getUploadDownloadNeighbor()
            print(Constants.BRACE_OPEN + self.peer_name + Constants.UPLOAD_NEIGHBOUR + str(self.__peer_UL)
                  + Constants.COLON + str(self.__port_UL))
            print(Constants.BRACE_OPEN + self.peer_name + Constants.DOWNLOAD_NEIGHBOUR + str(self.__peer_DL)
                  + Constants.COLON + str(self.__port_DL))

            print(self.peer_self_port)
            start_new_thread(self.executeRun, ())
            self.peer_self_port = int(self.peer_self_port)

            while self.peer_self_port < 0:
                event.wait(0.5)

            self.__setConnectionToPeer()

        # except:
        #     print("Exception in initialize function")


if __name__ == "__main__":
    n = len(sys.argv)
    # print(n)
    server_port = 0
    peer_port = 0
    download_port = 0
    if n == 4:
        server_port = sys.argv[1]
        peer_port = sys.argv[2]
        download_port = sys.argv[3]
        if peer_port == download_port:
            print("FileOwner only distributes the chunks, so peer port and download port should be " +
                  "different as peer can only download from other peers, not from file owner..")
        else:
            p1 = Peer(server_port, peer_port, download_port)
            p1.initialize()

    else:
        print("Argument length should be 3")
    # try:
    #     if n==4:
    #         server_port = sys.argv[1]
    #         peer_port = sys.argv[2]
    #         download_port = sys.argv[3]
    #         if peer_port == download_port:
    #             print("FileOwner only distributes the chunks, so peer port and download port should be " +
    #                         "different as peer can only download from other peers, not from file owner..")
    #         else:
    #             p1 = Peer(server_port, peer_port, download_port)
    #             p1.initialize()
    #
    #     else:
    #         print("Argument length should be 3")
    # except:
    #     print("Give proper input")