import mysql.connector
import random

dataBase = mysql.connector.connect(
    host="robot-db.cmemwv1xnh6c.eu-west-1.rds.amazonaws.com",
    port=8080,
    user="admin",
    passwd="bguBGU1234",
    database="micro_macro",
    use_pure=True)
# preparing a cursor object
cursorObject = dataBase.cursor()

ao_name = 'KTR-FIX-A-404'
ao_similar = 'KTR-FIX-A-304'


def add_equipment_num_to_ao():
    query1 = """select assembly_operation_id from assembly_operations"""
    cursorObject.execute(query1, )
    ao = [value for value, in cursorObject.fetchall()]
    print(ao)

    for a in ao:
        query2 = """select count(*) from ao_actors where assembly_operation_id = %s"""
        cursorObject.execute(query2, (a,))
        num_actors = cursorObject.fetchall()[0][0]
        print(num_actors)

        sql1 = "UPDATE assembly_operations SET equipment_num = %s WHERE assembly_operation_id = %s"
        val1 = (num_actors, a)
        cursorObject.execute(sql1, val1)
        dataBase.commit()


def add_cost_to_ao():
    query = """select assembly_operation_id from assembly_operations where connection_type = 'end'"""
    cursorObject.execute(query, )
    ao = [value for value, in cursorObject.fetchall()]
    print(ao)
    for a in ao:
        r = random.uniform(2, 5)
        # set ao cost
        sql = "UPDATE assembly_operations SET ao_eng_cost = %s WHERE assembly_operation_id = %s"
        val = (round(0 + r, 2), a)
        cursorObject.execute(sql, val)
        dataBase.commit()


def add_to_ao_materials(ao_name, ao_similar):
    query = """select * from ao_materials where assembly_operation_id = %s"""
    cursorObject.execute(query, (ao_similar,))
    result = cursorObject.fetchall()
    print(" ----- result -----------")
    print(result)
    # insert
    for r in result:
        print("++++++")
        print(r)
        # query = """INSERT INTO ao_materials (assembly_operation_id, material_type, quantity, is_fixed) VALUES
        #  (%s, %s, %s, %s)""", (r[0], animals))
        query = "INSERT INTO ao_materials (assembly_operation_id, material_type, quantity, is_fixed) VALUES (%s, %s," \
                "%s,%s) "
        val = (ao_name, r[1], r[2], r[3])
        cursorObject.execute(query, val)
        dataBase.commit()


def add_to_ao_actors(ao_name, ao_similar):
    query = """select * from ao_actors where assembly_operation_id = %s"""
    cursorObject.execute(query, (ao_similar,))
    result = cursorObject.fetchall()
    print(" ----- result -----------")
    print(result)

    # insert
    for r in result:
        print("++++++")
        print(r)
        # query = """INSERT INTO ao_materials (assembly_operation_id, material_type, quantity, is_fixed) VALUES
        #  (%s, %s, %s, %s)""", (r[0], animals))
        query = "INSERT INTO ao_actors (assembly_operation_id, generic_actor, actor_type,  " \
                "actor_model_file) VALUES (%s, %s,%s,%s)"
        val = (ao_name, r[1], r[2], r[3])
        cursorObject.execute(query, val)
        dataBase.commit()


add_to_ao_materials(ao_name, ao_similar)
add_to_ao_actors(ao_name, ao_similar)



