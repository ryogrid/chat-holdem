import os
import random
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi, sleep

ws_set = set()

user_hash = {} # ws => name
user_list = [] # contains names

cur_sb = -1
flop_round = 0 # 0-4

INIT_CHIP = 500
SB_BLIND = 1
pod_amount = 0
left_chips = [INIT_CHIP, INIT_CHIP, INIT_CHIP, INIT_CHIP, INIT_CHIP]
betting_chips = [0, 0, 0, 0, 0]
hands = [["", "" ], ["", "" ], ["", "" ], ["", "" ], ["", "" ]]
comm_cards = ["??", "??", "??", "??", "??"]
user_names = ["", "", "", "", ""]
roles = ["", "", "", "", ""]
active_idx = 0
statuses = ["", "", "", "", ""]
cards = []
open_flags = [0, 0, 0, 0, 0]
static_open_flags = [0, 0, 0, 0, 0]

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

def handle_join(name):
    global user_names
    global user_list
    idx = user_list.index(name)
    user_names[idx] = name
    return

def handle_next_game():
    global hands, roles, statuses, cur_sb
    global active_idx, pod_amount, flop_round
    global comm_cards, static_open_flags, betting_chips
    
    user_num = len(user_list)
    init_cards()    
    for idx in xrange(user_num):
        hands[idx][0] = draw_a_card()
        hands[idx][1] = draw_a_card()
    static_open_flags = [0, 0, 0, 0, 0]
    pod_amount = 0
    flop_round = 0
    comm_cards = ["??", "??", "??", "??", "??"]
    cur_sb += 1
    sb_player_idx = cur_sb % user_num
    bb_player_idx = (cur_sb + 1) % user_num

    for idx in xrange(user_num):
        if idx == sb_player_idx:
            roles[idx] = "SB"
            left_chips[idx] -= SB_BLIND
            betting_chips[idx] = SB_BLIND
        elif idx == bb_player_idx:
            roles[idx] = "BB"
            left_chips[idx] -= SB_BLIND * 2
            betting_chips[idx] = SB_BLIND * 2
        else:
            roles[idx] = ""            
            statuses[idx] = ""
    active_idx = (cur_sb + 2) % user_num
    mark_active(active_idx)

def mark_active(mark_idx):
    global statuses
    global user_list
    global active_idx
    user_num = len(user_list)
    not_all_flag = False

    for idx in xrange(user_num):
        if static_open_flags[idx] == 0:
            not_all_flag = True
    # if all users are opening cards
    if not_all_flag == False:
        statuses[(mark_idx + 1) % user_num] = "###"
        return

    active_idx = mark_idx    
    if static_open_flags[mark_idx] == 1:
        for inc in xrange(1,user_num):
            if static_open_flags[(mark_idx + inc) % user_num] == 0:
                active_idx = (mark_idx + inc) % user_num
                break
    for idx in xrange(user_num):
        if idx == active_idx:
            statuses[idx] = "###"
        else:
            statuses[idx] = ""

def remove_card(user_idx):
    global hands
    hands[user_idx][0] = "XX"
    hands[user_idx][1] = "XX"
    static_open_flags[user_idx] = 1

def handle_bet(name, amount):
    global user_list
    global betting_chips
    global active_idx
    global left_chips
    user_num = len(user_list)    
    idx = user_list.index(name)
    betting_chips[idx] += int(amount)
    left_chips[idx] -= int(amount)
    active_idx += 1
    active_idx = active_idx % user_num
    mark_active(active_idx)
            
def handle_fold(name):
    global user_list
    global active_idx
    user_num = len(user_list)        
    idx = user_list.index(name)
    remove_card(idx)
    active_idx += 1
    active_idx = active_idx % user_num    
    mark_active(active_idx)

def handle_open(name):
    global user_list
    user_num = len(user_list)        
    idx = user_list.index(name)
    static_open_flags[idx] = 1

def gather_chips():
    global betting_chips
    global pod_amount
    for idx in xrange(len(betting_chips)):
        pod_amount += betting_chips[idx]
        betting_chips[idx] = 0
    
def handle_next_betting():
    global flop_round
    global user_list
    gather_chips()
    flop_round += 1
    user_num = len(user_list)    
    active_idx = cur_sb % user_num
    mark_active(active_idx)
    if flop_round == 1:
        comm_cards[0] = draw_a_card()
        comm_cards[1] = draw_a_card()
        comm_cards[2] = draw_a_card()        
    if flop_round == 2:
        comm_cards[3] = draw_a_card()
    if flop_round == 3:
        comm_cards[4] = draw_a_card()

def handle_move_chip_from_pod(player_number, amount):
    global left_chips
    global pod_amount
    left_chips[int(player_number) - 1] += int(amount)
    pod_amount -= int(amount)
    
def handle_set_chip_amount_of_player(player_number, amount):
    global left_chips
    left_chips[int(player_number) - 1] = int(amount)

def handle_end_table():
    global user_hash, user_list, cur_sb, flop_round, pod_amount, left_chips
    global betting_chips, hands, comm_cards, user_names, roles, active_idx
    global statuses, cards, open_flags, static_open_flags
    
    user_hash = {} # ws => name
    user_list = [] # contains names
    cur_sb = -1
    flop_round = 0 # 0-4
    pod_amount = 0
    left_chips = [INIT_CHIP, INIT_CHIP, INIT_CHIP, INIT_CHIP, INIT_CHIP]
    betting_chips = [0, 0, 0, 0, 0]
    hands = [["", "" ], ["", "" ], ["", "" ], ["", "" ], ["", "" ]]
    comm_cards = ["??", "??", "??", "??", "??"]
    user_names = ["", "", "", "", ""]
    roles = ["", "", "", "", ""]
    active_idx = 0
    statuses = ["", "", "", "", ""]
    cards = []
    open_flags = [0, 0, 0, 0, 0]
    static_open_flags = [0, 0, 0, 0, 0]

    
def handle_commands(name, pure_text):
    if pure_text == "j":
        handle_join(name)
    elif pure_text == "ng":
        handle_next_game()
    elif pure_text.split(" ")[0] == "b":
        handle_bet(name, pure_text.split(" ")[1])
    elif pure_text == "f":
        handle_fold(name)
    elif pure_text == "o":
        handle_open(name)
    elif pure_text == "n":
        handle_next_betting()
    elif pure_text.split(" ")[0] == "pmv":
        handle_move_chip_from_pod(pure_text.split(" ")[1], pure_text.split(" ")[2])
    elif pure_text.split(" ")[0] == "pset":
        handle_set_chip_amount_of_player(pure_text.split(" ")[1], pure_text.split(" ")[2])
    elif pure_text == "cl":
        handle_end_table()
        
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
    if open_flags[0] == 1 or static_open_flags[0] == 1:
        ret_str += "<td>" + hands[0][0] + " " + hands[0][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    if open_flags[1] == 1 or static_open_flags[1] == 1:
        ret_str += "<td>" + hands[1][0] + " " + hands[1][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    if open_flags[2] == 1 or static_open_flags[2] == 1:
        ret_str += "<td>" + hands[2][0] + " " + hands[2][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    if open_flags[3] == 1 or static_open_flags[3] == 1:
        ret_str += "<td>" + hands[3][0] + " " + hands[3][1] + "</td>"
    else:
        ret_str += "<td>?? ??</td>"
    if open_flags[4] == 1 or static_open_flags[4] == 1:
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
        user_name = msg.split(":")[0]        
        if (not (ws in user_hash)) or (ws in user_hash and user_hash[ws] == "init"):
            user_hash[ws] = user_name
            if user_name != "init":
                user_list.append(user_name)
        if ws in user_hash and user_name not in user_list:
            if user_name != "init":
                user_list.append(user_name)
        remove = set()        
        name = msg.split(":")[0]
        pure_text = msg.split(":")[1]
        try:
            handle_commands(name, pure_text)
        except Exception:
            import traceback
            traceback.print_exc()
            return
        for s in ws_set:
            try:
                if s in user_hash:
                    user_name = user_hash[s]
                else:
                    user_name = "init"
                    
                if user_name != "init":
                    make_enable_open(user_list.index(user_name))
                s.send(msg + "," + gen_table(user_name, msg))
                make_all_close()
            except Exception:
                import traceback
                traceback.print_exc()
                remove.add(s)
        for s in remove:
            ws_set.remove(s)
    print 'exit!', len(ws_set)
                
def myapp(environ, start_response):
    path = environ["PATH_INFO"]
    if path == "/":
        start_response("200 OK", [("Content-Type", "text/html")])
        return open('./chat_holdem.html').read()
    elif path == "/chat":
        return chat_handle(environ, start_response)
    raise Exception('Not found.')

print("Server is running on localhost:8080...")
server = pywsgi.WSGIServer(('0.0.0.0', 8080), myapp, handler_class=WebSocketHandler)
server.serve_forever()

