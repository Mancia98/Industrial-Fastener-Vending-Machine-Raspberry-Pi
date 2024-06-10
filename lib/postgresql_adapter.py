import psycopg2
from psycopg2 import Error


class Data_Base_Connection:
    def __init__(self, user, password, database, host, port = "5432", sslmode=None, sslcert=None, sslkey=None, sslrootcert=None):
        self.log = ""
        self.connection_status = False
        self.__user = user
        self.__password = password
        self.__database = database
        self.__host = host
        self.__port = port
        self.__sslmode = sslmode
        self.__sslcert = sslcert
        self.__sslkey = sslkey
        self.__sslrootcert = sslrootcert

    def connect(self) -> bool:
        self.connection_status = False
        try:
            connection_params = {
                "user": self.__user,
                "password": self.__password,
                "host": self.__host,
                "port": self.__port,
                "database": self.__database
            }

            if self.__sslmode:
                connection_params["sslmode"] = self.__sslmode
            if self.__sslcert:
                connection_params["sslcert"] = self.__sslcert
            if self.__sslkey:
                connection_params["sslkey"] = self.__sslkey
            if self.__sslrootcert:
                connection_params["sslrootcert"] = self.__sslrootcert

            # # Connect to your PostgreSQL server
            # self.connection = psycopg2.connect(user=self.__user, password=self.__password, host=self.__host, port=self.__port, database=self.__database)
            self.connection = psycopg2.connect(**connection_params)
            cursor = self.connection.cursor()
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            self.log = (f"PostgreSQL connection at {self.__host} | Connected to {record}")
            self.connection_status = True
            cursor.close()
            return self.connection_status

        except (Exception, Error) as error:
            self.log = (f"Error while connecting to PostgreSQL with error: {error}")
            self.connection_status = False
            return self.connection_status

        # finally:
        #     if self.connection:
        #         # Close the connection
        #         cursor.close()
        #         # self.connection.close()
        #         # print("PostgreSQL connection is closed")

    def query(self, query_statement) -> list:
        self.log = "Called Query Routine"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query_statement)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except (Exception, Error) as error:
            self.log  = (f"Error while query to PostgreSQL with error: {error}")
            return []
    
    def insert(self, insert_statements:list) -> bool:
        self.log = "Called Insert Routine"
        
        # Ensure insert_statements is a list
        if isinstance(insert_statements, str):
            insert_statements = [insert_statements]

        try:
            cursor = self.connection.cursor()
            for statement in insert_statements:
                cursor.execute(statement)
            self.connection.commit()
            cursor.close()
            return True
        except (Exception, Error) as error:
            self.log = f"Error while executing batch insert to PostgreSQL with error: {error}"
            try:
                self.connection.rollback()
                cursor.close()
            except:
                pass
            return False

    def disconnect(self):
        try:
            self.connection.close()
            self.log = "PostgreSQL Disconnected"
            self.connection_status = False
        except (Exception, Error) as error:
             self.log  = (f"Error while disconnection to PostgreSQL with error: {error}")  
        



# cn = Data_Base_Connection("client","password", "vending-machine", "35.221.157.72")
# cn.connect()
# print(cn.log)
# print(cn.query("SELECT * FROM tbl_inventory_live"))
# print(cn.log)


# insert_query = """
#         INSERT INTO TBL_TRANSACTION_RECORD VALUES (
#             TO_TIMESTAMP('20240526-160035', 'YYYYMMDD-HH24MISS'), 
#             'ALLEN BOLTS SET 1', 
#             '3 mm x 1', 
#             50, 
#             1, 
#             '3', 
#             50, 
#             0, 
#             'GCASH', 
#             'SUCCESS', 
#             4, 
#             'MPH-LT-A69517', 
#             '10.164.46.200', 
#             '58.69.36.155'
#         );
#         """
# if not cn.insert(insert_query):
#     print(cn.log)

# print(cn.query("SELECT * FROM TBL_TRANSACTION_RECORD;"))
    
