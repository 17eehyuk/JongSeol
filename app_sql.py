from traceback import print_tb
import pymysql

#나중에 AWS 연동시키기
mydb = pymysql.connect(
    user='jongseol', 
    passwd='1234',
    host='localhost',
    charset='utf8'
)

sql_cursor = mydb.cursor(pymysql.cursors.DictCursor)

# #DB생성(jongsul)
# sql_cursor.execute('CREATE DATABASE jongseol;')

# #모든 DB보기
# def print_all_db():
#     sql_cursor.execute('SHOW DATABASES;')
#     for db in sql_cursor:
#         print(db)

def fetchall_data(sql_table_name):
    command = f'''SELECT * FROM jongseol.{sql_table_name};'''
    sql_cursor.execute(command)
    return sql_cursor.fetchall()


def clear_table_data(sql_table_name):
    command = f'''DELETE FROM jongseol.{sql_table_name}'''
    sql_cursor.execute(command)
    mydb.commit()
    print('초기화완료')

def insert_datas(sql_table_name, datas):
    command = f'''INSERT INTO jongseol.{sql_table_name} VALUES {datas}'''
    sql_cursor.execute(command)
    mydb.commit()
    print('삽입성공')
