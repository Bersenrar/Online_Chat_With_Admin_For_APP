import time

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


DB_Password = os.environ.get('DATABASE_PASSWORD')


class Database:
    def __init__(self, host: str, password: str, user: str, database_name: str, autocommit: bool = True, max_retrieves: int = 3, max_waiting_time: int = 1):
        self.database_name = database_name
        self.host = host
        self.user = user
        self.password = password
        self.autocommit = autocommit

        self.waiting_time = max_waiting_time
        self.max_retrieves = max_retrieves

        self.conn = None
        self.cursor = None

        self.connect()

    def connect(self):
        if not self.conn or not self.conn.is_connected():
            try:
                self.conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    database=self.database_name,
                    autocommit=self.autocommit,
                    password=self.password
                )
                self.cursor = self.conn.cursor()
                print(f"Connection to database: {self.database_name} successful")
            except mysql.connector.Error as err:
                print("Something went wrong trying to reconnect: ", err)
                self.reconnect_to_database()

    def drop_tables(self):
        try:
            self.cursor.execute("DROP TABLE MESSAGES;")
            self.cursor.execute("DROP TABLE CHATS;")
            self.cursor.execute("DROP TABLE TICKETS;")
        except Exception as err:
            print("Something went wrong while drop tables ", err)

    def reconnect_to_database(self):
        counter = 0
        while counter < self.max_retrieves:
            try:
                self.conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    database=self.database_name,
                    autocommit=self.autocommit,
                    password=self.password
                )
                self.cursor = self.conn.cursor()
                print(f"Connection to database: {self.database_name} successful")
            except mysql.connector.Error as err:
                print("Something went wrong trying to reconnect")
                time.sleep(self.waiting_time ** counter)
            counter += 1

    def disconnect(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as err:
            print("Something went wrong")


class TableMessages:
    def __init__(self, database: Database):
        self.db = database
        self.cursor = self.db.cursor

    def create_table(self):
        try:
            self.cursor.execute("SHOW TABLES LIKE 'MESSAGES';")
            if not self.cursor.fetchone():
                query_string = '''
                                CREATE TABLE MESSAGES (
                                    MESSAGE_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                                    NAME CHAR(20),
                                    USER_ID INTEGER,
                                    MESSAGE_TXT TEXT,
                                    MESSAGE_TIMESTAMP DATETIME,
                                    CHAT_ID INTEGER,
                                    FOREIGN KEY (CHAT_ID) REFERENCES CHATS (CHAT_ID)
                                )
                                '''
                self.cursor.execute(query_string)
                print("Table MESSAGES successfully created")
            else:
                print("Table already exists")
        except Exception as err:
            print(f"Something went wrong while creating table: {err}")
            self.db.connect()

    def get_all_messages_by_chat_id(self, room):
        try:
            query_chat_id = '''
            SELECT CHAT_ID FROM CHATS WHERE USER_ID=(%s);
            '''
            self.cursor.execute(query_chat_id, (room,))
            chat_id = self.cursor.fetchone()[0]
            query = '''
            SELECT * FROM MESSAGES WHERE CHAT_ID=(%s);
            '''
            self.cursor.execute(query, (chat_id,))
            return self.cursor.fetchall()
        except Exception as err:
            print(f"Something went wrong while inserting chat to database\nError: {err}")
            self.db.connect()

    def insert_message(self, user_id, message_txt, timestamp, name, room):
        try:
            # Receiving chat id by user id from table CHATS
            query_chat_id = "SELECT CHAT_ID FROM CHATS WHERE USER_ID=(%s)"
            self.cursor.execute(query_chat_id, (room,))
            chat_id = self.cursor.fetchone()[0]
            # Inserting message into table MESSAGES after getting chat id
            print(chat_id)
            query_insert_message = """
                            INSERT INTO MESSAGES (USER_ID, MESSAGE_TXT, MESSAGE_TIMESTAMP, CHAT_ID, NAME) 
                            VALUES (%s, %s, %s, %s, %s)
                            """
            self.cursor.execute(query_insert_message, (user_id, message_txt, timestamp, chat_id, name))
            print("Message successfully inserted into MESSAGES table")
        except Exception as err:
            print(f"Something went wrong while inserting message to database\nError: {err}")
            self.db.connect()


class TableChats:
    def __init__(self, database: Database):
        self.db = database
        self.cursor = self.db.cursor

    def create_table(self):
        try:
            self.cursor.execute("SHOW TABLES LIKE 'CHATS';")
            if not self.cursor.fetchone():
                query_string = '''
                                CREATE TABLE CHATS (
                                CHAT_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                                USER_ID INTEGER
                                );
                                '''
                self.cursor.execute(query_string)
                print("Table CHATS successfully created")
            else:
                print("Table CHATS already exists")
        except Exception as err:
            print(f"Something went wrong while creating table: {err}")
            self.db.connect()

    def get_all_chats(self):
        try:
            query = '''
            SELECT * FROM CHATS;
            '''
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as err:
            print(f"Something went wrong while inserting chat to database\nError: {err}")
            self.db.connect()

    def get_chat_by_key(self, room_key):
        try:
            query = '''
            SELECT * FROM CHATS WHERE USER_ID=(%s);
            '''
            self.cursor.execute(query, (room_key,))
            return self.cursor.fetchone()
        except Exception as err:
            print(f"Something went wrong while inserting chat to database\nError: {err}")
            self.db.connect()

    def insert_chat(self, user_id):
        try:
            # Inserting chat into table CHATS
            query_insert_message = """
                                INSERT INTO CHATS (USER_ID) 
                                VALUES (%s);
                                """
            self.cursor.execute(query_insert_message, (user_id,))
            print("Chat successfully inserted into CHATS table")
        except Exception as err:
            print(f"Something went wrong while inserting chat to database\nError: {err}")
            self.db.connect()

    def delete_empty_chats(self):
        try:
            # Select chat IDs with less than 2 messages using a LEFT JOIN
            self.cursor.execute(
                "SELECT DISTINCT CHATS.CHAT_ID FROM CHATS LEFT JOIN MESSAGES ON CHATS.CHAT_ID = MESSAGES.CHAT_ID GROUP BY CHATS.CHAT_ID HAVING COUNT(MESSAGES.CHAT_ID) < 2")
            chats_to_delete = self.cursor.fetchall()

            print("Chats to delete:", chats_to_delete)

            # Create a temporary table to store chat IDs
            self.cursor.execute("CREATE TEMPORARY TABLE TempChatsToDelete (CHAT_ID INT)")

            # Insert chat IDs to be deleted into the temporary table
            for chat_id in chats_to_delete:
                self.cursor.execute(f"INSERT INTO TempChatsToDelete (CHAT_ID) VALUES ({chat_id[0]})")

            # Delete messages for selected chat IDs if there are fewer than 2 messages
            self.cursor.execute("DELETE FROM MESSAGES WHERE CHAT_ID IN (SELECT CHAT_ID FROM TempChatsToDelete)")

            # Delete chats with less than 2 messages
            self.cursor.execute("DELETE FROM CHATS WHERE CHAT_ID IN (SELECT CHAT_ID FROM TempChatsToDelete)")

            # Drop the temporary table
            self.cursor.execute("DROP TEMPORARY TABLE IF EXISTS TempChatsToDelete")

            print("Chats with less than 2 messages deleted successfully.")
        except Exception as err:
            print(f"Something went wrong while inserting chat to database\nError: {err}")
            self.db.connect()


class TableTickets:
    def __init__(self, database: Database):
        self.db = database
        self.cursor = self.db.cursor

    def create_table(self):
        try:
            # Check if table exist
            self.cursor.execute("SHOW TABLES LIKE 'TICKETS';")
            if not self.cursor.fetchone():
                query_string = '''
                CREATE TABLE TICKETS (
                TICKET_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                USER_ID INTEGER,
                STATUS CHAR(100)
                );
                '''
                self.cursor.execute(query_string)
                print("Table TICKETS successfully created")
            else:
                print("Table already exist")
        except Exception as err:
            print(f"Something went wrong while inserting chat to database\nError: {err}")
            self.db.connect()

    def insert_ticket(self, user_id, status="Open"):
        try:
            # Inserting chat into table CHATS
            query_insert_message = """
                                INSERT INTO TICKETS (USER_ID, STATUS) 
                                VALUES (%s, %s)
                                """
            self.cursor.execute(query_insert_message, (user_id, status))
            print("Ticket successfully inserted into TICKETS table")
        except Exception as err:
            print(f"Something went wrong while inserting chat to database\nError: {err}")
            self.db.connect()

