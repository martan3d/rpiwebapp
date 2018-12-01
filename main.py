from flask import Blueprint, render_template, request, jsonify
import MySQLdb
from xbee import *
import time

main_api = Blueprint('main_api', __name__)


# main entry point, used on load page
@main_api.route('/main/', methods=['GET','POST'])
def main():
    return render_template('main.html')

# API entry point from web page javascript refresh code
@main_api.route('/refresh/', methods=['GET','POST'])
def refresh():

    data = '<svg id="svg1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="1000">'
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
         id="scanbutton" width="400" height="100"
         x="%s" y="%s" rx="6" ry="6"
         onclick="javascript:scanNetwork();"
        />''' % ( x, y)      #'''

    data = data + '<text x="%s" y="%s" font-size="28" fill="black">' % (x+100, y+40)
    data = data + '%s' % name
    data = data + '</text>'

    data = data + '<text x="%s" y="%s" font-size="22" fill="black">' % (x+100, y+80)
    data = data + '%s' % address
    data = data + '</text>'


    return data

# find neighbors on the Digimesh Network
@main_api.route('/scannetwork/', methods=['POST', 'GET'])
def scannetwork():

    print "scannetwork"

    Xbee = xbeeController()
    Xbee.clear()

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

    Xbee.close()
