import MySQLdb as db
from xbee import *
import time


# run forever in background. Does a 'Find Neighbors' to discover all Xbee Digimesh Nodes on the Network

Xbee = xbeeController()
Xbee.clear()


while(1):
     Xbee.xbeeDataQuery('F','N')
     time.sleep(5)

     for i in range(0,4):                        # range is too small here for a large network
         data = Xbee.getPacket()
         try:
            print "from address: ", hex(ord(data[10])), hex(ord(data[11])), hex(ord(data[12])), hex(ord(data[13])), hex(ord(data[14])), hex(ord(data[15])), hex(ord(data[16])), hex(ord(data[17])),
            print "  | Node ID: ",
            ni = ""
            for i in range(18,38):
            # if this equals 00 hex, it is end of string, otherwise it's up to 20 bytes
            #print hex(ord(data[i])),
                d = data[i]
                if d == 0:
                   for x in range(i, 38):
                       ni = ni + ' '
                break
                else:
                   ni= ni + data[i]
            print ni
         except:
            pass

    time.sleep(4)

#           01234567890123456789
#somedata = "This is a message 4U"
#data = list(somedata)

#dest = [ 0x00, 0x13, 0xA2, 0x00, 0x40, 0xE8, 0x22, 0x8B ]
#Xbee.xbeeTransmitDataFrame(dest, data)

#Xbee.close()
