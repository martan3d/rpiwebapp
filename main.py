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
    senddata = base64.b64encode(json.dumps(['READNODE', address, '01234567890123456789']))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    GLOB = 'G'
    return render_template('node.html', address=address, name=name, x=mx, y=my)

@main_api.route('/setcv/', methods=['POST','GET'])
def setcv():
    cvaddr = int(request.form['cvaddr'])
    cvdata = int(request.form['cvdata'])
    address = request.form['address']

    lsb = cvaddr & 0x00ff
    msb = cvaddr & 0xff00
    msb = msb >> 8

    DCCCVPACKET = 16
    datapayload = chr(DCCCVPACKET) + chr(lsb) + chr(msb) + chr(cvdata) + '4567890123456789'
    senddata = base64.b64encode(json.dumps(['SETCV', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP

@main_api.route('/setdcc/', methods=['POST','GET'])
def setdcc():
    print "SETDCC"
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

    consistdir = int(request.form['consistdir'])
    address = request.form['address']

    SETCONSISTDIR = 46
    datapayload = chr(SETCONSISTDIR) + chr(consistdir) + '234567890123456789'
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP

@main_api.route('/setproto/', methods=['POST','GET'])
def setproto():
    print "SETPROTO"

    protoaddr = int(request.form['protoaddr'])
    address = request.form['address']

    print protoaddr, address

    SETPROTO = 39
    datapayload = chr(SETPROTO) + chr(protoaddr) + '234567890123456789'
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP


@main_api.route('/setbase/', methods=['POST','GET'])
def setbase():
    print "SETBASE"

    baseaddr = ord(request.form['baseaddr'])
    address = request.form['address']
    print baseaddr, address

    SETBASE = 38
    datapayload = chr(SETBASE) + chr(baseaddr) + '234567890123456789'
    senddata = base64.b64encode(json.dumps(['SETDCC', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP


@main_api.route('/checkscan/', methods=['POST','GET'])
def checkscan():
    global GLOB
    return GLOB

@main_api.route('/refreshnode/', methods=['POST','GET'])
def refreshnode():
    global GLOB
    address = request.form['address']
    r = redis.Redis(host='127.0.0.1', port='6379')
    rxdata = r.rpop(['queue:xbee'])
    if rxdata != None:
       GLOB = 'S'
       message = json.loads(base64.b64decode(rxdata))
       print "MAIN", message
       nodetype = chr(message[9])
       addrproto = message[11]
       addrbase  = message[10]
       airchan   = message[12]
       dccaddr   = message[12]
       decoder   = message[13]

       r.set("NodeType", nodetype)
       r.set("AddrProto", addrproto)
       r.set("AddrBase", addrbase)

       if nodetype == 'A':   # airwire
          r.set("airChan", airchan)

       if nodetype == 'W':   # Widget
          r.set("dccAddr", dccaddr)
          r.set("decoder", decoder)
    else:
       nodetype  = r.get("NodeType")
       addrproto = r.get("AddrProto")
       addrbase  = r.get("AddrBase")
       dccaddr   = r.get("dccAddr")
       airchan   = r.get("airChan")

    # use redis variables below

    data = '<div style="width:95%;margin:0 auto;">'

    if nodetype == 'W':
       data = '<div style="font-size:24px;margin:20px;text-align:center;">Xbee DCC Receiver</div>'

    if nodetype == 'A':
       data = '<div style="font-size:24px;margin:20px;text-align:center;">Airwire Translator</div>'

    data = data + '<input type="hidden" id="address" value="%s">' % address

    data = data + '''
       <table align=center id="table1">

       <td>ProtoThrottle ID</td>
       <td style="width:20px;"> &nbsp; </td><td></td>
       <td style="width:44px;"><input class="myinput" type="text" id="pid" value="0"></td>
       <td><input class="theButton" type="button" onclick="setProto();" value="Prg"></td>
       <tr>

       <td>Base ID</td>
       <td> &nbsp; </td><td></td>
       <td><input class="myinput" type="text" id="bid" value="A"></td>
       <td><input  class="theButton" type="button" onclick="setBase();" value="Prg"></td>
       <tr>

       <td>Loco Address</td>
       <td> &nbsp; </td><td></td>
       <td><input class="myinput" type="text" id="dccaddr" value="3"></td>
       <td><input  class="theButton" type="button" id="dccaddr" onclick="setMaster();" value="Prg"></td>
       <tr>

       <td>Consist</td><td></td>
       <td><input type="text" id="consistdir" class="myinput" value="Off"></td>
       <td><input class="myinput" type="text" id="consistaddr" value="3"></td>
       <td><input class="theButton" type="button" onclick="setConsist();" value="Prg"></td>
       <tr>

       <td> &nbsp; </td><td></td>
       <td style="font-size:10px;text-align:center;">CVaddr</td><td style="font-size:10px;text-align:center;">CVdata</td>
       <tr>
       <td>CVProg</td><td></td>
       <td><input type="text" id="cvaddr" class="myinput" value="0"></td>
       <td><input type="text" id="cvdata" class="myinput" value="0"></td>
       <td><input class="theButton" type="button" onclick="setCV();" value="Prg"></td>
       <tr>

       <td> &nbsp; </td><td style="font-size:10px;">Rev</td>
       <td style="font-size:10px;text-align:center;">LoLim</td><td style="font-size:10px;text-align:center;">HiLim</td>
       <tr>
       <td>Servo 0</td><td><input type="checkbox"></td>
       <td><input type="text" id="slo0" class="myinput"></td>
       <td><input type="text" id="shi0" class="myinput"></td>
       <td><input class="theButton" type="button" onclick="setServo(0);" value="Prg"></td>
       <tr>

       <td>Servo 1</td><td><input type="checkbox"></td>
       <td><input type="text" id="slo1" class="myinput"></td>
       <td><input type="text" id="shi1" class="myinput"></td>
       <td><input class="theButton" type="button" onclick="setServo(1);" value="Prg"></td>
       <tr>

       </table>

           <div style="text-align:center;margin-top:20px;">
             <input  class="mybutton" type="button" onclick="setHome();" value="Home">
           </div>'''

    return data
