import os
import random
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

ws_set = set()

user_hash = {} # ws => name
user_list = [] # contains names

cur_sb = -1
flop_round = 0 # 0-3

INIT_CHIP = 500
pod_amount = 0
left_chips = [INIT_CHIP, INIT_CHIP, INIT_CHIP, INIT_CHIP, INIT_CHIP]
betting_chips = [0, 0, 0, 0, 0]
hands = [["??", "??" ], ["??", "??" ], ["??", "??" ], ["??", "??" ], ["??", "??" ]]
comm_cards = ["??", "??", "??", "??", "??"]
user_names = ["init", "init", "init", "init", "init"]
roles = ["", "", "", "", ""]
statuses = ["", "", "", "", ""]
cards = []
open_flags = [0, 0, 0, 0, 0]

def gen_all_cards():
    global cards
    nums = ["A", "2","3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    marks = ["s", "h", "d", "c"]
    cards = []
    for mark in marks:
        for num in nums:
            cards.append(mark + num)    
    
def shuffle_cards():
    global cards
    random.shuffle(cards)

def init_cards():
    gen_all_cards()
    shuffle_cards()

def draw_a_card():
    global cards
    return cards.pop()

def make_enable_open(idx):
    global open_flags
    open_flags[idx] = 1

def make_all_close():
    global open_flags
    open_flags = [0, 0, 0, 0, 0]

def is_active(name):
    print("not implemented yet")

def handle_join(name):
    global user_names
    idx = user_list.index(name)
    user_names[idx] = name
    return

def handle_next_game():
    global hands
    global roles
    global statuses
    global cur_sb
    user_num = len(user_list)
    init_cards()
    for idx in xrange(user_num):
        hands[idx][0] = draw_a_card()
        hands[idx][1] = draw_a_card()
    cur_sb += 1
    sb_player_idx = cur_sb % user_num
    bb_player_idx = (cur_sb + 1) % user_num    
    for idx in xrange(user_num):
        if idx == sb_player_idx:
            roles[idx] = "SB"
            statuses[idx] = "###"
        elif idx == bb_player_idx:
            roles[idx] = "BB"
        else:
            roles[idx] = ""
            statuses[idx] = ""
    
def handle_commands(name, pure_text):
    if pure_text == "j":
        handle_join(name)
    elif pure_text == "ng":
        handle_next_game()


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
    if open_flags[0] == 1:
        ret_str += "<td>" + hands[0][0] + " " + hands[0][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    if open_flags[1] == 1:
        ret_str += "<td>" + hands[1][0] + " " + hands[1][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    if open_flags[2] == 1:
        ret_str += "<td>" + hands[2][0] + " " + hands[2][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    if open_flags[3] == 1:
        ret_str += "<td>" + hands[3][0] + " " + hands[3][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    if open_flags[4] == 1:
        ret_str += "<td>" + hands[4][0] + " " + hands[4][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    ret_str += """</tr>
		</tbody>
	      </table>
           </div>"""

    return ret_str

def gen_table(name, msg):
    return gen_table_inner(name)


def chat_handle(environ, start_response):
    global user_list
    global user_hash
    
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
        name = msg.split(":")[0]
        pure_text = msg.split(":")[1]
        handle_commands(name, pure_text)        
        for s in ws_set:
            try:
                user_name = user_hash[s]
                if user_name != "init":
                    make_enable_open(user_list.index(user_name))
                    s.send(msg + "," + gen_table(user_name, msg))
                make_all_close()
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

