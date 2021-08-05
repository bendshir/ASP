import json
import mysql.connector
import socket
import ast
from datetime import datetime
from datetime import date

# User input:
sequence_id = 'ele_seq_1'  # / 'ele_seq_2'
HOST = '127.0.0.1'  # The server's hostname or IP address, '127.0.0.1' , socket.gethostname()
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

query = """SELECT work_cell_id, process_name, no_AO_QT FROM sequences WHERE sequence_id = %s"""
cursorObject.execute(query, (sequence_id,))
data = cursorObject.fetchall()
work_cell_id = data[0][0]
process_name = data[0][1]
number_of_operations = int(data[0][2])
today = str(date.today())
now = str(datetime.now().strftime("%H:%M:%S"))


def union_dict(msg_data, json_mysql):
    json_mysql = ast.literal_eval(json_mysql)
    if not json_mysql:
        return msg_data
    for k, value in json_mysql.items():
        msg_data[k] = value
    return msg_data


def save_data_toMySQL(data):
    if data['msg id'] == 'AP2SR2':  # todo - need to change to SR2AP2
        query_run_results = '''INSERT INTO run_results (sequence_id, op_num, assembly_operation_id, delta_time,
        collisions_num,end_effector_changes,near_miss_distance, near_miss,ok)
         VALUES (%s, %s,%s, %s,%s,%s,%s,%s,%s)'''
        val = (sequence_id, data['op num'], data['assembly operation id'], data['delta time'], data['collisions'],
               data['end effector changes'], data['near miss distance'], data['near miss'], data['ok'])
        cursorObject.execute(query_run_results, val)
        dataBase.commit()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for i in range(number_of_operations + 2):
        msg = {'msg id': None, 'msg data': None}
        if i == 0:  # opening msg
            msg['msg id'] = 'AP2SR1'
            query = """SELECT domain_code FROM process_details WHERE process_name = %s"""
            cursorObject.execute(query, (process_name,))
            domain_code = cursorObject.fetchall()[0][0]
            msg_data = {'process name': process_name, 'domain code': domain_code, 'work cell id': work_cell_id,
                        'sequence id': sequence_id, 'op num': number_of_operations, 'platform': 's',
                        'date': today, 'time': now, 'operator id': 'shir'}
        elif i == number_of_operations + 1:  # ending msg
            msg['msg id'] = 'AP2SR4'
            msg_data = {'process name': process_name, 'sequence id': sequence_id}
        else:
            # sending operations:
            query = """SELECT assembly_operation_id, values_to_update  FROM sequences_operations 
            WHERE sequence_id = %s AND op_num = %s"""
            cursorObject.execute(query, (sequence_id, i))
            extract_data = cursorObject.fetchall()
            assembly_operation_id = extract_data[0][0]
            json_mysql = extract_data[0][1]
            msg_data = {'op num': i, 'assembly operation id': assembly_operation_id}
            msg_data = union_dict(msg_data, json_mysql)
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
        data = data.replace("null", "None") ## to add
        save_data_toMySQL(eval(data))

