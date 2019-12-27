from flask import Flask
import sys
import sqlite3,csv
import os
from tabulate import tabulate

class DB:
    """Class for creating an SQLite database in the same dir of this app file.
    Loads data from tasks_data.csv in the given path to tasks table.
    Retrieves data from tasks table
    """
    def __init__(self):
        self.sdb = None
        self.cur = None

    def connect(self):
        """Connect to tasks db """
        try:        
            curpath = os.path.abspath(sys.modules[DB.__module__].__file__)
            os.chdir(os.path.dirname(curpath))
            self.sdb = sqlite3.connect("tasks.db")
            self.cur = self.sdb.cursor()
            print("connected")
        except Exception as e:
            print(e)
    
    def disconnect(self):
        """Commit Changes to tasks db and close connection"""
        try:
            self.sdb.commit()
            self.cur.close()
            self.sdb.close()
        except Exception as e:
            print(e)
            
    def load_data(self,filepath):
        """Load Data in the given csv file to tasks table.
        SQLite is used, so that database setup is simple,.
        Disadvantage of SQLite
            More than 15 precision is not supported, so stored as text. 
            Milliseconds in timestamp  not supported, so stored as text.
        """
        try:
            self.connect()
            print("Create Table")
            self.cur.execute(f"drop table if exists tasks")
            self.cur.execute(f"create table tasks(id INT,timestamp text,temperature text,duration text)")
            print("Load data from csv to table - Iterative manner")
            with open(f'{filepath}','r') as fl: 
                dict_file = csv.DictReader(fl)
                lt_rows = [(row['id'], row['timestamp'], row['temperature'], row['duration']) for row in dict_file]
            
            self.cur.executemany("insert into tasks VALUES (?, ?, ? , ?);", lt_rows)
            print("Create log table")
            self.cur.execute(f"drop table if exists requests")
            self.cur.execute("create table requests(id INTEGER primary key, req_time DATETIME DEFAULT CURRENT_TIMESTAMP,req varchar(10))")
            self.cur.execute("select count(*) from tasks")
            rowscount = self.cur.fetchone()[0]
            print(f"Load finished. Records count:{rowscount}")
            self.disconnect()
            return rowscount 
        except Exception as e:
            print(e)
    
    def get_taskdata(self):
        """Return task data in html format.
        Add request record to requests table
        """
        try:
            print("get")
            self.connect()
            self.cur.execute("select * from tasks")
            data = self.cur.fetchall()
            data.insert(0,('id','timestamp','temperature','duration'))
            data = tabulate(data, tablefmt='html')
            
            style = "<style>table td{border: 1px solid #999999;}</style>"

            self.cur.execute("insert into requests(req) values ('All')")
            requests = self.cur.execute("select count(*) from requests").fetchone()[0]
            request_number = f"Request Number : {requests}"
            
            data = style + "</br>" + request_number + "</br>" + data
            self.disconnect()
            return data
        except Exception as e:
            print(e)
            return(f"Error occurred: {str(e)}</br>Please check if load_data is run.")
        
        

#Flask app starts
#Not using ajax/jquery/html/js templates to avoid complexity
app = Flask(__name__)


@app.route('/')
def main():
    return """<a href="/get_taskdata">View Data<a>"""

@app.route('/get_taskdata', methods=['GET'])
def get_taskdata():
    """Return data from tasks in html format
    """
    db = DB()
    data = db.get_taskdata()
    html ='<b>Tasks Data</b>'
    html += data
    return(html)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
        