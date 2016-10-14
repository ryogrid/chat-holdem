import os
import random
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

ws_list = set()

def chat_handle(environ, start_response):
    global cnt
    ws = environ['wsgi.websocket']
    ws_list.add(ws)
    print 'enter!', len(ws_list)
    while 1:
        msg = ws.receive()
        if msg is None:
            break
        remove = set()
        for s in ws_list:
            try:
                s.send(msg)
            except Exception:
                remove.add(s)
        for s in remove:
            ws_list.remove(s)
    print 'exit!', len(ws_list)
                
def myapp(environ, start_response):
    path = environ["PATH_INFO"]
    if path == "/":
        start_response("200 OK", [("Content-Type", "text/html")])
        return open('./chat_sample.html').read()
    elif path == "/chat":
        return chat_handle(environ, start_response)
    raise Exception('Not found.')
        
server = pywsgi.WSGIServer(('0.0.0.0', 8080), myapp, handler_class=WebSocketHandler)

server.serve_forever()
