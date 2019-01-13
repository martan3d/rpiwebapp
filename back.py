import redis
import json
import base64
import time


z = [0x7e, 0x00, 0x14, 0x81, 0x00, 0x00, 0x33, 0x02, 0xd0, 0x30, 0x0f, 0xfc, 0xf2, 0x53, 0x80, 0x03, 0x00, 0x00, 0x00, 0x00, 0x81, 0x00, 0x8c, 0x69]

# pop off any messages that have been received, push any that need to go out.

r = redis.Redis(host='127.0.0.1', port='6379')

then = time.time()

while(1):

     data = r.rpop(['queue:xbee'])
     if data != None:
        dcode = json.loads(base64.b64decode(data))
        for d in dcode:
           print hex(d),
        print
        print

     now = time.time() - then
     if now > 2:
        then = time.time()
        print 'push transmit'
        r.rpush(['queue:xbeetx'], base64.b64encode(json.dumps(z)) )
