#!/usr/bin/env python3
"""
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import threading
import time
import json
import mysql.connector
import socket
import ast
from datetime import datetime
from datetime import date


def run_sequence(seq_id, is_batch):
    logging.info('Running sequence id: {}'.format(seq_id))
    start(seq_id, is_batch)
    logging.info('Finished sequence id: {}'.format(seq_id))


def union_dict(msg_data, json_mysql):
    json_mysql = ast.literal_eval(json_mysql)
    if not json_mysql:
        return msg_data
    for k, value in json_mysql.items():
        msg_data[k] = value
    return msg_data


def save_data_toMySQL(data, cursorObject, dataBase, seq_id):
    if data['msg id'] == 'AP2SR2':  # todo - need to change to SR2AP2
        query_run_results = '''INSERT INTO run_results (sequence_id, op_num, assembly_operation_id, delta_time,
               collisions_num,end_effector_changes,near_miss_distance, near_miss,ok)
                VALUES (%s, %s,%s, %s,%s,%s,%s,%s,%s)'''
        val = (seq_id, data['op num'], data['assembly operation id'], data['delta time'], data['collisions'],
               data['end effector changes'], data['near miss distance'], data['near miss'], data['ok'])
        cursorObject.execute(query_run_results, val)
        dataBase.commit()
        print("commited")


def send_operations_batch(seq_id, host, port, cursorObject):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        query = """SELECT count(*) FROM sequences_operations WHERE sequence_id = %s"""
        cursorObject.execute(query, (seq_id,))
        length_seq = cursorObject.fetchall()[0][0]
        # prepare msg:
        msg = {'msg id': 'AP2SR5', 'msg data': {'operations': []}}
        operations_list = []
        for j in range(1, length_seq+1):
            ao_msg = {'msg id': 'AP2SR2', 'msg data': None}
            msg_data_ao = msg_data_for_ao(seq_id, j, cursorObject)
            ao_msg['msg data'] = msg_data_ao
            operations_list.append(ao_msg)
        msg['msg data']['operations'] = operations_list
        jsonObj = json.dumps(msg)
        json_encode = jsonObj.encode()
        s.sendall(json_encode)


def msg_data_for_ao(seq_id, op_num, cursorObject):
    query = """SELECT assembly_operation_id, values_to_update  FROM sequences_operations 
                        WHERE sequence_id = %s AND op_num = %s"""
    cursorObject.execute(query, (seq_id, op_num))
    extract_data = cursorObject.fetchall()
    assembly_operation_id = extract_data[0][0]
    json_mysql = extract_data[0][1]
    msg_data = {'op num': op_num, 'assembly operation id': assembly_operation_id}
    msg_data = union_dict(msg_data, json_mysql)
    return msg_data


def send_to_simulate(seq_id, host, port, cursorObject):
    query = """SELECT work_cell_id, process_name, no_AO_QT FROM sequences WHERE sequence_id = %s"""
    cursorObject.execute(query, (seq_id,))
    data = cursorObject.fetchall()
    work_cell_id = data[0][0]
    process_name = data[0][1]
    number_of_operations = int(data[0][2])
    today = str(date.today())
    now = str(datetime.now().strftime("%H:%M:%S"))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        for i in range(number_of_operations + 2):
            msg = {'msg id': None, 'msg data': None}
            if i == 0:  # opening msg
                msg['msg id'] = 'AP2SR1'
                query = """SELECT domain_code FROM process_details WHERE process_name = %s"""
                cursorObject.execute(query, (process_name,))
                domain_code = cursorObject.fetchall()[0][0]
                msg_data = {'process name': process_name, 'domain code': domain_code, 'work cell id': work_cell_id,
                            'sequence id': seq_id, 'op num': number_of_operations, 'platform': 's',
                            'date': today, 'time': now, 'operator id': 'shir'}
            elif i == number_of_operations + 1:  # ending msg
                msg['msg id'] = 'AP2SR4'
                msg_data = {'process name': process_name, 'sequence id': seq_id}
            else:
                # sending  assembly operations:
                msg_data = msg_data_for_ao(seq_id, i, cursorObject)
                msg['msg id'] = 'AP2SR2'
            msg['msg data'] = msg_data
            print("msg num", i, ":", msg)
            # sending
            jsonObj = json.dumps(msg)
            json_encode = jsonObj.encode()
            s.sendall(json_encode)
            # receiving
            data = s.recv(4096)
            data = data.decode("utf-8")
            data = json.loads(data)
            data = data.replace("null", "None")
            # save_data_toMySQL(eval(data), cursorObject, dataBase, seq_id)


def start(seq_id, is_batch):
    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 8787  # The port used by the server
    # connecting to the database
    dataBase = mysql.connector.connect(
        host="robot-db.cmemwv1xnh6c.eu-west-1.rds.amazonaws.com",
        port=8080,
        user="siemens",
        passwd="siemens_bgu_mysql",
        database="micro_macro",
        use_pure=True)

    # preparing a cursor object
    cursorObject = dataBase.cursor()
    if is_batch:
        send_operations_batch(seq_id, HOST, PORT, cursorObject)
    else:
        send_to_simulate(seq_id, HOST, PORT, cursorObject)


class S(BaseHTTPRequestHandler):
    t1 = None

    # body of the constructor

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        try:
            # micro-macro3.surge.sh?seq=ele_zubi&isbatch=true
            seq_arg = str(self.path).split('?')[1]
            params_dict = {}
            key_val_pairs = seq_arg.split('&')
            for pair in key_val_pairs:
                key_val = pair.split('=')
                params_dict[key_val[0]] = key_val[1]

            seq_id = params_dict["seq"]

            if "batchmode" in params_dict.keys() and params_dict["batchmode"] == 'true':
                is_batch = True
            else:
                is_batch = False

            if not S.t1 or not S.t1.is_alive():
                S.t1 = threading.Thread(target=run_sequence, args=[seq_id, is_batch])
                S.t1.start()
                response = '{{"seq":"{}","status":"ok"}}'.format(seq_id)
            else:
                response = '{{"seq":"{}","status":"busy"}}'.format(seq_id)

        except IndexError as e:

            response = '{"status":"ok"}'

        self._set_response()
        logging.info('Response: {}'.format(response))
        self.wfile.write(response.encode('utf-8'))

        # logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        # self._set_response()
        # self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def end_headers(self) -> None:
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


def run(server_class=HTTPServer, handler_class=S, port=8090):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
