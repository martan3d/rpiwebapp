from flask import Blueprint, render_template, request, jsonify
import MySQLdb
import time
import redis
import base64
import json

main_api = Blueprint('main_api', __name__)

NOP = "sent"
GLOB = 'G'
HEIGHT = 0
WIDTH = 0

protad = { 'A': 0x30, 'B': 0x31, 'C': 0x32, 'D': 0x33, 'E': 0x34, 'F': 0x35, 'G': 0x36, 'H': 0x37, 'I': 0x38,
           'J': 0x39, 'K': 0x3a, 'L': 0x3b, 'M': 0x3c, 'N': 0x3d, 'O': 0x3e, 'P': 0x3f,
           'Q': 0x40, 'R': 0x41, 'S': 0x42, 'T': 0x43, 'U': 0x44, 'V': 0x45, 'W': 0x46, 'X': 0x47, 'Y': 0x48, 'Z': 0x49 }

adprot = { 0x30 :'A', 0x31 :'B', 0x32 :'C', 0x33 :'D', 0x34 :'E', 0x35 :'F', 0x36 : 'G', 0x37 : 'H', 0x38 : 'I', 0x39 : 'J',
           0x3a : 'K', 0x3b : 'L', 0x3c : 'M', 0x3d : 'N', 0x3e : 'O', 0x3f : 'P', 0x40 : 'Q', 0x41 : 'R', 0x42 : 'S',
           0x43 : 'T', 0x44 : 'U', 0x45 : 'V', 0x46 : 'W', 0x47 : 'X', 0x48 : 'Y', 0x49 : 'Z' }

@main_api.route('/notchtable/', methods=['GET','POST'])
def notchtable():
    global GLOB
    global HEIGHT
    global WIDTH

    my = int(HEIGHT)
    mx = int(WIDTH)

    address = request.form['address']
    name    = request.form['name']

    senddata = base64.b64encode(json.dumps(['READNOTCHES', address, '01234567890123456789']))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    GLOB = 'G'
    
    notches = []

    return render_template('notchtable.html', notches=notches, address=address, name=name)

@main_api.route('/setnotch/', methods=['GET','POST'])
def setnotch():
    enable    = "0"
    address   = request.form['address']
    notch     = request.form['notchnum']
    notchlow  = request.form['notchlow']
    notchhigh = request.form['notchhigh']
    notchval  = request.form['notchvalue']
    
    nhigh = "000" + notchhigh
    nhigh = nhigh[-3:]

    nlow = "000" + notchlow
    nlow = nlow[-3:]
    
    nval = "000" + notchval
    nval = nval[-3:]
    
    SETNOTCH = 50   ## 1        2        3       4         5         6         7         8         9        10        11         12       
    payload = chr(SETNOTCH) + enable + notch + nval[0] + nval[1] + nval[2] + nlow[0] + nlow[1] + nlow[2] + nhigh[0] + nhigh[1] + nhigh[2] + '01234567'   
    
    print "SET NOTCH", payload
    
    senddata = base64.b64encode(json.dumps(['SETNOTCH', address, payload]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    
    return NOP


@main_api.route('/setnodeid/', methods=['GET','POST'])
def setnodeid():
    # get new ID and 64bit address of node
    nodeid = request.form['nodeid'].encode("utf-8")
    address = request.form['address']

    print "SETNODEID", nodeid, " ", address

    REMOTECOMMAND = 23
    senddata = base64.b64encode(json.dumps(['REMOTECOMMAND', address, nodeid ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    return NOP


@main_api.route('/setsize/', methods=['GET','POST'])
def setsize():
    global HEIGHT
    global WIDTH

    HEIGHT = request.form['height']
    WIDTH  = request.form['width']

    print HEIGHT, WIDTH

    return NOP


# main entry point, used on load page
@main_api.route('/main/', methods=['GET','POST'])
def main():
    print "main"
    db = MySQLdb.connect(host="localhost", passwd="raspberry", db="webapp")
    cr = db.cursor()
    sql = "SELECT * from nodes;"
    cr.execute(sql)
    results = cr.fetchall()
    return render_template('main.html', results=results)


# API entry point from web page javascript refresh code
@main_api.route('/refresh/', methods=['GET','POST'])
def refresh():
    db = MySQLdb.connect(host="localhost", passwd="raspberry", db="webapp")
    cr = db.cursor()
    sql = "SELECT * from nodes;"
    cr.execute(sql)
    results = cr.fetchall()
    return render_template('main.html', results=results)

# find neighbors on the Network
@main_api.route('/scannetwork/', methods=['POST', 'GET'])
def scannetwork():
    print "scannetwork"
    senddata = base64.b64encode(json.dumps(['SCAN', '0', '1']))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    return NOP

@main_api.route('/displaynode/', methods=['POST','GET'])
def displayNode():
    global GLOB
    global HEIGHT
    global WIDTH

    my = int(HEIGHT)
    mx = int(WIDTH)

    address = request.form['address']
    name    = request.form['name']
    
    ## clear any old entries in queue
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.flushdb()
    
    print "PUSH READNODE", address
    
    senddata = base64.b64encode(json.dumps(['READNODE', address, '01234567890123456789']))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    GLOB = 'G'
    return render_template('node.html', address=address, name=name, x=mx, y=my)


##########################################################################

@main_api.route('/setservo/', methods=['POST','GET'])
def setservo():
    print "SETServo"
    servonum = request.form['servonum']
    servohi  = request.form['hilimit']
    servolo  = request.form['lolimit']
    servorev = request.form['reverse']
    address  = request.form['address']
    func     = request.form['func']

    shigh = "0000" + servohi
    shigh = shigh[-4:]

    slow  = "0000" + servolo
    slow = slow[-4:]

    if servorev == 'true': sr = '1'
    else: sr = '0'

    adr = "00" + func
    addr = adr[-2:]

    print addr[0]
    print addr[1]

    SETSERVOCONFIG = 47
    datapayload = chr(SETSERVOCONFIG) + servonum + shigh[0] + shigh[1] + shigh[2] + shigh[3] + slow[0] + slow[1] + slow[2] + slow[3] + sr + addr[0] + addr[1] + '3456789'
    print datapayload
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))

    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP


@main_api.route('/setcv/', methods=['POST','GET'])
def setcv():

    cvaddr = request.form['cvaddr']
    cvdata = request.form['cvdata']

    cva = "0000" + cvaddr
    cvad = cva[-4:]

    cvd  = "0000" + cvdata
    cvda = cvd[-4:]

    address = request.form['address']

    print address, cva, cvd

    DCCCVPACKET = 16
    datapayload = chr(DCCCVPACKET) + cvad[0] + cvad[1] + cvad[2] + cvad[3] + cvda[0] + cvda[1] + cvda[2] + cvda[3] +'90123456789'
    senddata = base64.b64encode(json.dumps(['SETCV', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP

@main_api.route('/setdcc/', methods=['POST','GET'])
def setdcc():
    print "SETLOCOADDRESS"
    adr = int(request.form['dccaddr'])
    address = request.form['address']

    dccaddr = "%04s" % adr

    SETDCCADDR = 40
    datapayload = chr(SETDCCADDR) + dccaddr[0] + dccaddr[1] + dccaddr[2] + dccaddr[3] + '567890123456789'
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))

    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP


@main_api.route('/setconsist/', methods=['POST','GET'])
def setconsist():
    print "SETCONSIST"
    adr = int(request.form['consistaddr'])
    address = request.form['address']

    ca = "%04s" % adr

    SETCONSISTADDR = 45
    datapayload = chr(SETCONSISTADDR) + ca[0] + ca[1] + ca[2] + ca[3] + '567890123456789'
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP

@main_api.route('/setconsistdir/', methods=['POST','GET'])
def setconsistdir():
    print "SETCONSISTDIR"
    consistdir = request.form['consistdir']
    address = request.form['address']
    cd = 0
    if consistdir == 'OFF':
       cd = 0
    if consistdir == 'FWD':
       cd = 1
    if consistdir == 'REV':
       cd = 2

    SETCONSISTDIR = 46
    datapayload = chr(SETCONSISTDIR) + chr(cd) + '234567890123456789'
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    return NOP

@main_api.route('/setservomode/', methods=['POST','GET'])
def setservomode():
    print "SETSERVOMODE"
    servomode = request.form['servomode']
    address = request.form['address']

    print servomode

    sm = 0
    if servomode == 'Steam':
       sm = 0
    if servomode == 'Couplers':
       sm = 1
    if servomode == "ESC":
       sm = 2

    SETSERVOMODE = 48
    datapayload = chr(SETSERVOMODE) + chr(sm) + '234567890123456789'
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    return NOP



@main_api.route('/setproto/', methods=['POST','GET'])
def setproto():
    print "SETPROTO"

    protoaddr = request.form['protoaddr']
    address = request.form['address']

    # proto = A-Z, encode to 0x30 to 0x49, discard if not that range

    if len(protoaddr) > 1:
       return NOP

    try:
       pa = protad[protoaddr]
    except:
       print "bad data"
       return NOP

    SETPROTO = 39
    datapayload = chr(SETPROTO) + chr(pa) + '234567890123456789'
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP


@main_api.route('/setbase/', methods=['POST','GET'])
def setbase():
    print "SETBASE"
    try:
       baseaddr = int(str(request.form['baseaddr']))
    except:
       return NOP

    if baseaddr > 31 or baseaddr < 0:
       return NOP

    address = request.form['address']
    print baseaddr, address

    SETBASE = 38
    datapayload = chr(SETBASE) + chr(baseaddr) + '234567890123456789'
    print datapayload
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP


def consistScreen(address, name, message):
    nl = []
    nh = []
    nv = []
    
    enablenotches = message[10]
    l = 11
    for i in range(0,8):
        nl.append(message[l])
        l = l + 1
        nh.append(message[l])
        l = l + 1
        nv.append(message[l])
        l = l + 1
    
    data = '''    
        <table border="0" class="center" padding=4 style="align-self:center;margin-top:20px;">
           <td colspan=5 style="padding-top:8px;text-align:center;"><h3>Notch Table</h3></td>
           <tr><td></td><td>low</td><td>high</td><td>output</td><tr>'''
           
    for s in range(0,8):
        data = data + '<td style="text-align:right;"><b>%s - </b></td>' % str(s+1)
        data = data + '<td><input class=myinput type=text size=8 id=notchlow%s value=%s></td>' % (str(s+1), nl[s])
        data = data + '<td><input class=myinput type=text size=8 id=notchhigh%s value=%s></td>' % (str(s+1), nh[s])
        data = data + '<td><input class=myinput type=text size=8 id=notchoutput%s value=%s></td>' % (str(s+1), nv[s])
        data = data + '<td><input class="theButton" type="button" onclick="setNotch(%s);" value="Prg"></td>' % str(s+1)
        data = data + '<tr>'
        
    data = data + '<td colspan=5 style="text-align:center;padding-top:10px;">'
    data = data + '<input class="theButton" type="button" onclick="setHome();" value="Home">'
    data = data + '</td></table>'

    return data


def airwireScreen(address):
    r = redis.Redis(host='127.0.0.1', port='6379')
    addrbase    = r.get("AddrBase")
    addrproto   = r.get("AddrProto")
    dccaddr     = r.get("dccAddr")
    channel     = r.get("airChan")
    
    data = '<div style="width:95%;margin:0 auto;">'
    data = data + '<input type="hidden" id="address" value="%s">' % address

    data = data + '''
       <table align=center id="table1">
       <td>ProtoThrottle ID</td>
       <td style="width:20px;"> &nbsp; </td><td style="width:20px;"> &nbsp; </td><td></td>'''

    try:
       adr = adprot[int(addrproto)]
    except:
       adr = 0
       print 'addr decode bad', addrproto, adprot

    data = data + '''
       <td style="width:44px;"><input class="myinput" type="text" id="pid" value="%s"></td>''' % adr
    data = data + '''
       <td><input class="theButton" type="button" onclick="setProto();" value="Prg"></td>
       <tr>
       <td>Base ID</td>
       <td> &nbsp; </td><td> &nbsp; </td><td></td>'''

    data = data + '''
       <td><input class="myinput" type="text" id="bid" value="%s"></td>''' % addrbase

    data = data + '''
       <td><input  class="theButton" type="button" onclick="setBase();" value="Prg"></td>
       <tr>
       <td>Airwire Channel</td>
       <td> &nbsp; </td><td> &nbsp; </td><td></td>'''

    data = data + '''
       <td><input class="myinput" type="text" id="channel" value="%s"></td>''' % channel

    data = data + '''
      <td><input  class="theButton" type="button" id="channel" onclick="setMaster();" value="Prg"></td>'''
      
    data = data + '''
       <tr>
       <td> &nbsp; </td><td></td>
       <td style="font-size:10px;text-align:center;">DCCaddr</td>
       <td style="font-size:10px;text-align:center;">CVaddr</td>
       <td style="font-size:10px;text-align:center;">CVdata</td>
       <tr>
       <td>CVProg</td><td> &nbsp; </td>
       <td><input type="text" id="dccaddr" class="myinput" value="0"></td>
       <td><input type="text" id="cvaddr"  class="myinput" value="0"></td>
       <td><input type="text" id="cvdata"  class="myinput" value="0"></td>
       <td><input class="theButton" type="button" onclick="setCV();" value="Prg"></td>
       <tr>'''
            
    data = data + '''  
      </table> '''

    data = data + '''
           <div style="text-align:center;margin-top:20px;">
             <input  class="mybutton" type="button" onclick="setHome();" value="Home">
           </div>'''

    return data


@main_api.route('/checkscan/', methods=['POST','GET'])
def checkscan():
    global GLOB
    return GLOB

@main_api.route('/refreshnode/', methods=['POST','GET'])
def refreshnode():
    global GLOB
    print "REFRESH NODE"

    nodetype = "Z"

    try:
       address = request.form['address']
    except:
       address = ""
       
    try:
       name = request.form['name']
    except:
       name = ""
       
    r = redis.Redis(host='127.0.0.1', port='6379')
    rxdata = r.rpop(['queue:xbee'])

    if rxdata == None:
       data = '''
           <div style="text-align:center;margin-top:40px;">
             <input  class="mybutton" type="button" onclick="setHome();" value="Home">
           </div>'''       
       return data
       
    ## got a response, pull the data from it and build the page 

    GLOB = 'S'
    message = json.loads(base64.b64decode(rxdata))
    print "Return Message -> ", message

    nodetype    = chr(message[9])
    addrbase    = int(message[10])
    addrproto   = message[11]

    print "Node Type -> ", nodetype
       
    ## if this is a translator       
    dccaddr     = int(message[12])
    dccaddr     = dccaddr | (int(message[13]) >> 8)
    airchan     = message[14]
       
    ## otherwise it's an Xbee node
    locoaddr    = message[12]
    ch          = message[13] << 8
    locoaddr    = locoaddr | ch             # offset 4,5 in main.c firmware side

    consistaddr = message[14]               # 6,7
    ch          = message[15] << 8
    consistaddr = consistaddr | ch

    cdir        = message[16]               # 8

    svlo0       = message[17]               # 9,10
    ch          = message[18] << 8
    svlo0       = svlo0 | ch

    svhi0       = message[19]
    ch          = message[20] << 8          # 11,12
    svhi0       = svhi0 | ch

    svlo1       = message[21]               # 13,14
    ch          = message[22] << 8
    svlo1       = svlo1 | ch

    svhi1       = message[23]               # 15,16
    ch          = message[24] << 8
    svhi1       = svhi1 | ch

    svlo2       = message[25]               # 17,18                                                                                     ch          = message[22] << 8                                                                                                      svlo1       = svlo1 | ch                                                                                                     
    ch          = message[26] << 8
    svlo2       = svlo2 | ch

    svhi2       = message[27]               # 19,20
    ch          = message[28] << 8
    svhi2       = svhi2 | ch

    sv0func     = message[29]
    sv1func     = message[30]
    sv2func     = message[31]

    svrr        = message[32]
    servomode   = message[33]

    ## data pulled from return Xbee message, put in redis

    r.set("ConsistAddress", consistaddr)
    r.set("ConsistDirection", cdir)
    r.set("Servo0LowLim", svlo0)
    r.set("Servo0HighLim", svhi0)
    r.set("Servo1LowLim", svlo1)
    r.set("Servo1HighLim", svhi1)
    r.set("Servo2LowLim", svlo2)
    r.set("Servo2HighLim", svhi2)
    r.set("Servo0Func", sv0func)
    r.set("Servo1Func", sv1func)
    r.set("Servo2Func", sv2func)
    ##r.set("NodeType", nodetype)
    r.set("AddrProto", addrproto)
    r.set("AddrBase", addrbase)
    r.set("ServoReverse", svrr)
    r.set("ServoMode", servomode)
    r.set("airChan", airchan)
    r.set("locoAddr", locoaddr)
    r.set("dccAddr", dccaddr)

    ## Check message return to determine screen to display
    
    if nodetype == 'A':
       data = airwireScreen(address)
       return data

    if nodetype == 'W':
       data = nodeScreen(address)
       return data

    if nodetype == 'N':
       print "CONSIST SCREEN", address, name, message
       data = consistScreen(address, name, message)
       return data

       
def nodeScreen(address):

    r = redis.Redis(host='127.0.0.1', port='6379')

    nodetype    = r.get("NodeType")
    addrproto   = r.get("AddrProto")
    addrbase    = r.get("AddrBase")
    locoaddr    = r.get("locoAddr")
    airchan     = r.get("airChan")
    consistaddr = r.get("ConsistAddress")
    cdir        = r.get("ConsistDirection")
    svlo0       = r.get("Servo0LowLim")
    svhi0       = r.get("Servo0HighLim")
    svlo1       = r.get("Servo1LowLim")
    svhi1       = r.get("Servo1HighLim")
    svlo2       = r.get("Servo2LowLim")
    svhi2       = r.get("Servo2HighLim")
    sv0func     = r.get("Servo0Func")
    sv1func     = r.get("Servo1Func")
    sv2func     = r.get("Servo2Func")
    svrr        = r.get("ServoReverse")
    servomode   = r.get("ServoMode")

    fn0=sv0func
    fn1=sv1func
    fn2=sv2func

    data = '<div style="width:95%;margin:0 auto;">'
    data = data + '<input type="hidden" id="address" value="%s">' % address
    data = data + '''
       <table align=center id="table1">
       <td>ProtoThrottle ID</td>
       <td style="width:20px;"> &nbsp; </td><td style="width:20px;"> &nbsp; </td><td></td>'''

    try:
       adr = adprot[int(addrproto)]
    except:
       adr = 0
       print 'addr decode bad', addrproto, adprot

    data = data + '''
       <td style="width:44px;"><input class="myinput" type="text" id="pid" value="%s"></td>''' % adr
    data = data + '''
       <td><input class="theButton" type="button" onclick="setProto();" value="Prg"></td>
       <tr>
       <td>Base ID</td>
       <td> &nbsp; </td><td> &nbsp; </td><td></td>'''

    data = data + '''
       <td><input class="myinput" type="text" id="bid" value="%s"></td>''' % addrbase

    data = data + '''
       <td><input  class="theButton" type="button" onclick="setBase();" value="Prg"></td>
       <tr>
       <td>Loco Address</td>
       <td> &nbsp; </td><td> &nbsp; </td><td></td>'''

    data = data + '''
       <td><input class="myinput" type="text" id="dccaddr" value="%s"></td>''' % str(locoaddr)

    data = data + '''
      <td><input  class="theButton" type="button" id="dccaddr" onclick="setMaster();" value="Prg"></td>
      <tr>
      <td>Consist</td><td> &nbsp; </td><td></td>'''

    consist = 'OFF'
    if cdir == '1': consist = 'FWD'
    if cdir == '2': consist = 'REV'

    data = data + '''
       <td><div id="cdir" style="cursor:pointer;border:1px solid #666666;border-radius:4px;height:22px;text-align:center;padding-top:6px;" onclick="setConsDir();">%s</div></td>''' % consist

    data = data + '''
       <td><input class="myinput" type="text" id="consistaddr" value="%s"></td>''' % consistaddr

    data = data + '''
       <td><input class="theButton" type="button" onclick="setConsist();" value="Prg"></td>
       <tr>'''

    data = data + '''
       <td> &nbsp; </td><td></td>
       <td> &nbsp; </td><td style="font-size:10px;text-align:center;">CVaddr</td><td style="font-size:10px;text-align:center;">CVdata</td>
       <tr>
       <td>CVProg</td><td> &nbsp; </td><td></td>
       <td><input type="text" id="cvaddr" class="myinput" value="0"></td>
       <td><input type="text" id="cvdata" class="myinput" value="0"></td>
       <td><input class="theButton" type="button" onclick="setCV();" value="Prg"></td>
       <tr>'''

    if servomode == '0':
       svmstr = 'Steam'
    elif servomode == '1':
       svmstr = 'Couplers'
    else:
       svmstr = 'ESC'

    data = data + '''
       <td><div style="height:22px;"> </div></td><td></td><td></td><td><td>
       <tr>
       <td>Servo Mode</td><td> &nbsp; </td><td></td><td></td>
       <td colspan=2>
       <div id="smode" style="cursor:pointer;border:1px solid #666666;border-radius:4px;height:22px;text-align:center;padding-top:6px;" onclick="setServoMode();">%s</div></td>''' % svmstr

    checked = ''
    if (int(svrr) & 0x01) == 1:
        checked = 'checked'

    data = data + '''
       <tr>

       <td> &nbsp; </td><td style="font-size:10px;">Rev</td><td style="font-size:10px;padding-left:5px">Fn</td>
       <td style="font-size:10px;text-align:center;">LoLim</td><td style="font-size:10px;text-align:center;">HiLim</td>
       <tr>

       <td>Servo 0</td>
       <td><input id="ck0" type="checkbox" %s></td>
       <td><input type="text" id="fn0" class="myinputsmall" value="%s"></td>''' % (checked, fn0)

    data = data + '''
       <td><input type="text" id="slo0" class="myinput" value="%s"></td>
       <td><input type="text" id="shi0" class="myinput" value="%s"></td>''' % (svlo0, svhi0)

    data = data + '''
       <td><input class="theButton" type="button" onclick="setServo(0);" value="Prg"></td>
       <tr>'''

    checked = ''
    if (int(svrr) & 0x02) == 2:
        checked = 'checked'

    data = data + '''
       <td>Servo 1</td>
       <td><input id="ck1" type="checkbox" %s></td>
       <td><input type="text" id="fn1" class="myinputsmall" value="%s"></td>
       <td><input type="text" id="slo1" class="myinput" value="%s"></td>
       <td><input type="text" id="shi1" class="myinput" value="%s"></td>''' % (checked, fn1, svlo1, svhi1)

    data = data + '''
       <td><input class="theButton" type="button" onclick="setServo(1);" value="Prg"></td>
       <tr>'''

    checked = ''
    if (int(svrr) & 0x04) == 4:
        checked = 'checked'

    data = data + '''
       <td>Servo 2</td>
       <td><input id="ck2" type="checkbox" %s></td>
       <td><input type="text" id="fn2" class="myinputsmall" value="%s"></td>
       <td><input type="text" id="slo2" class="myinput" value="%s"></td>
       <td><input type="text" id="shi2" class="myinput" value="%s"></td>''' % (checked, fn2, svlo2, svhi2)

    data = data + '''
       <td><input class="theButton" type="button" onclick="setServo(2);" value="Prg"></td>
       <tr>
       </table>'''
    
    if consist != 'OFF':
       data = data + '''
           <div style="text-align:center;margin-top:20px;">
             <input class="mybutton" type="button" onclick="notchtable();" value="Notch Table">
          </div> '''
          
    data = data + '''
           <div style="text-align:center;margin-top:20px;">
             <input  class="mybutton" type="button" onclick="setHome();" value="Home">
           </div>'''

    return data
