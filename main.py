from flask import Blueprint, render_template, request, jsonify
import MySQLdb
import time
import redis
import base64
import json

main_api = Blueprint('main_api', __name__)

NOP = "sent"

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
         onclick="javascript:getNode('%s');"
        />''' % ( x, y, address)      #'''

    data = data + '<text x="%s" y="%s" font-size="28" class="myfont" fill="black" ' % (x+10, y+30 )
    data = data + 'onclick="javascript:getNode('
    data = data + "'%s');" % address
    data = data + '">'
    data = data + '%s' % name
    data = data + '</text>'

    data = data + '<text x="%s" y="%s" font-size="22" class="myfont" fill="black" ' % (x+10, y+60)
    data = data + 'onclick="javascript:getNode('
    data = data + "'%s');" % address
    data = data + '">'
    data = data + '%s' % address
    data = data + '</text>'

    print data

    return data

# find neighbors on the Network
@main_api.route('/scannetwork/', methods=['POST', 'GET'])
def scannetwork():
    print "push tx message code"

    senddata = base64.b64encode(json.dumps(['SCAN', '0', '1']))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return NOP

@main_api.route('/displaynode/', methods=['POST','GET'])
def displayNode():
    address = request.form['address']

    print "displayNode"
    senddata = base64.b64encode(json.dumps(['READNODE', address, '01234567890123456789']))
    r = redis.Redis(host='127.0.0.1', port='6379')
    r.rpush(['queue:xbeetx'], senddata )

    return render_template('node.html', address=address)
