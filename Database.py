import sqlite3 as sql
import sqlite3
import datetime

def database():
    conn = sql.connect("database.db")
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM datas")
        conn.commit()
        c.close()
        return True
    except sql.OperationalError:
        c.execute("CREATE TABLE datas(id INTEGER PRIMARY KEY AUTOINCREMENT,userinput varchar(255),userresponse varchar(255),date varchar(255))")
        conn.commit()
        c.close()
        return False

def updatedatabase(userinput,userresponse):
    conn=sql.connect("database.db")
    c=conn.cursor()
    c.execute("INSERT INTO datas(userinput,userresponse,date) VALUES(?,?,?);",(userinput,userresponse,datetime.date.today(),))
    conn.commit()
    c.close()

def get_update():
    result=database()
    if result==True:
        conn = sql.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT userinput,userresponse FROM datas")
        ans=c.fetchall()
        inputs,res=[],[]
        for i in ans:
            inputs.append(i[0])
            res.append(i[1])
        c.close()
        return inputs,res

