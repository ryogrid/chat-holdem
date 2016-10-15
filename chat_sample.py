import os
import random
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

ws_list = set()

replace_table_str = """
	    <div class="right_side">
	      <H3>hK sK cK</h3>
	      <table>
		<tbody>
		  <tr>
		    <td>pod</td>
		    <td>0</td>
		  </tr>		  		  		  
		  <tr>
		    <td>player number</td>
		    <td>1</td>
		    <td>2</td>
		    <td>3</td>
		    <td>4</td>
		    <td>5</td>
		  </tr>
		  <tr>
		    <td>name</td>
		    <td>aaa</td>
		    <td>bbb</td>
		    <td>ccc</td>
		    <td>ddd</td>
		    <td>eee</td>
		  </tr>
		  <tr>
		    <td>role</td>
		    <td>SB</td>
		    <td>BB</td>
		    <td></td>
		    <td></td>
		    <td></td>
		  </tr>	  
		  <tr>
		    <td>active</td>
		    <td></td>
		    <td></td>
		    <td>###</td>
		    <td></td>
		    <td></td>
		  </tr>
		  <tr>
		    <td>betting chips</td>
		    <td>1</td>
		    <td>2</td>
		    <td>0</td>
		    <td>0</td>
		    <td>0</td>
		  </tr>
		  <tr>
		    <td>reft chips</td>
		    <td>100</td>
		    <td>100</td>
		    <td>100</td>
		    <td>100</td>
		    <td>100</td>
		  </tr>
		  <tr>
		    <td>hand</td>
		    <td>hA sK</td>
		    <td></td>
		    <td></td>
		    <td></td>
		    <td></td>
		  </tr>
		</tbody>
	      </table>
           </div>
"""

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
                s.send(msg + "," + replace_table_str)
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

