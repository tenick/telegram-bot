# help resources:
# https://python.gotrained.com/scraping-telegram-group-members-python-telethon/
# https://docs.telethon.dev/
import threading
from telethon import errors
import telethon.errors
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog
from tkinter import messagebox
import asyncio
from functools import partial
import os
import pickle
# User(id=1180268541, is_self=False, contact=True, mutual_contact=True, deleted=False, bot=False,
# bot_chat_history=False, bot_nochats=False, verified=False, restricted=False, min=False, bot_inline_geo=False,
# support=False, scam=False, access_hash=5353402755429568321, first_name='Angelo', last_name=None, username=None,
# phone='639052792476', photo=None,
# status=UserStatusOffline(was_online=datetime.datetime(2020, 5, 3, 20, 29, 25, tzinfo=datetime.timezone.utc)),
# bot_info_version=None, restriction_reason=[], bot_inline_placeholder=None, lang_code=None)


class StartSessionForm:
    def __init__(self, master, parent, new_session):
        self.parent = parent
        self.root = master
        self.new_session = new_session
        width = master.winfo_screenwidth() - round(master.winfo_screenwidth() * 0.7)
        height = master.winfo_screenheight() - round(master.winfo_screenheight() * 0.7)
        x = master.winfo_screenwidth() // 2 - width // 2
        y = master.winfo_screenheight() // 2 - height // 2
        master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        master.configure(bg="#53acdb")
        master.title("Start Session Form")

        self.lbl_font = self.parent.lbl_font
        # Labels
        if new_session:
            lbl_sname = tk.Label(master, bg="#53acdb", fg="white", font=self.lbl_font, text="Session name:")
            lbl_sname.place(relx=0.01, rely=0, relheight=0.15)
            lbl_pnumber = tk.Label(master, bg="#53acdb", fg="white", font=self.lbl_font, text="Phone Number: ")
            lbl_pnumber.place(relx=0.01, rely=0.45, relheight=0.15)
            lbl_code = tk.Label(master, bg="#53acdb", fg="white", font=self.lbl_font, text="Code: ")
            lbl_code.place(relx=0.01, rely=0.6, relheight=0.15)
        else:
            self.lbl_session_file = tk.Label(master, bg="#53acdb", fg="white", font=self.lbl_font)
            self.lbl_session_file.place(relx=0.3, rely=0.45, relheight=0.15)
        lbl_api_id = tk.Label(master, bg="#53acdb", fg="white", font=self.lbl_font, text="API ID: ")
        lbl_api_id.place(relx=0.01, rely=0.15, relheight=0.15)
        lbl_api_hash = tk.Label(master, bg="#53acdb", fg="white", font=self.lbl_font, text="API Hash: ")
        lbl_api_hash.place(relx=0.01, rely=0.3, relheight=0.15)

        # Entries
        if new_session:
            self.entry_sname = tk.Entry(master, font=self.lbl_font)
            self.entry_sname.place(relx=0.3, rely=0, relwidth=0.65, relheight=0.12)
            self.entry_pnumber = tk.Entry(master, font=self.lbl_font)
            self.entry_pnumber.place(relx=0.3, rely=0.45, relwidth=0.45, relheight=0.12)
            self.entry_code = tk.Entry(master, font=self.lbl_font)
            self.entry_code.place(relx=0.3, rely=0.6, relwidth=0.65, relheight=0.12)
        f = open("api_details.txt", "r")
        self.entry_api_id = tk.Entry(master, font=self.lbl_font)
        self.entry_api_id.place(relx=0.3, rely=0.15, relwidth=0.65, relheight=0.12)
        self.entry_api_id.insert(tk.END, f.readline())
        self.entry_api_hash = tk.Entry(master, font=self.lbl_font)
        self.entry_api_hash.place(relx=0.3, rely=0.3, relwidth=0.65, relheight=0.12)
        self.entry_api_hash.insert(tk.END, f.readline())
        f.close()

        # Buttons
        if new_session:
            btn_code = tk.Button(master, text="Send Code", border=0, command=self.authenticate)
            btn_code.place(relx=0.77, rely=0.45, relwidth=0.18, relheight=0.12)
        else:
            btn_open_file = tk.Button(master, text="Open Session File", border=0, command=self.open_file)
            btn_open_file.place(relx=0.01, rely=0.45, relheight=0.12)
        btn_cancel = tk.Button(master, text="Cancel", border=0, command=self.cancel)
        btn_cancel.place(relx=0.15, rely=0.8, relwidth=0.2, relheight=0.12)
        btn_connect = tk.Button(master, text="Connect", border=0, command=self.connect)
        btn_connect.place(relx=0.65, rely=0.8, relwidth=0.2, relheight=0.12)

    def open_file(self):
        file_name = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                               filetypes=(("SESSION Files", ".session"), ("All Files", ".*")))
        self.parent.session_name = file_name[:file_name.find(".session")]
        self.lbl_session_file.configure(text=file_name.split("/")[-1])
        self.root.focus_force()

    def cancel(self):
        if self.parent.client is not None:
            try:
                self.parent.client.log_out()
            except:
                pass
        self.root.destroy()

    def authenticate(self):
        self.parent.session_name = self.entry_sname.get()
        self.parent.api_id = self.entry_api_id.get()
        self.parent.api_hash = self.entry_api_hash.get()
        self.parent.phone_number = self.entry_pnumber.get()
        self.parent.code = self.entry_code.get()
        if os.path.exists(self.parent.session_name + ".session"):
            messagebox.showinfo("Error", "Session already exists.")
            self.root.focus_force()
            return
        if self.parent.session_name == "":
            messagebox.showinfo("Error", "Invalid Session Name")
            self.root.focus_force()
            return
        if self.parent.phone_number == "":
            messagebox.showinfo("Error", "Invalid Phone Number")
            self.root.focus_force()
            return
        try:
            self.parent.client = TelegramClient(self.parent.session_name, int(self.parent.api_id), self.parent.api_hash)
            self.parent.client.connect()
        except:
            messagebox.showinfo("Error", "Invalid API_ID/API_Hash Combination.")
            self.root.focus_force()
            return

        if not self.parent.client.is_user_authorized():
            try:
                self.parent.client.send_code_request(self.parent.phone_number)
                messagebox.showinfo("Success", "Code sent!")
            except errors.PhoneNumberInvalidError:
                messagebox.showinfo("Error", "Phone number is invalid.")
                self.parent.client.log_out()
            except errors.ApiIdInvalidError:
                messagebox.showinfo("Error", "Invalid API_ID/API_Hash Combination.")
                self.parent.client.log_out()
        self.root.focus_force()

    def connect(self):
        if self.new_session:
            try:
                self.parent.code = self.entry_code.get()
                self.parent.client.sign_in(self.parent.phone_number, self.parent.code)
                self.parent.is_authorized = True
                self.parent.me = self.parent.client.get_me()
                messagebox.showinfo("Success", "Successfully connected!")
                self.parent.create_logged_in_gui()
                self.root.destroy()
            except:
                messagebox.showinfo("Error", "Invalid code.")
                self.root.focus_force()
        else:
            try:
                self.parent.api_id = self.entry_api_id.get()
                self.parent.api_hash = self.entry_api_hash.get()
                self.parent.client = TelegramClient(self.parent.session_name, int(self.parent.api_id), self.parent.api_hash)
                self.parent.client.connect()
                if not self.parent.client.is_user_authorized():
                    messagebox.showinfo("Error", "Invalid API_ID/API_Hash Combination.")
                    self.parent.client.log_out()
                    self.root.focus_force()
                else:
                    messagebox.showinfo("Success", "Successfully connected!")
                    self.parent.me = self.parent.client.get_me()
                    self.parent.is_authorized = True
                    self.parent.create_logged_in_gui()
                    self.root.destroy()
            except:
                messagebox.showinfo("Error", "Invalid API_ID/API_Hash Combination.")
                self.root.focus_force()


class TelegramUser:
    def __init__(self, username, phone, first_name, last_name):
        self.username = username
        self.phone = phone
        self.first_name = first_name
        self.last_name = last_name


class TelegramUserBot:
    def __init__(self, master):
        self.root = master
        self.client = None
        self.me = None
        self.session_name = ""
        self.api_id = 0
        self.api_hash = ""
        self.phone_number = ""
        self.code = ""
        self.is_authorized = False
        self.telegram_loop = asyncio.get_event_loop()
        self.groups = {}
        self.members = {}
        self.cancel_msg_send = False
        try:
            self.members = self.load_obj("contacted_members")
        except FileNotFoundError:
            pass
        self.files = []
        print(self.members)

        width = master.winfo_screenwidth() - round(master.winfo_screenwidth() * 0.5)
        height = master.winfo_screenheight() - round(master.winfo_screenheight() * 0.1)
        x = master.winfo_screenwidth() // 2 - width // 2
        y = master.winfo_screenheight() // 2 - height // 2
        master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        master.configure(bg="#53acdb")
        master.title("Telegram User Bot")

        self.lbl_font = tkFont.Font(family='Helvetica', size=20)
        self.others_font = tkFont.Font(family='Helvetica', size=15)
        # log in frame
        self.login_frame = tk.Frame(master, bg="#e6e9ed")
        self.login_frame.place(relwidth=0.9, relheight=0.1, relx=0.05, rely=0.05)
        self.btn = tk.Button(self.login_frame, text="Create New Session", font=self.lbl_font, border=0, bg="#e6e9ed",
                             command=lambda: self.create_session(True))
        self.btn.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        self.btn2 = tk.Button(self.login_frame, text="Use Existing Session", font=self.lbl_font, border=0, bg="#e6e9ed",
                              command=lambda: self.create_session(False))
        self.btn2.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)

        # logged in frame
        self.logged_in_frame = tk.Frame(master, bg="#e6e9ed")
        self.lbl_greetings = tk.Label(self.logged_in_frame, font=self.lbl_font, bg="#e6e9ed", text="")
        self.lbl_greetings.place(relx=0.05, rely=0.3)

        # remaining gui parts
        # target group
        self.lbl_target_group = tk.Label(master, font=self.others_font, text="Target Group: ")
        self.lbl_target_group.place(relx=0.05, rely=0.2, relwidth=0.14)
        self.entry_target_group = tk.Entry(master, font=self.others_font, text="")
        self.entry_target_group.place(relx=0.2, rely=0.2, relwidth=0.4)

        # group list
        self.btn_group_list = tk.Button(master, font=self.others_font, text="Get Group List", command=lambda: self.start_thread(self.get_group_list))
        self.btn_group_list.place(relx=0.65, rely=0.2)
        self.group_list = tk.Text(master)
        self.group_list.place(relx=0.65, rely=0.25, relwidth=0.3, relheight=0.7)

        # contacted users
        self.option = tk.StringVar()
        self.lbl_contacted_users = tk.Label(master, font=self.others_font, text="Contacted users contact again?")
        self.lbl_contacted_users.place(relx=0.05, rely=0.3)
        self.rbtn_contacted_users1 = tk.Radiobutton(master, font=self.others_font, text="Yes", value=True, var=self.option)
        self.rbtn_contacted_users1.place(relx=0.4, rely=0.3)
        self.rbtn_contacted_users2 = tk.Radiobutton(master, font=self.others_font, text="No", value=False, var=self.option)
        self.rbtn_contacted_users2.place(relx=0.5, rely=0.3)
        self.rbtn_contacted_users2.invoke()

        # add image
        self.btn_add_img = tk.Button(master, font=self.others_font, text="Add Files", command=self.open_file)
        self.btn_add_img.place(relx=0.05, rely=0.45)
        self.lbl_add_img = tk.Label(master, text="")
        self.lbl_add_img.place(relx=0.17, rely=0.46)
        self.btn_clear_files = tk.Button(master, font=self.others_font, text="Clear Files", command=self.clear_file)
        self.btn_clear_files.place(relx=0.05, rely=0.4)

        # message area
        self.message_box = tk.Text(master, font=self.others_font)
        self.message_box.place(relx=0.05, rely=0.5, relheight=0.4, relwidth=0.55)
        self.btn_send_msg = tk.Button(master, font=self.others_font, text="Send Message", command=lambda: self.start_thread(self.send_msg))
        self.btn_send_msg.place(relx=0.45, rely=0.91)
        self.btn_cancel_sending = tk.Button(master, text="Cancel", state=tk.DISABLED, command=self.cancel_sending)
        self.btn_cancel_sending.place(relx=0.36, rely=0.91, relwidth=0.08)

        # message timeout
        self.lbl_msg_delay = tk.Label(master, text="Send delay: ")
        self.lbl_msg_delay.place(relx=0.05, rely=0.91, relwidth=0.07)
        self.entry_msg_delay = tk.Entry(master)
        self.entry_msg_delay.place(relx=0.13, rely=0.91, relwidth=0.05)
        self.entry_msg_delay.insert(tk.END, "120")

    def cancel_sending(self):
        self.cancel_msg_send = True
        self.btn_cancel_sending["state"] = tk.DISABLED
        self.btn_cancel_sending["text"] = "Cancelling..."
        messagebox.showinfo("", "Will cancel in less than {} seconds".format(self.entry_msg_delay.get()))

    def clear_file(self):
        self.files.clear()
        self.lbl_add_img.config(text='')

    def open_file(self):
        file_name = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                               filetypes=(("All Files", ".*"), ("All Files", ".*")))
        self.files.append(file_name)
        self.lbl_add_img.config(text=', '.join([x.split("/")[-1] for x in self.files]))
        self.root.focus_force()

    def save_obj(self, obj, name):
        with open(name + '.pkl', 'wb') as f:  # 'obj/' +
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

    def load_obj(self, name): # BRB
        with open(name + '.pkl', 'rb') as f:
            return pickle.load(f)

    # peerflooderror current problem, fix: probably just need to add sleep, test for each seconds
    async def send_msg(self):
        try:
            self.btn_send_msg["state"] = tk.DISABLED
            self.btn_cancel_sending["state"] = tk.NORMAL
            self.btn_send_msg["text"] = "Sending..."
            self.message_box["state"] = tk.DISABLED
            if self.message_box.get("1.0", "end-1c").strip() == "":
                1/0
            all_participants = await self.client.get_participants(entity=int(self.entry_target_group.get()), aggressive=True)
            count = 0
            for user in all_participants:
                if user.id not in self.members or int(self.option.get()):  # self.option.get() = contact users contacted last time?
                    count += 1
                    self.members[user.id] = TelegramUser(user.username, user.phone, user.first_name, user.last_name)
                    await self.client.send_message(user, self.message_box.get("1.0", "end-1c"))
                    for file_path in self.files:
                        await self.client.send_file(user, file_path)
                    print(str(count)+".", user.id, "sent")
                    await asyncio.sleep(float(self.entry_msg_delay.get()))
                if self.cancel_msg_send:
                    self.cancel_msg_send = False
                    break
        except AttributeError:
            messagebox.showinfo("Error", "Please login first.")
        except ZeroDivisionError:
            messagebox.showinfo("Error", "Message can't be empty unless a file is provided.")
        except ValueError:
            messagebox.showinfo("Error", "Please input a valid ID")
        except telethon.errors.PeerFloodError as e:
            messagebox.showinfo("Error", "Must wait {} seconds".format(e))
        self.save_obj(self.members, "contacted_members")
        self.btn_send_msg["state"] = tk.NORMAL
        self.btn_cancel_sending["state"] = tk.DISABLED
        self.btn_cancel_sending["text"] = "Cancel"
        self.btn_send_msg["text"] = "Send Message"
        self.message_box["state"] = tk.NORMAL

    async def get_group_list(self):
        try:
            self.btn_group_list["state"] = tk.DISABLED
            self.btn_group_list["text"] = "Getting Groups..."
            self.group_list.delete(1.0, tk.END)
            for x in await self.client.get_dialogs():
                await asyncio.sleep(0.1)
                if x.is_group or x.is_channel:
                    group_name = ''.join([y for y in x.name if y.isalnum() or y == ' '])+": {}".format(str(x.id))
                    self.groups[group_name] = x.id
                    temp_btn = tk.Button(self.group_list, text=group_name, command=partial(self.select_group, group_name))
                    self.group_list.window_create(tk.INSERT, window=temp_btn)
                    self.group_list.insert(tk.END, "\n")
            print("Done getting group list!")
        except AttributeError:
            messagebox.showinfo("Error", "Please login first.")

        self.btn_group_list["state"] = tk.NORMAL
        self.btn_group_list["text"] = "Get Group List"

    def select_group(self, id):
        self.entry_target_group.delete(0, tk.END)
        self.entry_target_group.insert(0, "")
        self.entry_target_group.insert(tk.END, self.groups.get(id))

    async def loading_label(self):
        loading_label = tk.Label(self.root, text="Loading", fg="white", bg="red")
        loading_label.place(relx=0.7, rely=0.25, relwidth=0.3, relheight=0.7)
        count = 0
        while self.telegram_loop.is_running():
            await asyncio.sleep(0.5)
            count += 1
            if count % 4 == 0:
                count = 0
            loading_label.config(text="Loading"+"."*count)
        loading_label.pack_forget()

    def create_logged_in_gui(self):
        self.login_frame.place_forget()
        self.logged_in_frame.place(relwidth=0.9, relheight=0.1, relx=0.05, rely=0.05)
        self.lbl_greetings.config(text="Welcome, {}!".format(self.me.username))

    def create_session(self, is_new_session):
        if os.path.exists("api_details.txt"):
            StartSessionForm(tk.Tk(), self, is_new_session)
        else:
            messagebox.showinfo("File is missing", "api_details.txt is missing, please make one and add your api details there")

    def start_thread(self, func):
        threading.Thread(target=self.start_telegram_loop, args=(func,)).start()

    def stop_telegram_loop(self):
        self.telegram_loop.stop()

    def start_telegram_loop(self, func):
        #self.telegram_loop.create_task(func())
        #if not self.telegram_loop.is_running():
        self.telegram_loop.run_until_complete(func())

    async def connect(self):  # reference function
        await self.client.connect()
        if not self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))
        else:
            self.main()

    def main(self):  # reference function
        print(self.client.is_user_authorized())
        # You can print all the dialogs/conversations that you are part of:
        for dialog in self.client.iter_dialogs():
            print(dialog.name, 'has ID', dialog.id)

        # You can send messages to yourself...
        self.client.send_message('me', 'Hello, myself!')
        # ...or even to any username
        # await client.send_message('Fiqire96', 'Hello, Fiqire96!')

        chats = []
        last_date = None
        chunk_size = 200
        groups = []

        result = self.client(GetDialogsRequest(
            offset_date=last_date,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=chunk_size,
            hash=0
        ))
        chats.extend(result.chats)

        for chat in chats:
            try:
                if chat.megagroup == True:
                    groups.append(chat)
            except:
                continue

        print('Choose a group to scrape members from:')
        i = 0
        for g in groups:
            print(str(i) + '- ' + g.title)
            i += 1

        g_index = input("Enter a Number: ")
        target_group = groups[int(g_index)]

        all_participants = []
        all_participants = self.client.get_participants(entity=target_group, aggressive=True)
        for x in all_participants:
            print(x.id)
        print(len(all_participants))

        # Or send files, songs, documents, albums...
        self.client.send_file('me', r'C:\Users\Kenneth\Desktop\Untitled2.png')
        # await client.log_out() # deletes session file


root = tk.Tk()
user_bot = TelegramUserBot(root)
root.mainloop()