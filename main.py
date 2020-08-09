from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox

from tempfile import TemporaryFile

import logging
import io
import shutil

import csv

tmp_logging_stream = io.StringIO()
logging.basicConfig(stream=tmp_logging_stream)

def export_file(filelike, initialfile=''):
    fname = filedialog.asksaveasfilename(initialfile=initialfile)
    with open(fname, 'w') as fout:
        filelike.seek(0)
        shutil.copyfileobj(filelike, fout)

def swap_names():
    try:
        with open(name_mapping.get()) as fin:
            name_map = {name.strip(): nickname.strip() for name, nickname in csv.reader(fin)}

    except FileNotFoundError as e:
        messagebox.showerror('File Not Found', f'Mapping file not found: {name_mapping.get()}')
        logging.error('File could not be opened', exc_info=True)
        return

    out_names = []
    try:
        with open(name_list.get()) as fin:
            for name in fin:
                name = name.strip()
                out_names.append(name_map.get(name, name))

    except FileNotFoundError as e:
        messagebox.showerror('File Not Found', f'Backer name file not found: {name_list.get()}')
        logging.error('File could not be opened', exc_info=True)
        return

    with filedialog.asksaveasfile(initialfile='PatreonBackerList.txt') as fout:
        fout.write('\n'.join(sorted(out_names)))
        fout.flush()

def change_buttons(*args):
    # Make sure these are both filled out
    if name_list.get() and name_mapping.get():
        button_run.config(state=ACTIVE)
    else:
        button_run.config(state=DISABLED)

root = Tk()
root.title('Patreon Backer Nickname Converter')

mainframe = ttk.Frame(root, padding='3 3 12 12')
mainframe.grid(column=0, row=0, sticky=NSEW)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

name_list = StringVar()
name_mapping = StringVar()
for strvar in (name_list, name_mapping):
    strvar.trace('w', change_buttons)

def create_file_selector(entry_widget, file_extension):
    def file_selector():
        fname = filedialog.askopenfilename(initialdir='~', filetypes=((file_extension.upper(), f'*.{file_extension.lower()}'), ('All Files', '*')))
        entry_widget.delete(0, 'end')
        entry_widget.insert(0, fname)
    return file_selector

### Select File for Patreon Backers ###
entry_name_list = ttk.Entry(mainframe, width=30, textvariable=name_list)
entry_name_list.grid(column=2, row=1, sticky=EW)
ttk.Label(mainframe, text='Patreon Backer List File:').grid(column=1, row=1, sticky=E)
ttk.Button(mainframe, text='Browse', command=create_file_selector(entry_name_list, 'txt')).grid(column=3, row=1, sticky=EW)

### Select File for Nickname Mapping ####
entry_name_mapping = ttk.Entry(mainframe, width=30, textvariable=name_mapping)
entry_name_mapping.grid(column=2, row=2, sticky=EW)
ttk.Label(mainframe, text='Nickname Mapping CSV:').grid(column=1, row=2, sticky=E)
ttk.Button(mainframe, text='Browse', command=create_file_selector(entry_name_mapping, 'csv')).grid(column=3, row=2, sticky=EW)

### Run button to generate new backer file ###
button_run = ttk.Button(mainframe, text='Run', command=swap_names)
button_run.grid(column=3, row=3, sticky=E)
button_run.config(state=DISABLED)  # set to disabled by default

### Controls for exporting our log file ###
button_export_log = ttk.Button(mainframe, text='Export Logfile',
                               command=lambda : export_file(tmp_logging_stream, initialfile='PatreonBackerLog.log'))
button_export_log.grid(column=2, row=5, sticky=E)

### Quit button and cleanup ###
def cleanup_and_exit():
    tmp_logging_stream.close()
    root.destroy()

ttk.Button(mainframe, text='Close', command=cleanup_and_exit).grid(column=3, row=5, sticky=W)


### Misc Config ###
entry_name_list.focus()
mainframe.columnconfigure(2, weight=1)  # Make our Entry elements the only things that expand with the window
for child in mainframe.winfo_children():
    child.grid(pady=5, padx=5)

root.mainloop()

