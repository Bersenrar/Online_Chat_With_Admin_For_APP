import time

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
import datetime

from DatabaseCreator import Database, DB_Password, TableChats, TableTickets, TableMessages

app = Flask(__name__)
app.config["SECRET_KEY"] = "fgdsgfsdASRWEbv"
socketio = SocketIO(app)

db = Database("localhost", DB_Password, "admin", "chatdatabase")
db.connect()

table_chats = TableChats(db)
table_chats.create_table()

table_messages = TableMessages(db)
table_messages.create_table()

table_tickets = TableTickets(db)
table_tickets.create_table()

user_id_counter = 1
ticket_id_counter = 1
key_len = 4
# chats = []
tickets = []
existing_keys = []


def generate_user_room_key():
    global key_len
    while True:
        key = ""
        for _ in range(key_len):
            key = key + random.choice(ascii_uppercase)
        if key not in existing_keys:
            existing_keys.append(key)
            return key


@app.route("/", methods=["GET", "POST"])
def user_start_page():
    session["chat_status"] = False
    if request.method == "POST" and not session.get("chat_status", default=False):
        global user_id_counter, ticket_id_counter

        user_message = request.form.get("user_message")
        if not user_message:
            return render_template("user_page.html", error="Enter Your request to administrator")

        print(f"Current user id is: {user_id_counter}\nUser Message: {user_message}")

        room_key = generate_user_room_key()

        session["room"] = room_key
        session["user_id"] = user_id_counter
        session["name"] = f"User_{user_id_counter}"

        table_chats.insert_chat(user_id=user_id_counter, room_key=room_key)
        table_messages.insert_message(user_id=user_id_counter, message_txt=user_message,
                                      timestamp=datetime.datetime.now().isoformat(), name="User", chat_key=room_key)
        table_tickets.insert_ticket(user_id=user_id_counter)

        user_id_counter += 1
        return redirect(url_for("chat_with_admin"))

    return render_template("user_page.html")


@app.route("/chat")
def chat_with_admin():
    return render_template("chat.html")


@app.route("/admin_page")
def admin_start_page():
    session["admin"] = True
    session["name"] = "Admin"
    session["user_id"] = -1
    database_response = table_chats.get_all_chats()
    chats = [{"chat_id": chat[0], "user_id": chat[1], "room_key": chat[2]} for chat in database_response]
    return render_template("admin_chat_list.html", chats=chats)  # Render a different template that lists all chats


@app.route("/admin_page/chat/<chat_id>")
def admin_chat_page(chat_id):
    session["room"] = chat_id
    return render_template("chat.html")


@socketio.on("message")
def handle_message(data):
    room = session.get("room")
    if room not in existing_keys:
        return
    content = {
        "name": session.get("name"),
        "message": data["data"],
        "date": datetime.datetime.now().isoformat()
    }
    print(content)
    send(content, to=room)
    table_messages.insert_message(user_id=session["user_id"], message_txt=content["message"],
                                  timestamp=content["date"], name=content["name"], chat_key=room)


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")

    join_room(room)
    send({"name": name, "message": "Connected in chat", "date": datetime.datetime.now().isoformat()}, to=room)
    print(f"{name} has joined the room {room}")

    chat_key = table_chats.get_chat_by_key(room)
    print(chat_key)
    if chat_key:
        chat_messages = table_messages.get_all_messages_by_chat_id(chat_key[2])
        print(chat_messages)
        if chat_messages:
            for message in chat_messages:
                print(message)
                send({
                    "name": message[1],
                    "message": message[3],
                    "date": message[4].strftime('%Y-%m-%d %H:%M:%S')},
                    to=room)


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", allow_unsafe_werkzeug=True)
