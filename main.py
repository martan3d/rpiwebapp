from flask import Blueprint, render_template, request, jsonify
import MySQLdb
import time
import redis
import base64
import json

main_api = Blueprint('main_api', __name__)

NOP = "sent"
GLOB = 'G'

# main entry point, used on load page
@main_api.route('/main/', methods=['GET','POST'])
def main():
    return render_template('main.html')

# API entry point from web page javascript refresh code
@main_api.route('/refresh/', methods=['GET','POST'])
def refresh():

    data = '<svg id="svg1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="1000">'
    data = data + '<style>.myfont { font: 20px sans-serif; } </style>'

    data = data + drawNodes(data)
    data = data + "</svg>"
    return data

# draw the big scan button at the top of the screen
def drawNodes(data):
    x = 10
    y = 10
    db = MySQLdb.connect(host="localhost", passwd="raspberry", db="webapp")
    cr = db.cursor()
    sql = "SELECT * from nodes;"
    cr.execute(sql)
    results = cr.fetchall()
    for r in results:
        data = data + drawBox(x, y, r[0],r[1],r[2],r[3],r[4])
        y = y + 110
    return data

def drawBox(x, y, id, name, address, type, status):
    data = '''
        <rect
         fill="lightgray"
         style="stroke:black;stroke-width:1;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1"
         id="scanbutton" width="200" height="80"
         x="%s" y="%s" rx="6" ry="6"
         onclick="javascript:getNode('%s','%s');"
        />''' % ( x, y, address, name)      #'''

    data = data + '<text x="%s" y="%s" font-size="28" class="myfont" fill="black" ' % (x+10, y+30 )
    data = data + 'onclick="javascript:getNode('
    data = data + "'%s','%s');" % (address, name)
    data = data + '">'
    data = data + '%s' % name
    data = data + '</text>'

    data = data + '<text x="%s" y="%s" font-size="22" class="myfont" fill="black" ' % (x+10, y+60)
    data = data + 'onclick="javascript:getNode('
    data = data + "'%s','%s');" % (address, name)
    data = data + '">'
    data = data + '%s' % address
    data = data + '</text>'

    return data

# find neighbors on the Network
@main_api.route('/scannetwork/', methods=['POST', 'GET'])
def scannetwork():
    senddata = base64.b64encode(json.dumps(['SCAN', '0', '1']))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    return NOP

@main_api.route('/displaynode/', methods=['POST','GET'])
def displayNode():
    global GLOB
    address = request.form['address']
    name    = request.form['name']
    senddata = base64.b64encode(json.dumps(['READNODE', address, '01234567890123456789']))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )
    GLOB = 'G'
    return render_template('node.html', address=address, name=name)

@main_api.route('/setcv/', methods=['POST','GET'])
def setcv():
    cvaddr = int(request.form['cvaddr'])
    cvdata = int(request.form['cvdata'])

    lsb = cvaddr & 0x00ff
    msb = cvaddr & 0xff00
    msb = msb >> 8

    DCCCVPACKET = 16
    datapaylod = chr(DCCCVPACKET) + chr(lsb) + chr(msb) + chr(cvdata) + '4567890123456789'
    senddata = base64.b64encode(json.dumps(['READNODE', address, datapayload ]))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    print cvaddr
    print cvdata

    return NOP


@main_api.route('/checkscan/', methods=['POST','GET'])
def checkscan():
    global GLOB
    return GLOB

@main_api.route('/refreshnode/', methods=['POST','GET'])
def refreshnode():
    global GLOB
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

    data = data + '''
       <table style="margin-left:50px;">
       <td>ProtoThrottle ID</td><td><input style="text-align:right;margin-left:40px;font-size:18px;width:50px;padding-right:4px;" type="text" name="pid" value="0"></td>
       <tr>
       <td>Base ID</td><td><input style="text-align:right;margin-left:40px;font-size:18px;width:50px;padding-right:4px;" type="text" name="bid" value="A"></td>
       <tr>'''

    if nodetype == 'W':
       data = data + '''
       <td>DCC Address</td><td><input style="text-align:right;margin-left:40px;font-size:18px;width:50px;padding-right:4px;" type="text" name="dccaddr" value="3"></td>
       '''
    if nodetype == 'A':
       data = data + '''
       <td>Airwire Channel</td><td><input style="text-align:right;margin-left:40px;font-size:18px;width:50px;padding-right:4px;" type="text" name="dccaddr" value="3"></td>
       '''

    data = data + '''
       </table>
    </div>'''

    if nodetype == 'W':
       data = data + '''
         <div style="font-size:22px;text-align:center;margin-top:10px;">
           <div style="text-align:center;margin-top:16px;">
             <span style="position:block;font-size:10px;margin-right:28px;">CVaddr</span> <span style="position:block;font-size:10px;margin-right:62px;">CVdata</span>
           </div>
           <div style="text-align:center;margin-top:10px;">
               <input type="text" id="cvaddr" style="width:54px;height:32px;font-size:20px;margin-right:8px;margin-left:8px;">
               <input type="text" id="cvdata" style="width:54px;height:32px;font-size:20px;margin-right:8px;">
               <input class="theButton" type="button" style="position:relative;top:50%;transform:translateY(-8%);" onclick="setCV();" value="Prg">
           </div>
           <div style="text-align:center;margin-top:40px;">
             <input  class="mybutton" type="button" onclick="setHome();" value="Home">
           </div>
        </div>
     '''
    if nodetype == 'A':
       data = data + '''
           <div style="text-align:center;margin-top:40px;">
             <input  class="mybutton" type="button" onclick="setHome();" value="Home">
           </div>
     '''

    return data
