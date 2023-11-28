from tkinter.simpledialog import askstring
from tkinter.messagebox import showerror, showinfo,askyesno
from tkinter.ttk import Treeview, Style
from tkinter import *
from datetime import date
from cryptography.fernet import Fernet
import pandas as pd
import random
import math
import hashlib


def clear_frame(frame_name):
    for widgets in frame_name.winfo_children():
        widgets.destroy()


def add_page():

    def add_data():
        website_data = website.get()
        password_data = password.get()
        username_data = username.get()

        verified = askyesno('Verify info',f'Please verify this data\n'
                                        f'website: {website_data}\n'
                                        f'username: {username_data}\n'
                                        f'password: {password_data}')
        if verified:
            global data_file
            if website_data != "" and username_data != "" and password_data != "":
                data = pd.DataFrame({'website': [website_data],
                                     'username': [username_data],
                                     'password': [CRYPTO.encrypt(password_data.encode()).decode()],
                                     'last update': [date.today().strftime("%d/%m/%Y")]})
                data.index = [len(data_file)]
                data_file = pd.concat([data_file, data], ignore_index=False)
                data_file.to_csv(path_or_buf=f"{RESOURCE_PATH}/passwordmanager.csv", mode="w", header=True, index=False)
                website.delete(0, END)
                username.delete(0, END)
                password.delete(0, END)
                error_label.config(text="Successfully added", fg="green", padx=20)
            else:
                error_label.config(text="Values cant be empty", fg="red", padx=0)

    def generate_password():
        password_generated = []
        chars = [*'abcdefghijklmnopqrstvuwxyzABCDEFGHIJKLMNOPQRSTVUWXYZ!@#$%1234567890']
        for n in range(0, 24):
            password_generated.append(random.choice(chars))
        password.insert(0, "".join(password_generated))

    clear_frame(window)

    small_logo = Canvas(width=200, height=189, highlightthickness=0)
    small_logo.create_image(100, 100, image=LOGO_IMAGE)
    small_logo.pack(pady=20)

    main_frame = Frame(window, borderwidth=10)
    main_frame.rowconfigure(0, weight=1, pad=35)
    main_frame.rowconfigure(1, weight=1, pad=35)
    main_frame.rowconfigure(2, weight=1, pad=30)
    main_frame.pack()

    error_label = Label(text="", font=("ariel", 15))
    error_label.place(x=260, y=210)

    website_label = Label(main_frame, text="Website:")
    website_label.grid(column=0, row=0)

    website = Entry(main_frame, width=40)
    website.grid(column=1, row=0)

    username_label = Label(main_frame, text="Email/Username:")
    username_label.grid(column=0, row=1)

    username = Entry(main_frame, width=40)
    username.grid(column=1, row=1)

    password_label = Label(main_frame, text="Password:")
    password_label.grid(column=0, row=2, padx=30)

    password = Entry(main_frame, width=30)
    password.grid(column=1, row=2, sticky=W)

    generate_password_button = Button(main_frame, text="Generate", borderwidth=0, fg=MAIN_WHITE, bg=MAIN_COLOR,
                                      activeforeground=MAIN_COLOR, activebackground=MAIN_WHITE, command=generate_password)
    generate_password_button.grid(column=1, row=2, sticky=E)

    add_button = Button(main_frame, text="ADD", width=50, borderwidth=0,
                        fg=MAIN_WHITE, bg=MAIN_COLOR, activeforeground=MAIN_COLOR, activebackground=MAIN_WHITE,
                        command=add_data)
    add_button.grid(columnspan=2, rowspan=3, pady=20, sticky=E)

    return_button = Button(image=RETURN_IMAGE, borderwidth=0, command=main_page)
    return_button.place(x=10, y=10)

    window.mainloop()


def motion(event):
    if event.char == 'a':
        print(f"X: {event.x}, Y: {event.y}")


def admin_verify():
    while True:
        inserted_password = askstring('Admin verify', 'Enter admin password')
        if inserted_password is not None:
            hashed = hashlib.sha256(inserted_password.encode()).hexdigest()
            if hashed == ADMIN_PASS:
                showinfo('Success', 'Admin successfully verified')
                return True
            else:
                showerror('Failure', 'Wrong password')
        else:
            return False


def display_page():
    if admin_verify():
        def last_page(rows):
            if rows[0] != 0:
                rows[0] -= ROWS_PER_PAGE
                rows[1] -= ROWS_PER_PAGE
                data_table.delete(*data_table.get_children())
                for n, data in enumerate(data_file.iloc[rows[0]:rows[1]].iterrows()):
                    data = data[1]
                    data_table.insert(parent='', index='end', iid=n,
                                      values=(data['website'], data['username'], CRYPTO.decrypt(data['password'].encode()).decode(), data['last update']))
                if len(data_file) != 0:
                    indicator.config(text=f"{round(rows[0]/ROWS_PER_PAGE)+1} / {math.ceil(len(data_file)/ROWS_PER_PAGE)}")

        def next_page(rows):
            if rows[1] < len(data_file):
                rows[0] += ROWS_PER_PAGE
                rows[1] += ROWS_PER_PAGE
                data_table.delete(*data_table.get_children())
                for n, data in enumerate(data_file.iloc[rows[0]:rows[1]].iterrows()):
                    data = data[1]
                    data_table.insert(parent='', index='end', iid=n,
                                      values=(data['website'], data['username'], CRYPTO.decrypt(data['password'].encode()).decode(), data['last update']))
                if len(data_file) != 0:
                    indicator.config(text=f"{round(rows[0]/ROWS_PER_PAGE)+1} / {math.ceil(len(data_file)/ROWS_PER_PAGE)}")

        def update_table():
            data_table.delete(*data_table.get_children())
            for n, data in enumerate(data_file.iloc[rows[0]:rows[1]].iterrows()):
                data = data[1]
                data_table.insert(parent='', index='end', iid=n,
                                  values=(data['website'], data['username'], CRYPTO.decrypt(data['password'].encode()).decode(), data['last update']))

        def update_delete():
            global data_file
            data_file.index = [x for x in range(0, len(data_file))]
            if len(data_table.get_children()) != 0:
                index = data_table.focus()
                next_index = list(data_table.get_children()).index(index)
                data_file = data_file.drop(axis=0, labels=(int(index))+rows[0])

                data_table.delete(index)
                update_table()

                if next_index != 0:
                    data_table.focus(data_table.get_children()[next_index-1])
                    data_table.selection_set(data_table.get_children()[next_index-1])
                elif len(data_table.get_children()) != 0:
                    data_table.focus(data_table.get_children()[next_index])
                    data_table.selection_set(data_table.get_children()[next_index])

                data_file.to_csv(path_or_buf=f"{RESOURCE_PATH}/passwordmanager.csv", mode="w", header=True, index=False)

                if math.ceil(len(data_file) / ROWS_PER_PAGE) == len(data_file) / ROWS_PER_PAGE and len(data_file) != 0:
                    indicator.config(text=f"{round(rows[0] / ROWS_PER_PAGE) + 1} / {math.ceil(len(data_file) / ROWS_PER_PAGE)}")

        clear_frame(window)

        headline = Label(text="Password Manager", font=("Ariel", 20, "bold"), fg=MAIN_COLOR)
        headline.place(x=200, y=10)

        small_logo = Canvas(width=46, height=46, highlightthickness=0)
        small_logo.create_image(23, 23, image=SMALL_LOGO)
        small_logo.place(y=5, x=450)

        trash_button = Button(image=TRASH_LOGO, borderwidth=0, fg=MAIN_COLOR, command=update_delete)
        trash_button.place(x=650, y=7)

        style = Style(window)
        style.theme_use("clam")
        style.configure("Treeview", background=MAIN_WHITE,
                        fieldbackground=MAIN_WHITE, foreground="black")

        data_table = Treeview(window, height=24)
        data_table['columns'] = tuple(data_file.keys())
        data_table.column("#0", width=0, stretch=NO)

        rows = [0, ROWS_PER_PAGE]

        if len(data_file) < 2:
            rows[1] = len(data_file)

        for col in data_table['columns']:
            data_table.heading(col, text=col, anchor=CENTER)
            if col != 'password':
                data_table.column(col, width=0, anchor=CENTER)
            else:
                data_table.column('password', width=50, anchor=CENTER)

        for n, data in enumerate(data_file.iloc[rows[0]:rows[1]].iterrows()):
            data = data[1]
            data_table.insert(parent='', index='end', iid=n, values=(data['website'], data['username'], CRYPTO.decrypt(data['password'].encode()).decode(), data['last update']))

        data_table.pack(fill="x", pady=50)

        last_page_button = Button(borderwidth=0, text="last page", fg=MAIN_COLOR, bg=MAIN_WHITE, command=lambda: last_page(rows))
        last_page_button.place(x=200, y=465)

        if len(data_file) == 0:
            indicator = Label(text=f"{round(rows[0]/ROWS_PER_PAGE)+1} / {math.ceil(len(data_file)/ROWS_PER_PAGE)+1}", fg=MAIN_COLOR)
        else:
            indicator = Label(
                text=f"{round(rows[0] / ROWS_PER_PAGE) + 1} / {math.ceil(len(data_file) / ROWS_PER_PAGE)}",
                fg=MAIN_COLOR)
        indicator.place(x=340, y=467)

        next_page_button = Button(borderwidth=0, text="next page", fg=MAIN_COLOR, bg=MAIN_WHITE, command=lambda: next_page(rows))
        next_page_button.place(x=450, y=465)

        return_button = Button(image=RETURN_IMAGE, borderwidth=0, command=main_page)
        return_button.place(x=10, y=5)

        window.mainloop()


def main_page():
    clear_frame(window)

    small_logo = Canvas(width=200, height=189, highlightthickness=0)
    small_logo.create_image(100, 100, image=LOGO_IMAGE)
    small_logo.pack(pady=40)

    display_button = Button(text="Display", bg=MAIN_COLOR, fg=MAIN_WHITE, activebackground=MAIN_WHITE,
                            activeforeground=MAIN_COLOR, borderwidth=0, command=display_page)
    display_button.pack()

    return_button = Button(text="Add", bg=MAIN_COLOR, fg=MAIN_WHITE, activebackground=MAIN_WHITE,
                           activeforeground=MAIN_COLOR, borderwidth=0, command=add_page)
    return_button.pack(pady=60)

    window.mainloop()


window = Tk()
window.geometry("700x500")
# window.bind("<Key>", motion)

RESOURCE_PATH = "resources/PasswordManager"
LOGO_IMAGE = PhotoImage(file=f"{RESOURCE_PATH}/logo.png")
SMALL_LOGO = PhotoImage(file=f"{RESOURCE_PATH}/small_logo.png")
RETURN_IMAGE = PhotoImage(file=f"{RESOURCE_PATH}/return.png", width=40, height=40)
TRASH_LOGO = PhotoImage(file=f"{RESOURCE_PATH}/trash.png")
MAIN_COLOR = "#D4483B"
MAIN_WHITE = "#F0F0F0"
ROWS_PER_PAGE = 18
CRYPTO = Fernet(b'YnhYyxH_YkYZvOYm9L04CJibItOd4BFEZLn1JCnRWWA=')
ADMIN_PASS = '99bafb1d500f1078842fbf8aab8b6e45a91b141d74ad7fa9e545a5a819f173df'

data_file = pd.read_csv(f"{RESOURCE_PATH}/passwordmanager.csv")

main_page()
