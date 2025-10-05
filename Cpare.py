import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector

# --- Global style config ---
COLORS = {"bg": "#fefefe",
    "btn_bg": "#0078D7",
    "btn_fg": "white",
    "btn_active": "#005A9E",
    "text": "#333"}

FONTS = {"title": ("Helvetica", 20, "bold"),
    "subtitle": ("Helvetica", 18, "bold"),
    "big": ("Helvetica", 16),
    "normal": ("Helvetica", 14),
    "msg": ("Helvetica", 13)}

BTN_STYLE = {
    "bg": COLORS["btn_bg"],
    "fg": COLORS["btn_fg"],
    "activebackground": COLORS["btn_active"],
    "bd": 0,
    "height": 2,
    "font": FONTS["big"]
}

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root4505",
        database="ProjectC")
    cursor = conn.cursor()

except mysql.connector.Error as err:
    print("Error connecting to DB:", err)
    exit()

def close_connection():
    cursor.close()
    conn.close()

def login_window():
    root = tk.Tk()
    root.title("Login / Sign Up")
    root.geometry("420x320")
    root.config(bg=COLORS["bg"])

    tk.Label(root, text="Welcome to Chat Interface", font=FONTS["title"], bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=(18, 12))

    tk.Label(root, text="Username", font=FONTS["big"], bg=COLORS["bg"]).pack(pady=(10, 4))
    entry_user = tk.Entry(root, font=FONTS["big"], width=25, relief="solid", bd=1)
    entry_user.pack(pady=4)

    tk.Label(root, text="Password", font=FONTS["big"], bg=COLORS["bg"]).pack(pady=(10, 4))
    entry_pass = tk.Entry(root, show="*", font=FONTS["big"], width=25, relief="solid", bd=1)
    entry_pass.pack(pady=4)

    def try_signup():
        u = entry_user.get().strip()
        p = entry_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Error", "Enter username and password")
            return
        cursor.execute("SELECT U_name FROM users WHERE U_name=%s", (u,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return
        cursor.execute("INSERT INTO users (U_name, password) VALUES (%s, %s)", (u, p))
        conn.commit()
        messagebox.showinfo("Success", "Registered — you can log in now")

    def try_login():
        u = entry_user.get().strip()
        p = entry_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Oops", "Enter username and password")
            return
        cursor.execute("SELECT * FROM users WHERE U_name=%s AND password=%s", (u, p))
        if cursor.fetchone():
            messagebox.showinfo("Welcome", f"Logged in as {u}")
            root.destroy()
            menu_window(u)
        else:
            messagebox.showerror("Nope", "Invalid username or password")

    tk.Button(root, text="Sign Up", command=try_signup, **BTN_STYLE).pack(fill='x', padx=80, pady=6)
    tk.Button(root, text="Login", command=try_login, **BTN_STYLE).pack(fill='x', padx=80, pady=6)

    root.mainloop()

def back(root,username):
    root.destroy()
    menu_window(username)

def menu_window(username):
    root = tk.Tk()
    root.title(f"Menu - {username}")
    root.config(bg=COLORS["bg"])
    root.geometry("350x350")

    tk.Label(root, text=f"Welcome, {username}!", bg=COLORS["bg"], font=FONTS["subtitle"]).pack(pady=24)

    def open_inbox():
        root.destroy()
        inbox_window(username)

    def open_compose():
        root.destroy()
        compose_window(username)

    tk.Button(root, text="Inbox", command=open_inbox, width=16, **BTN_STYLE).pack(pady=10)
    tk.Button(root, text="Compose", command=open_compose, width=16, **BTN_STYLE).pack(pady=10)
    tk.Button(root, text="Leave", command=lambda: (close_connection(), root.destroy()), width=16, **BTN_STYLE).pack(pady=10)

    root.mainloop()

def inbox_window(username):
    root = tk.Tk()
    root.config(bg=COLORS["bg"])
    root.title(f"Inbox - {username}")
    root.geometry("1000x750")

    columns = ("SENDER", "SNIPPET", "STAMP")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

    # style only
    style = ttk.Style()
    style.configure("Treeview.Heading", font=FONTS["big"])
    style.configure("Treeview", font=FONTS["normal"], rowheight=28)

    tree.heading("SENDER", text="From")
    tree.heading("SNIPPET", text="Message Snippet")
    tree.heading("STAMP", text="Time")

    tree.column("SENDER", width=180)
    tree.column("SNIPPET", width=450)
    tree.column("STAMP", width=140)

    cursor.execute("SELECT SENDER,CONTENT,STAMP FROM CHATLOG WHERE RECEIVER = %s order by STAMP desc ", (username,))
    for row in cursor.fetchall():
        tree.insert("", 0, values=row)

    def full_open():
        root1 = tk.Toplevel(root)
        root1.geometry("400x300")
        root1.config(bg="white")

        Cont = tk.StringVar()
        lab = tk.Label(root1, textvariable=Cont, bg="white", fg="black", wraplength=380, font=FONTS["normal"])
        lab.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        Cont.set(value=tree.item(tree.selection())["values"][1])

        tk.Button(root1, text="Close", command=root1.destroy, **BTN_STYLE).pack(pady=10)

        root1.transient(root)
        root1.grab_set()
        root1.wait_window()

    tree.bind('<Double-Button-1>', lambda event: full_open())

    tk.Button(root,text = 'Back', command= lambda: back(root,username), **BTN_STYLE).pack(pady=10,side = tk.RIGHT)
    root.mainloop()

    root.mainloop()

def compose_window(username):
    root = tk.Tk()
    root.config(bg=COLORS["bg"])
    root.title(f"Compose - {username}")
    root.geometry("560x400")

    tk.Label(root, text="To:", font=FONTS["big"], bg=COLORS["bg"]).pack(anchor='w', padx=12, pady=(14, 4))
    entry_to = tk.Entry(root, font=FONTS["big"], width=40, relief="solid", bd=1)
    entry_to.pack(padx=12, pady=4)

    tk.Label(root, text="Message:", font=FONTS["big"], bg=COLORS["bg"]).pack(anchor='w', padx=12, pady=(12, 4))
    txt = tk.Text(root, font=FONTS["msg"], width=62, height=10, relief="solid", bd=1, wrap="word")
    txt.pack(padx=12, pady=4)

    def send():
        r = entry_to.get().strip()
        c = txt.get("1.0", tk.END).strip()
        if not r or not c:
            messagebox.showwarning("Error", "Receiver and message cannot be empty")
            return
        cursor.execute("SELECT U_name FROM users WHERE U_name=%s", (r,))
        if not cursor.fetchone():
            messagebox.showerror("Error", "Receiver not found")
            return
        cursor.execute("INSERT INTO CHATLOG (SENDER, RECEIVER, CONTENT, STAMP) VALUES (%s, %s, %s, NOW())",
                       (username, r, c))
        conn.commit()
        messagebox.showinfo("Success", "Message sent!")
        root.destroy()
        menu_window(username)

    btn_frame = tk.Frame(root, bg=COLORS["bg"])
    btn_frame.pack(fill='x', pady=10, padx=12)

    tk.Button(btn_frame, text="Send", command=send, width=10, **BTN_STYLE).pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="Cancel", command=lambda: (root.destroy(), menu_window(username)), width=10, **BTN_STYLE).pack(side=tk.RIGHT, padx=8)

    root.mainloop()

if __name__ == "__main__":
    login_window()
