import socket
import threading
from tkinter import *
from tkinter import ttk
from tkinter import messagebox

port = 80


class HTTP_getr(object):
    def __init__(self, master):
        self.host_http = Label(master, text="http://", font=16)
        self.host_http.place(x=5, y=5, height=30, width=45)
        self.host_txt = Entry(master, font=16)
        self.host_txt.place(x=50, y=10, height=22, width=500)
        self.host_txt.bind("<Return>", self.get_pack)

        self.listbox = Text()
        self.listbox.configure(state='normal')
        self.listbox.place(x=0, y=40, height=560, width=800)
        scrollbar = Scrollbar(self.listbox, orient="vertical",
                              command=self.listbox.yview)
        scrollbar.grid(row=0, column=1)
        self.listbox['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side=RIGHT, fill=Y)

        self.progress = ttk.Progressbar(master, orient='horizontal',
                                        length=240, mode='determinate')
        self.progress.place(x=555, y=10, height=22)
        self.progress["value"] = 0

    def get_http_list(self):
        addr = self.host_txt.get()
        host_addr = addr.split('/')[0]
        try:
            host = socket.gethostbyname(host_addr.replace(' ', ''))
        except:
            messagebox.showerror("Error", "Host not avaliable")
            return
        if addr[len(host_addr):]:
            request = b"GET " + addr[len(host_addr):].encode()
            request += b" HTTP/1.1\r\nHost: " + host_addr.encode()
            request += b"\r\n\r\n"
        else:
            request = b"GET " + b"/" + b" HTTP/1.1\r\nHost: "
            request += host_addr.encode() + b"\r\n\r\n"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(1)
        s.send(request)
        try:
            first_data = s.recv(2048)
        except:
            messagebox.showerror("Error", "Can't connect to server")
            return
        data = first_data.decode(errors='ignore')
        ind = data.find("Content-Length:")
        if ind != -1:
            flag = True
            content_len = data[ind:].split('\n')[0].split(' ')[1]
            self.progress["maximum"] = int(content_len)
            self.progress["value"] += len(data)
        else:
            flag = False
        self.listbox.insert(END, data)
        while True:
            try:
                msg = s.recv(2048)
            except socket.timeout as e:
                if not flag:
                    self.progress["value"] = self.progress["maximum"]
                self.listbox.configure(state='disabled')
                break
            except socket.error as e:
                messagebox.showerror("Error", "Can't connect to server")
                return
            else:
                self.listbox.insert(END, msg.decode(errors='ignore'))
                if flag:
                    self.progress["value"] += len(msg)

    def get_pack(self, event):
        self.listbox.configure(state='normal')
        self.listbox.delete(1.0, END)
        self.progress["value"] = 0
        thread = threading.Thread(target=self.get_http_list)
        thread.daemon = True
        thread.start()


if __name__ == '__main__':
    root = Tk()
    http = HTTP_getr(root)
    root.minsize(width=800, height=600)
    root.wm_title("HTTP")
    root.mainloop()
