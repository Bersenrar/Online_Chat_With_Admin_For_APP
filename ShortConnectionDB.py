import time

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


DB_Password = os.environ.get('DATABASE_PASSWORD')


class CreateTables:
    @staticmethod
    def __create_table_messages():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="admin",
                database="chatdatabase",
                autocommit=True
            )
            cursor = conn.cursor()

            # Check if table exist
            cursor.execute("SHOW TABLES LIKE 'MESSAGES';")
            if not cursor.fetchone():
                query_string = '''
                CREATE TABLE MESSAGES (
                    MESSAGE_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                    USER_ID INTEGER,
                    MESSAGE_TXT TEXT,
                    MESSAGE_TIMESTAMP DATETIME,
                    FOREIGN KEY (CHAT_ID) REFERENCES CHATS (CHAT_ID)
                )
                '''
                cursor.execute(query_string)
                print("Table MESSAGES successfully created")
            else:
                print("Table already exist")
        except mysql.connector.Error as err:
            print(f"Error occurred while creating message table\nError message: {err}")
        finally:
            if "conn" in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def insert_message(user_id, message_txt, timestamp):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="admin",
                database="chatdatabase",
                autocommit=True
            )
            cursor = conn.cursor()
            # Receiving chat id by user id from table CHATS
            query_chat_id = "SELECT CHAT_ID FROM CHATS WHERE USER_ID = %s"
            cursor.execute(query_chat_id, (user_id,))
            chat_id = cursor.fetchone()[0]
            # Inserting message into table MESSAGES after getting chat id
            query_insert_message = """
                    INSERT INTO MESSAGES (USER_ID, MESSAGE_TXT, MESSAGE_TIMESTAMP, CHAT_ID) 
                    VALUES (%s, %s, %s, %s)
                    """
            cursor.execute(query_insert_message, (user_id, message_txt, timestamp, chat_id))
            print("Message successfully inserted into MESSAGES table")
        except mysql.connector.Error as err:
            print(f"Something went wrong\nError message: {err}")
        finally:
            if "conn" in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def __create_chats_table():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="admin",
                database="chatdatabase",
                autocommit=True
            )
            cursor = conn.cursor()

            # Check if table exist
            cursor.execute("SHOW TABLES LIKE 'CHATS';")
            if not cursor.fetchone():
                query_string = '''
                CREATE TABLE CHATS (
                CHAT_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                USER_ID INTEGER,
                CHAT_KEY CHAR(50)
                );
                '''
                cursor.execute(query_string)
                print("Table CHATS successfully created")
            else:
                print("Table already exist")
        except mysql.connector.Error as err:
            print(f"Error occurred while creating CHATS table\nError message: {err}")
        finally:
            if "conn" in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def insert_chat(user_id, room_key):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="admin",
                database="chatdatabase",
                autocommit=True
            )
            cursor = conn.cursor()

            # Inserting chat into table CHATS after getting chat id
            query_insert_message = """
                    INSERT INTO CHATS (USER_ID, CHAT_KEY) 
                    VALUES (%s, %s)
                    """
            cursor.execute(query_insert_message, (user_id, room_key))
            print("Chat successfully inserted into CHATS table")
        except mysql.connector.Error as err:
            print(f"Something went wrong\nError message: {err}")
        finally:
            if "conn" in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def __create_tickets_table():
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="admin",
                database="chatdatabase",
                autocommit=True
            )
            cursor = conn.cursor()

            # Check if table exist
            cursor.execute("SHOW TABLES LIKE 'TICKETS';")
            if not cursor.fetchone():
                query_string = '''
                CREATE TABLE TICKETS (
                TICKET_ID INTEGER PRIMARY KEY AUTO_INCREMENT,
                USER_ID INTEGER,
                STATUS CHAR(100)
                );
                '''
                cursor.execute(query_string)
                print("Table TICKETS successfully created")
            else:
                print("Table already exist")
        except mysql.connector.Error as err:
            print(f"Error occurred while creating TICKETS table\nError message: {err}")
        finally:
            if "conn" in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    @staticmethod
    def insert_ticket(user_id, status="Open"):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="admin",
                database="chatdatabase",
                autocommit=True
            )
            cursor = conn.cursor()

            # Inserting ticket into table TICKETS after getting chat id
            query_insert_message = """
                    INSERT INTO TICKETS (USER_ID, STATUS) 
                    VALUES (%s, %s)
                    """
            cursor.execute(query_insert_message, (user_id, status))
            print("Ticket successfully inserted into TICKETS table")
        except mysql.connector.Error as err:
            print(f"Something went wrong\nError message: {err}")
        finally:
            if "conn" in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def create_tables(self):
        self.__create_tickets_table()
        self.__create_chats_table()
        self.__create_table_messages()