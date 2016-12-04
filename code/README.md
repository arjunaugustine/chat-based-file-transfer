# chat-based-file-transfer

## a. Environment settings

Clone the library from git as follows:-
```
git clone git@github.com:arjunaugustine/chat-based-file-transfer.git
```
Navigate inside cde directory. This is our working directory, where all the run-time code is stored.

## b. Understanding how the code works:

Following is a flow chart that depicts working of a server.
![alt tag](../bin/Algorithm%20for%20Server-to-Client.png)

Following is a flow chart that depicts file transfer between two peers.
![alt tag](../bin/Peer%20to%20peer%20File%20Transfer%20Algorithm.png)

## c. How to run the code

### Start

On the device we wish to run the server on, open a terminal windows and obtain the IP address.
```
ifconfig
```
Navigate inside the code directory and run server.py as admin(sudo because we need to open sockets).
```
sudo ./server.py
```
Next, on the device we need to start the client, run the client can be run with command line arguments. The options made available to us are:-

| Argument       | Description                                     |
|:---------------|:------------------------------------------------|
| -h --help      | Print help options                              |
| -s --share     | 0/1 to clear/set global file share              |
| -p --parallel  | Integer argument to define parallel connections |
| --ip           | Server IP                                       |
| --port         | Server Port (50000-50009 by default)            |
| -w --window    | Window Size for Go-Back-N (16/32 recommended)   |

Example to start client:-
```
sudo ./client.py -h
```
Displays the options aavailable to start client.
```
sudo ./client.py -w 32 -p 100
```
Starts client with Go-Back-N window size 32 and 100 parallel connection limit

### Chat Options

Chat commands made available to the user:-

| Command                    | Description                                                      |
|:---------------------------|:-----------------------------------------------------------------|
| `@username|chat`           | Sends a message 'chat' to 'username'                             |
| `@all|chat`                | Sends a message 'chat' to all users in chatroom                  |
| `@server|chat`             | Sends a message 'chat' to server (admin)                         |
| `@all|whohas|file`         | Sends broadcast message to see who has file with filename 'file' |
| `@user|getfile|file`       | Sends a message to 'user' to start UDP peer-to-peer file transfer|
| `@server|get_rooms`        | Get a list of chat rooms avaialable with server                  |
| `@server|get_peers`        | Get a list of connected peers in chatroom                        |
| `exit`                     | Clean exit chat room                                             |
| `@me|setwindowsize|n`      | Sets Go-Back-N window size to 'n'                                |
| `@me|setshare|file`        | Enable sharing of filename: 'file'                               |
| `@me|clrshare|file`        | Disable sharing of filename: 'file'                              |
| `@me|setglobalshare|file`  | Enable sharing all files                                         |
| `@me|clrglobalshare|file`  | Disable sharing any files                                        |


Commands made available to the server:-

| Command              | Description                                                      |
|:---------------------|:-----------------------------------------------------------------|
| `@username|chat`     | Sends a message 'chat' to 'username'                             |
| `@all|chat`          | Sends a message 'chat' to all users in all chatroom              |
| `@server|chat`       | Sends a message 'chat' to self                                   |
| `exit`               | Kill all client connections and exit application gracefully      |

## d. How to interpret the results

Chat         : Check for chat messages in terminal (Format: #sender|message from user)
File Transfer: Check for file existance inside [folder](code/folder) or Check for terminal output
Go-Back-N    : Results included in [README.md](README.md)


## e. Any sample input and output files

Sample screen shots included inside the project report.
