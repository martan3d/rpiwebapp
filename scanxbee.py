# background task runs as root, if message comes in, queue it for the background (web) to pick it up
# if transmit queue has an entry, send it.
# ignore broadcast packets from Protothrottle

from xbee import *
import redis
import json
import base64
import MySQLdb


def getAddress(data):
    addr = ""
    for i in range(10, 18):
        a = "%02x" % data[i]
        addr = addr + a
    return addr

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

def clearDatabase():
    db = MySQLdb.connect(host="localhost", passwd="raspberry", db="webapp")
    cr = db.cursor()
    sql = "DELETE from nodes;"
    cr.execute(sql)
    db.commit()

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
    print sql

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

#
# Main scan
#

Xbee = xbeeController()
Xbee.clear()

r = redis.Redis(host='127.0.0.1', port='6379')

while(1):
    data = Xbee.getPacket()
    if data != None:
       data = removeESC(data)

       msgtype = data[3]
       msb     = data[1]
       lsb     = data[2]

       if msgtype == 136:
          print "node discovery response"
          if lsb > 5:                     # is this from external nodes?
            nodeid  = getNodeID(data)
            address = getAddress(data)
            insertNode(nodeid, address)

       z = []
       for d in data:
           z.append(d)
           p = "%x" % d
           print p,
       print

       #TODO: decode and submit all data to database here if it is a response from ND
       #      otherwise, extract the data response from a node and queue it

#       z = []
#       for d in data:
#           z.append(ord(d))

       # TDO: Ignore protothrottle broadcast here, don't push
#TODO       r.rpush(['queue:xbee'], base64.b64encode(json.dumps(z)) )

    # check transmit queue here, if not empty, build the message and transmit it
    # this queue is populated from the webform, it issues a ascii command, like 'SCAN' and this builds and transmits it
    # data coming back from any of the below commands is captured above and pushed onto the RX queue where the front end can get it

    data = r.rpop(['queue:xbeetx'])
    if data != None:
       print "data from background to transmit"
       print data
       if data == 'SCAN':
          clearDatabase()
          Xbee.xbeeDataQuery('N','D')

