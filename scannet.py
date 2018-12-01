import MySQLdb
from xbee import *
import time

def scanNet():
     Xbee = xbeeController()
     Xbee.clear()
     Xbee.xbeeDataQuery('F','N')

     time.sleep(4)

     for i in range(0,4):                        # range is too small here for a large network
         data = Xbee.getPacket()
         l = len(data)
         if l > 0:
           address = printAddress(data)
           nodeid =  printNodeID(data)
           print address, nodeid
           updateMySQL(address, nodeid)

         time.sleep(2)

     time.sleep(4)
     Xbee.close()

def printAddress(data):
    addr = ""
    for i in range(10, 17):
        a = str(hex(ord(data[i])))
        addr = addr + a[2:]
    return addr

def printNodeID(data):
    nodeid = ""
    for i in range(18,38):
        d = data[i]
        if d.isalpha() or d.isdigit():
           nodeid = nodeid + d
        else:
           nodeid = nodeid + ' '
    return nodeid


def updateMySQL(address, nodeid):
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




#         if len(data) > 4:
#            try:
#               print "from address: ", hex(ord(data[10])), hex(ord(data[11])), hex(ord(data[12])), 
#       hex(ord(data[13])), hex(ord(data[14])), hex(ord(data[15])), hex(ord(data[16])), hex(ord(data[17])),
#               print "  | Node ID: ",
#               ni = ""
#               for i in range(18,38):
               # if this equals 00 hex, it is end of string, otherwise it's up to 20 bytes
               #print hex(ord(data[i])),
#                  d = data[i]
#                  if chr(d) == 0:
#                     for x in range(i, 38):
#                         ni = ni + ' '
#                     break
#                  else:
#                     ni= ni + d
#               print ni
#            except:
#               pass

#     time.sleep(4)
#     Xbee.close()


while(1):
    scanNet()
    time.sleep(5)


#           01234567890123456789
#somedata = "This is a message 4U"
#data = list(somedata)

#dest = [ 0x00, 0x13, 0xA2, 0x00, 0x40, 0xE8, 0x22, 0x8B ]
#Xbee.xbeeTransmitDataFrame(dest, data)

#Xbee.close()
