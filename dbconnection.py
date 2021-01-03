import psycopg2
from configuration import DATABASE


class Connection:

    def __init__(self, host=None, service=None, user=None, passwd=None):
        self.host = host        
        self.service = service
        self.user = user
        self.passwd = passwd        


    def execute_statement(self, statement):
        mydb = self.connect()
        mycursor = mydb.cursor()
        mycursor.execute(statement)
        mydb.commit()


    def connect(self):  
        mydb = psycopg2.connect(
                host=DATABASE["DB_HOST"],
                database=DATABASE["DB_SERVICE"],
                user=DATABASE["DB_USER"],
                password=DATABASE["DB_PASSWORD"])                      
        return mydb

    #def close(self):
     #   self.mydb.close()
