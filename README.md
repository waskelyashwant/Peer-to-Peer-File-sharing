# Peer-to-Peer-File-sharing
Peer to peer file sharing network implemented in python.

The file owner has a file, and it breaks the file into chunks of 100KB, each stored as a separate file. Note that the last chunk can be smaller than 100KB. The minimum number of chunks that the file can be split into is 5. The file owner listens on a TCP port. It should be designed as a server that can run multiple threads to serve multiple clients simultaneously.

Each peer should be able to connect to the file owner to download some chunks. It then should have two threads of control, one acting as a server that uploads the local chunks to another peer (referred to as upload neighbor), and the other acting as a client that downloads chunks from a third peer (referred to as download neighbor).
So each peer has two neighbors, one of which will get the chunks from this peer and another one will send chunks to this peer.

Some features that are implemented as part of the project involves:

No always-on server
Arbitrary end systems can directly communicate
Peers request service from other peers, provide service in return to other peers
auto scalability – new peers bring new service capacity, as well as new service demands
Peers connect intermittently and can change its IP addresses, supporting complex management.


Commands to run the following files:-
In one system or you can open a command prompt
cd FileOwner
python FileOwner.py 5000 

New command prompt
cd Peer1
python peer.py 5000 5001 5002

New command prompt
cd Peer2
python peer.py 5000 5002 5003

New command prompt
cd Peer3
python peer.py 5000 5003 5004

New command prompt
cd Peer4
python peer.py 5000 5003 5001

Execution
Start the file owner process, giving a listening port.
Start the five peer processes as: file owner, peer itself, download neighbor(another peer’s port)
Each peer connects to the server’s listening port.
The latter creates a new thread to upload one or several file chunks to the peer, while its main thread goes back to listening for new peers.
After receiving chunk(s) from the file owner, the peer stores them as separate file(s) and creates a summary file, listing the IDs of the chunks it has.
The peer then proceeds with two new threads, with one thread listening to its upload neighbor to which it will upload file chunks, and the other thread connecting to its download neighbor.
The peer requests for the chunk ID list from the download neighbor, compares with its own to find the missing ones, and randomly requests a missing chunk from the neighbor. In the meantime, it sends its own chunk ID list to its upload neighbor, and upon request uploads chunks to the neighbor.
After a peer has all file chunks, it combines them for a single file.
A peer MUST output its activity to its console whenever it receives a chunk, sends a chunk, receives a chunk ID list, sends out a chunk ID list, requests for chunks, or receives such a request.
