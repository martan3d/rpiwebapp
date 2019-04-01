# ESCaped Version of Xbee communications

import serial

class xbeeController:
    def __init__(self):
        usbPort = '/dev/ttyUSB0'
        self.sp = serial.Serial(usbPort, 38400, timeout=0.25)

    def close(self):
        self.sp.close()

    def clear(self):
        self.sp.reset_input_buffer()

    def xbeeReturnResult(self, datalength):
        return(self.sp.read(datalength))

    def getPacket(self):
        r = self.sp.read(1)
        if r == '':
           return None
        try:
           d = ord(r)
        except:
           return None

        if d != 0x7e:
          while(1):
             try:
                d = ord(self.sp.read(1))
             except:
                return None

             if d == None:
                return None

             if d == 0x7e:
                break

        l1 = self.sp.read(1)
        if l1 == '': return None

        lh = ord(l1)

        l2 = self.sp.read(1)
        if l2 == '': return None
        ll = ord(l2)

        l = lh << 8
        l = lh | ll

        try:
           data = self.sp.read(l+1)
        except:
           return None

        rdata = chr(d) + chr(lh) + chr(ll) + data
        r = []
        for d in rdata:
            r.append(ord(d))
        return r


    def xbeeDataQuery(self, cmdh, cmdl):
        frame = []
        c0 = ord(cmdl)
        c1 = ord(cmdh)
        frame.append(0x7e)	# header
	frame.append(0)	        # our data is always fixed size
	frame.append(4)         # this is all data except header, length and checksum
	frame.append(0x08)      # AT COMMAND - send Query to Xbee module
	frame.append(0x52)	# frame ID for ack- 0 = disable
	frame.append(c1)	# Command high character
	frame.append(c0)	# low character
	frame.append(0)	        # zero checksum location

	cks = 0;
	for i in range(3,7):	# compute checksum
	    cks = cks + frame[i]

	i = (255-cks) & 0x00ff
	frame[7] = i	        # and put it in the message

        for i in range(0,8):
            self.sp.write(chr(frame[i]))

#
# Command to Random Xbee out there
#

    def xbeeTransmitDataFrame(self, dest, data):
        txdata = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        i = 0              # data must be 20 bytes
        data = data[:20]   # truncate to 20 if needed
        for d in data:     # make sure it's in valid bytes for transmit
            try:
               txdata[i] = int(ord(d))
            except:
               txdata[i] = int(d)
            i = i + 1

        frame = []
        frame.append(0x7e)	# header
	frame.append(0)	        # our data is always fixed size, 20 bytes of payload
	frame.append(0x1f)      # this is all data except header, length and checksum
	frame.append(0x00)      # TRANSMIT REQUEST - send Query to Xbee module
	frame.append(0x01)      # frame ID for ack- 0 = disable

        frame.append(dest[0])   # 64 bit address (mac)
        frame.append(dest[1])
        frame.append(dest[2])
        frame.append(dest[3])
        frame.append(dest[4])
        frame.append(dest[5])
        frame.append(dest[6])
        frame.append(dest[7])

        frame.append(0x00)      # always reserved in digimesh mode

        txdata = txdata[:20]    # make sure we only use 20 bytes here

        for i in txdata:        # move data to transmit buffer
            frame.append(i)
        frame.append(0)         # checksum position

	cks = 0;
	for i in range(3,34):	# compute checksum
	   cks += int(frame[i])

	i = (255-cks) & 0x00ff
        frame[34] = i

        for d in frame:
            self.sp.write(chr(d))

        print "SENT"
        for d in frame:
            p = "%x" % d
            print p,
        print
