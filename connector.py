import pandas as pd
import json
import xlwings as xlwings


def find_next_A(seq_num, AO ,QT ,AO_index ,QT_index):
    for i in range(AO_index, len(AO)):
        print("AO", i)
        if AO[i]['OpNo'] == seq_num:
            AO_index = i+1
            print(AO[i])
            return AO[i]
    for j in range(QT_index, len(QT)):
        print("QT", j)
        if QT[j]['OpNo'] == seq_num:
            QT_index = j+1
            print(QT[j])
            return QT[j]



seq_num = 1
number_of_assemblies = 6
msg_num = 1
AO = pd.read_excel('DataBase_example_for_ASP.xlsx', sheet_name='AO')
QT = pd.read_excel('DataBase_example_for_ASP.xlsx', sheet_name='QT')
AP2SR_start = pd.read_excel('DataBase_example_for_ASP.xlsx', sheet_name='AP2SR_start')
AO = AO.to_dict(orient='records')
QT = QT.to_dict(orient='records')
AP2SR_start = AP2SR_start.to_dict(orient='records')

# send AP2SR- Process start
AP2SR_start[0]['MSG ID'] = "BGU", msg_num
msg_num = msg_num + 1
print(AP2SR_start)
with open('transformation.json', 'w') as fp:
    json.dump(AP2SR_start[0], fp)

#########################  wait
# send AP2SR- Assembly operation/ Quality test (macro)
AO_index = 0
QT_index = 0
while seq_num!=number_of_assemblies:
    Ass_to_send = find_next_A(seq_num, AO, QT, AO_index, QT_index)
    Ass_to_send['MSG ID'] = "BGU", msg_num
    msg_num = msg_num + 1
    with open('transformation.json', 'w') as fp:
        json.dump(Ass_to_send, fp)
    seq_num+=1


# get data from JSON
# SR2AP- Assembly operation/ Quality test (macro)
# צריך להפריד בין גיליון שמחזיר AO לבין |QT עקב שדות שונים
with open('transformation.json') as f:
  data = json.load(f)
print(data)
wb = xlwings.Book('DataBase_example_for_ASP.xlsx')
Sheet1 = wb.sheets[4]
row = 2
col = 1
data_val = list(data.values())
for i in range(0, len(data_val)):
    Sheet1.range(row, col).value = data_val[i]
    col+=1
wb.save()







