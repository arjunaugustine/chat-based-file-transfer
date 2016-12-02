#! /usr/bin/python

from library import *
from socket import *
from chatRoom import *
import logging
import threading
MAX_SIZE = 16
logging.basicConfig(filename='server.log', level=logging.DEBUG)


class UDPServer(object):
  """
  """

  def __init__(self, parent, msg):
    self.parent = parent
    self.udp_client_name = msg[0][1:]
    self.socket = socket(AF_INET, SOCK_DGRAM)
    self.cip, self.cport = msg[3], int(msg[4])
    self.sip, self.sport = self.parent.ip, bind_to_random(self.socket)
    self.filename = msg[2]
    self.suspended = False
    self.lock = threading.Lock()
    self.readyToSend = 1
    self.send_msg = ''
    self.buffered_msgs = []

  def udp_send(self, msg):
    # print self.cip, self.cport
    # try:
    #   msg = msg
    # except TypeError:
    #   try:
    #     msg = msg.decode('hex')
    #   except TypeError:
    #     try:
    #       msg = msg.decode('utf-8')
    #     except UnicodeDecodeError:
    #       try:
    #         msg = msg.decode('latin-1')
    #       except TypeError:
    #         self.suspended = True
    #         return

    self.socket.sendto(msg, (self.cip, self.cport))

  def udp_recv(self, size=2048):
    msg, saddr = self.socket.recvfrom(size)
    assert saddr[0] == self.cip
    msg = str(msg.decode())
    if msg[-1:] == '\n':
      msg = msg[:-1]
    if msg != 'ACK':
      print msg
    return msg

  def execute(self):
    """
    Comes here when a file is requested.
    Msg from UDPServer is in format: #FROM|getfile|filename|udpserver_IP|udpserver_port
    """
    self.connect()
    self.transfer()

  def connect(self):
    """
    Connect to server ip and port from a random client port cport = random.randrange(something)
    Save c-port in self. Bind to cport and connect to server.
    """
    if self.suspended:
      return
    if not self.parent.check_file(self.filename):
      self.udp_send('ERROR| File Not Found')
      self.suspended = True

    self.udp_send('OK| Sending file on port ' + str(self.cport) + ' from |' + str(self.sip) + '|' + str(self.sport))

  def send_file(self):
    buff = 2048
    self.window = MAX_SIZE
    self.seqNo = 0
    f = open('folder/' + self.filename)
    self.send_msg = f.read(buff-10) # 4 bytes for seq no
#   print "msg***   %s" %self.send_msg
    prev_msg = self.send_msg
    while self.send_msg != ''and not self.suspended:
      self.lock.acquire()
      if self.window>0:
          self.send_msg = str(self.seqNo)+'|*)'+self.send_msg
          print "send %s" %self.seqNo
          #print "msg***   %s" %self.send_msg
          self.buffered_msgs.append([self.seqNo,self.send_msg]) #store the msg in a dict for reTx
          self.udp_send(self.send_msg)
          prev_msg = self.send_msg
          self.send_msg = f.read(buff-10) # 4 bytes for seq no
          self.seqNo +=1  
          self.seqNo %=MAX_SIZE
          #print "send %s" %self.window
          self.window -=1
          #print "send release %s" %self.windo
      self.lock.release()
    print "send EOF %d %s" %(self.suspended,prev_msg)
    self.udp_send('EOF')
    self.buffered_msgs.append([self.seqNo,'EOF'])
    f.close()
    
  def get_index(self,ack_no):
      count = 0
      if self.buffered_msgs[0][0]>ack_no: #dup ack
        return -1
      for i in self.buffered_msgs:
        if i[0]== ack_no:
          self.buffered_msgs.remove(i)
          self.window += 1
          return count
        else:
          self.buffered_msgs.remove(i)
          self.window += 1
        count +=1
      return -1  
    
  def rec_ack(self,tries=10):
    while not self.suspended:
      #print "msg wait rec %s"
      msg = self.udp_recv()
      msg = msg.split('|')
      #print "msg received seq no %s" %msg[0]
      while len(msg[1]) > 3 and msg[1][:4] == 'NACK' and tries > 1:
        tries -= 1
        self.udp_send(self.send_msg)
        msg = self.udp_recv()
        msg = msg.split('|')
      if msg[1][:3] != 'ACK': 
        print "Non ACK non NACK"
        self.suspended = True
      
      #print "bef rec %s" %self.window
      if msg[1][:3]=='ACK':
        self.lock.acquire()
        
        print "rec %s" %self.window
        index = self.get_index(int(msg[0]))
        if index == -1:#dup msg
          self.suspended = True
          print "duplicate ack %s" %msg[0]
          self.udp_send("STA")
          while self.buffered_msgs:
             self.udp_send(self.buffered_msgs[0][1])
             print "duplicate send %s" %self.buffered_msgs[0][0]
             msg = self.udp_recv()
             msg = msg.split('|')
             print "duplicate rec ack %s" %msg[0]
             if msg[1][:3]=='ACK' and msg[0] == str(self.buffered_msgs[0][0]):
               self.buffered_msgs.pop(0)
               self.window+=1
             elif msg[:3]=='EOF':
                break;
        self.udp_send("END")
        self.suspended = False
        self.lock.release()
        print "rec release %s" %self.window
  
    
  def transfer(self):
    """
    Transfer the filename in our folder/filename to the server.
    """
    # TODO::take buffer size from an ip
    if self.suspended:
      return
    empty_tuple = ()
    thread.start_new_thread(self.send_file, empty_tuple)
    print "created a thread"
    thread.start_new_thread(self.rec_ack, empty_tuple)
      
    ##old code
    #buff = 2048
    #f = open('folder/' + self.filename)
    #msg = f.read(buff)
    #while msg != '' and not self.suspended:
     # self.send_pkt(msg)
      #msg = f.read(buff)
    #self.send_pkt('EOF')
    #f.close()
    ##END of old code
    # print "All close"



  def send_pkt(self, send_msg, tries=10):
    """
    Send msg to socket. Receive an ACK from other side that has format #FROM|(N)ACK
    retry send if NACK, else return.
    """
    self.udp_send(send_msg)
    msg = self.udp_recv()
    while len(msg) > 3 and msg[:4] == 'NACK' and tries > 1:
      tries -= 1
      self.udp_send(send_msg)
      msg = self.udp_recv()
    if msg[:3] != 'ACK':
      print "Non ACK non NACK"
      self.suspended = True
