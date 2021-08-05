#!/usr/bin/env python3
import socket
import json
person = '{"name": "null", "languages": ["English", "null"]}'
c = '{"msg id": "AP2SR2", "op num": "1", "assembly operation id": "ELE-INIT-A-1", "delta time": 0.5,' \
    '"actor id": "null"}'


# x = {'msg_id': 'SR2AP2', 'msg data': {'c': 5, 'd': 3}}  # data send to client
x = ["{\"msg id\": \"AP2SR1\", \"process name\": \"light panel assembly\", \"sequence id\": \"ele_seq_2\", \"ok\": 1}",
     '{"msg id": "AP2SR2", "op num": "1", "assembly operation id": "ELE-INIT-A-1", "delta time": 0.5, "ok": 1,'
     '"actor id": null, "end effector changes": 0, "collisions": 0, "near miss distance": 5.0, "near miss": 0, '
     '"joint id": [], "joint distance": []}',
     '{"msg id": "AP2SR2", "op num": "2", "assembly operation id": "ELE-PNC-A-2", "delta time": 30.5, "ok": 1,'
     '"actor id":null, "end effector changes": 0, "collisions": 0, "near miss distance": 5.0, "near miss": 0,'
     '"joint id": [], "joint distance": []}',
     {"msg id": "AP2SR2", "op num": "3", "assembly operation id": "ELE-SNP-A-3", "delta time": 0.782842, "ok": 1,
      "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0, "near miss": 0,
      "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "4", "assembly operation id": "ELE-PLC-A-4", "delta time": 16.159153208251318,
      "ok": 1, "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0,
      "near miss": 0, "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "5", "assembly operation id": "ELE-PNC-A-5", "delta time": 30.5, "ok": 1,
      "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0, "near miss": 0,
      "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "6", "assembly operation id": "ELE-SNP-A-6", "delta time": 1.0632139294097902,
      "ok": 1, "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0,
      "near miss": 0, "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "7", "assembly operation id": "ELE-PNC-A-2", "delta time": 30.5, "ok": 1,
      "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0, "near miss": 0,
      "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "8", "assembly operation id": "ELE-SNP-A-3", "delta time": 2.0686118826141167,
      "ok": 1, "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0,
      "near miss": 0, "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "9", "assembly operation id": "ELE-PLC-A-4", "delta time": 6.814328, "ok": 1,
      "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0, "near miss": 0,
      "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "10", "assembly operation id": "ELE-PNC-A-5", "delta time": 30.5, "ok": 1,
      "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0, "near miss": 0,
      "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "11", "assembly operation id": "ELE-SNP-A-6", "delta time": 1.5015528931085775,
      "ok": 1, "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0,
      "near miss": 0, "joint id": [], "joint distance": []},
     {"msg id": "AP2SR2", "op num": "12", "assembly operation id": "ELE-END-A-7", "delta time": 0.5, "ok": 1,
      "actor id": 'null', "end effector changes": 0, "collisions": 0, "near miss distance": 5.0, "near miss": 0,
      "joint id": [], "joint distance": []},
     {"msg id": "AP2SR4", "process name": "light panel assembly", "sequence id": "ele_seq_2", "ok": 1}
     ]
i = 0

HOST = socket.gethostname()  # Standard loopback interface address (localhost) change to socket.gethostname()
PORT = 8787  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                print("no more data")
            if not data:
                break
            jsonObj = json.dumps(x[i])
            i += 1
            json_encode = jsonObj.encode()
            conn.sendall(json_encode)
        #  conn.sendall(b"server: got the data, thank you")
