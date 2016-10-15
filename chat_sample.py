import os
import random
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

ws_set = set()

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

user_hash = {} # ws => name
user_list = [] # contains names

cur_sb = 0
flop_round = 0 # 0-3

INIT_CHIP = 500
pod_amount = 0
left_chips = [INIT_CHIP, INIT_CHIP, INIT_CHIP, INIT_CHIP, INIT_CHIP]
betting_chips = [0, 0, 0, 0, 0]
hands = [["??", "??" ], ["??", "??" ], ["??", "??" ], ["??", "??" ], ["??", "??" ]]
comm_cards = ["??", "??", "??", "??", "??"]
user_names = ["init", "init", "init", "init", "init"]
roles = ["SB", "BB", "", "", ""]
statuses = ["###", "", "", "", ""]

def is_active(name):
    print("not implemented yet")

def handle_join(name):
    idx = user_list.index(name)
    user_names[idx] = name
    return
    
def handle_commands(name, pure_text):
    if pure_text == "j":
        handle_join(name)


def gen_table_inner(name):
    ret_str = "<div class=\"right_side\">"
    ret_str += "<H3>" + comm_cards[0] + " " + comm_cards[1] + " " + comm_cards[2] + " " + comm_cards[3] +" " + comm_cards[4] +  "</h3>"
    ret_str +=  """<table>
                      <tbody>
                        <tr>
                         <td>pod</td>"""

    ret_str += "<td>" + str(pod_amount) + "</td>"
    ret_str += """</tr>		  		  		  
		  <tr>
		    <td>player number</td>
		    <td>1</td>
		    <td>2</td>
		    <td>3</td>
		    <td>4</td>
		    <td>5</td>
		  </tr>
                  <tr>
		    <td>name</td>"""
    ret_str += "<td>" + user_names[0] + "</td>"
    ret_str += "<td>" + user_names[1] + "</td>"
    ret_str += "<td>" + user_names[2] + "</td>"
    ret_str += "<td>" + user_names[3] + "</td>"
    ret_str += "<td>" + user_names[4] + "</td>"
    ret_str += """</tr>
		  <tr>
		    <td>role</td>"""
    ret_str += "<td>" + roles[0] + "</td>"
    ret_str += "<td>" + roles[1] + "</td>"
    ret_str += "<td>" + roles[2] + "</td>"
    ret_str += "<td>" + roles[3] + "</td>"
    ret_str += "<td>" + roles[4] + "</td>"    
    ret_str += """</tr>
		  <tr>
		    <td>active</td>"""
    ret_str += "<td>" + statuses[0] + "</td>"
    ret_str += "<td>" + statuses[1] + "</td>"
    ret_str += "<td>" + statuses[2] + "</td>"
    ret_str += "<td>" + statuses[3] + "</td>"
    ret_str += "<td>" + statuses[4] + "</td>"        
    ret_str += """</tr>
		  <tr>
		    <td>betting chips</td>"""
    ret_str += "<td>" + str(betting_chips[0]) + "</td>"
    ret_str += "<td>" + str(betting_chips[1]) + "</td>"
    ret_str += "<td>" + str(betting_chips[2]) + "</td>"
    ret_str += "<td>" + str(betting_chips[3]) + "</td>"
    ret_str += "<td>" + str(betting_chips[4]) + "</td>"            
    ret_str += """</tr>
		  <tr>
		    <td>left chips</td>"""
    ret_str += "<td>" + str(left_chips[0]) + "</td>"
    ret_str += "<td>" + str(left_chips[1]) + "</td>"
    ret_str += "<td>" + str(left_chips[2]) + "</td>"
    ret_str += "<td>" + str(left_chips[3]) + "</td>"
    ret_str += "<td>" + str(left_chips[4]) + "</td>"                
    ret_str += """</tr>
		  <tr>
		    <td>hand</td>"""
    ret_str += "<td>" + hands[0][0] + " " + hands[0][1] + "</td>"
    ret_str += "<td>" + hands[1][0] + " " + hands[1][1] + "</td>"
    ret_str += "<td>" + hands[2][0] + " " + hands[2][1] + "</td>"
    ret_str += "<td>" + hands[3][0] + " " + hands[3][1] + "</td>"
    ret_str += "<td>" + hands[4][0] + " " + hands[4][1] + "</td>"
    ret_str += """</tr>
		</tbody>
	      </table>
           </div>"""

    return ret_str

def gen_table(name, msg):
    pure_text = msg.split(":")[1]
    handle_commands(name, pure_text)
    return gen_table_inner(name)

def chat_handle(environ, start_response):
    ws = environ['wsgi.websocket']
    ws_set.add(ws)
    print 'enter!', len(ws_set)
    while 1:
        msg = ws.receive()
        if msg is None:
            break
        print("point1")
        if (not (ws in user_hash)) or (ws in user_hash and user_hash[ws] == "init"):
            user_name = msg.split(":")[0]
            user_hash[ws] = user_name
            if user_name != "init":
                user_list.append(user_name)
        print("point2")
        remove = set()
        for s in ws_set:
            try:
                s.send(msg + "," + gen_table(user_name, msg))
            except Exception:
                import traceback
                traceback.print_exc()
                print("point_exception")
                remove.add(s)
        for s in remove:
            ws_set.remove(s)
    print 'exit!', len(ws_set)
                
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

