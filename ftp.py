import threading
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
from tkinter.filedialog import *
from ftplib import FTP
import os
# ftp1.at.proftpd.org


class FTP_client(object):
    def __init__(self, master):
        self.host = Label(master, text="HOST:", font=16)
        self.host.place(x=5, y=5, height=30, width=45)
        self.host_txt = Entry(master, font=16)
        self.host_txt.place(x=55, y=10, height=22, width=300)
        self.host_txt.bind('<Return>', self.connect)

        self.label = Label(master, text='Done!!!', font=16, anchor='w')
        self.label.place(x=0, y=40, width=800)

        f = ttk.Frame()
        f.place(x=0, y=80, height=500, width=800)

        # create the tree and scrollbars
        self.dataCols = ('fullpath', 'type', 'size')
        self.tree = ttk.Treeview(columns=self.dataCols,
                                 displaycolumns='size')

        ysb = ttk.Scrollbar(orient=VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(orient=HORIZONTAL, command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set

        # setup column headings
        self.tree.heading('#0', text='Directory Structure', anchor=W)
        self.tree.heading('size', text='File Size', anchor=W)
        self.tree.column('size', stretch=0, width=150)

        # add tree and scrollbars to frame
        self.tree.grid(in_=f, row=0, column=0, sticky=NSEW)
        ysb.grid(in_=f, row=0, column=1, sticky=NS)
        xsb.grid(in_=f, row=1, column=0, sticky=EW)

        # set frame resizing priorities
        f.rowconfigure(0, weight=1)
        f.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self.DoubleClick)

    def save_file_dir(self, item, dir_path, path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            messagebox.showerror('Error', 'Directory already exists')
            return
        list_child = self.tree.get_children(item)
        if list_child:
            for i in list_child:
                item_chi = self.tree.item(i)
                name = item_chi['values'][0]
                type_item = item_chi['values'][1]
                save_dir = dir_path + '/' + name
                print(save_dir)
                save_path = path + '/' + name
                if type_item == 'file':
                    self.save_file(save_dir, save_path)
                else:
                    self.save_file_dir(i, save_dir, save_path)

    def save_file(self, dir_path, path):
        self.label['text'] = 'Downloading file: ' + dir_path
        with open(dir_path, 'wb') as file:
            self.ftp.retrbinary('RETR ' + path, file.write)

    def downloading(self):
        item_id = self.tree.selection()
        item = self.tree.item(item_id)
        path = item['values'][0]
        type_path = item['values'][1]
        dir_save = askdirectory()
        if not dir_save:
            return
        parent_id = self.tree.parent(item_id)
        while True:
            parent = self.tree.item(parent_id)
            if not parent['values']:
                break
            path = parent['values'][0] + '/' + path
            parent_id = self.tree.parent(parent_id)
        path = './' + path
        dir_path = dir_save + path.split('/')[-1]
        if type_path == 'file':
            self.save_file(dir_path, path)
        else:
            self.save_file_dir(item_id, dir_path, path)
        print(path, 'end')
        self.label['text'] = 'Done!!!'

    def DoubleClick(self, event):
        tr = threading.Thread(target=self.downloading)
        tr.daemon = True
        tr.start()

    def add_dir(self, ftp, dir, parent):
        self.label['text'] = 'Loading: ' + dir
        dir_list = ftp.mlsd(dir)
        if not dir_list:
            return
        for item in dir_list:
            if item[0] != '.' and item[0] != '..':
                if item[1]['type'] == 'file':
                    self.tree.insert(parent, END, text=item[0],
                                     values=[item[0], 'file',
                                             item[1]['size'] + ' B',
                                             'size'])
                else:
                    parent_next = self.tree.insert(parent, END, text=item[0],
                                                   values=[item[0],
                                                           'directory'])
                    nextdir = dir + '/' + item[0]
                    self.add_dir(ftp, nextdir, parent_next)
        self.label['text'] = 'Done!!!'

    def connect(self, event):
        self.tree.delete(*self.tree.get_children())
        host = self.host_txt.get()
        try:
            self.ftp = FTP(host)
            self.ftp.login()
        except:
            messagebox.showerror("Error", "Host not avaliable")
            return
        th = threading.Thread(target=self.add_dir, kwargs={'ftp': self.ftp,
                                                           'dir': '.',
                                                           'parent': ''})
        th.daemon = True
        th.start()


if __name__ == '__main__':
    root = Tk()
    ftp = FTP_client(root)
    root.minsize(width=800, height=600)
    root.wm_title("FTP")
    root.mainloop()
