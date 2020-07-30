# background task runs as root, if message comes in, queue it for the background (web) to pick it up
#
# if transmit queue has an entry, send it.
#
# log but otherwise ignore broadcast packets, acks etc
#

from xbee import *
import redis
import json
import base64
import MySQLdb

# message codes from front end requests

READNOTCHES = 36
RETURNTYPE  = 37
SETCV       = 16

# build bytes address from string

def buildAddress(address):
    dest    = [0,0,0,0,0,0,0,0]
    dest[0] = int(address[:2], 16)           # very brute force way to pull this out!
    dest[1] = int(address[2:4], 16)
    dest[2] = int(address[4:6], 16)
    dest[3] = int(address[6:8], 16)
    dest[4] = int(address[8:10], 16)
    dest[5] = int(address[10:12], 16)
    dest[6] = int(address[12:14], 16)
    dest[7] = int(address[14:16], 16)
    return dest

# break the 64 bit mac address out of the Network Discovery 'ND' response message

def getAddress(data):
    addr = ""
    for i in range(10, 18):
        a = "%02x" % data[i]
        addr = addr + a
    return addr

# get the ASCII name NodeID from the 'ND' response message

def getNodeID(data):
    nodeid = ""
    for i in range(19,37):
        if data[i] == 0:
           return nodeid
        d = chr(data[i])
        if d.isalpha() or d.isdigit():
           nodeid = nodeid + d
        else:
           nodeid = nodeid + ' '
    return nodeid

# when the scan button is clicked, clear out the Mysql Database of all nodes

def clearDatabase():
    db = MySQLdb.connect(host="localhost", passwd="raspberry", db="webapp")
    cr = db.cursor()
    sql = "DELETE from nodes;"
    cr.execute(sql)
    db.commit()

# as we find the nodes via valid responses to our 'ND' response, put them into the database

def insertNode(nodeid, address):
    db = MySQLdb.connect(host="localhost", passwd="raspberry", db="webapp")
    cr = db.cursor()
    sql = "SELECT * from nodes where address='%s';" % address
    cr.execute(sql)
    result = cr.fetchall()
    if result:
       sql = "UPDATE nodes SET name='%s' where address='%s';" % (nodeid, address)
    else:
       sql = "INSERT INTO nodes (name, address, type, status) VALUES ('%s','%s','%s','%s') " % (nodeid, address, 'node', 'ok')
    cr.execute(sql)
    db.commit()

# API Mode 2 says we have to 'escape' four characters if our message has then, the removes them from an incoming xbee message

def removeESC(data):
    rd = []
    i = 0
    for d in data:
        try:
           if ord(data[i]) != 125:  #ESC char
              rd.append(ord(data[i]))
              i = i + 1
           else:
              i = i + 1
              rd.append(ord(data[i]) ^ 0x20)
              i = i + 1
        except:
           return rd

    return rd

def debugprint(datalist):
    for d in datalist:
        p = "%x" % d
        print p,
    print


#
# Main scan - this is the never ending loop that should be run as a background task as root
#             only root can access the USB port that the Xbee is on
#

Xbee = xbeeController()
Xbee.clear()

r = redis.Redis(host='127.0.0.1', port='6379')

while(1):
    data = Xbee.getPacket()
    if data != None:
       msgtype = data[3]
       msb     = data[1]
       lsb     = data[2]

       if msgtype == 129:
          #if data[7] == 2:
          #   print "Protothrottle Broadcast"
          if data[7] == 0:
             print "Return Message"
             r.rpush(['queue:xbee'], base64.b64encode(json.dumps(data)) )

             debugprint(data)

       if msgtype == 136:
          print "node discovery response"
          if lsb > 5:                     # is this from external nodes?
            nodeid  = getNodeID(data)     # yep, grab some stuff
            address = getAddress(data)    # Node ID and network address
            insertNode(nodeid, address)   # Stick it into the database
          else:
            print "internal ND response"  # otherwise it's from us, just toss it

          debugprint(data)

       if msgtype == 137:                 # Log ACKs from any outgoing messages
          print "ACK"
          debugprint(data)

       # print some message bytes as debug

#       for d in data:
#           p = "%x" % d
#           print p,
#       print

# check transmit queue here, if not empty, build the message and transmit it
# this queue is populated from the webform, it pushes (redis queue) an ascii command, like 'SCAN' and this builds and transmits it
# data coming back from any of the below commands is captured above and pushed onto the RX queue where the front end can get it

    data = r.rpop(['queue:xbeetx'])
    if data != None:
       message = json.loads(base64.b64decode(data))
       cmd = message[0]
       print cmd

       if cmd == 'SCAN':
          clearDatabase()
          Xbee.xbeeDataQuery('N','D')

       if cmd == 'READNODE':
          address = message[1]
          data    = message[2]
          txaddr  = buildAddress(address)
          data =  chr(RETURNTYPE) + data[1:]
          Xbee.xbeeTransmitDataFrame(txaddr, data)
          
       if cmd == 'READNOTCHES':
          address = message[1]
          data    = message[2]
          txaddr  = buildAddress(address)
          data =  chr(READNOTCHES) + data[1:]
          Xbee.xbeeTransmitDataFrame(txaddr, data)
       
       if cmd == 'SETCV':
          address = message[1]
          data    = message[2]
          txaddr  = buildAddress(address)
          data =  chr(SETCV) + data[1:]
          Xbee.xbeeTransmitDataFrame(txaddr, data)

       if cmd == "SETDCC":
          address = message[1]
          data    = message[2]
          txaddr  = buildAddress(address)
          Xbee.xbeeTransmitDataFrame(txaddr, data)

       if cmd == "REMOTECOMMAND":
          address = message[1]
          data    = message[2]
          txaddr  = buildAddress(address)
          Xbee.xbeeTransmitRemoteCommand(txaddr, 'N', 'I', data)    # set node id
          Xbee.xbeeTransmitRemoteCommand(txaddr, 'A', 'C', '')      # apply changes
          Xbee.xbeeTransmitRemoteCommand(txaddr, 'W', 'R', '')      # write to eeprom
