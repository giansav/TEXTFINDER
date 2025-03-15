# TEXTFINDER - alpha version
# 
# built with Python 3.10
#
# This app allows you to search a word or a text within a PDF file 
# or within all the PDF files stored in a certain folder.
# This kind of search may be useful to check 
# whether a certain file or group of files contains the kind of informations 
# you are looking for without reading it.
# The output is a complete list of all the occurrences of the searched text 
# within all the selected files,
# with indication of all the pages where you can find the text 
# and the number of occurrences for each page.
#
# WARNINGS: 
# It only works with native PDF files, because of the limitations of PyPDF2 modules.
# It could take 2-3 minutes to give output.
# The user interface graphic is very basic.
# In case you browse a group of files the response widgets will adapt 
# automatically to the window without resizing the window itself.
# So, if the number of files is very high this could make the output hard to read.


# import the required libraries
import threading
import time
from tkinter import *
from tkinter import ttk, filedialog
import os
import PyPDF2
import regex

# create an instance of tkinter frame
win = Tk()
win.title("TEXT FINDER - Search text within PDF files")
win.geometry("1300x780")
win.configure(bg="light cyan")

# set global variable for searching files
entry = StringVar()
choice = 0
searching = False  # Flag to control the search state

# Frame per la selezione del file e della cartella
file_folder_frame = Frame(win, bg="light cyan")
file_folder_frame.pack(pady=20)

# Function to select a single PDF file
def open_file():
    global filepath
    global choice
    choice = 1
    file = filedialog.askopenfile(mode='r', filetypes=[('PDF Files', '*.pdf')])
    if file:
        filepath = os.path.abspath(file.name)
        file_label.config(text="File: " + str(filepath))

# Function to select a whole folder
def open_folder():
    global folderpath
    global pdffiles
    global choice
    choice = 2
    folderpath = filedialog.askdirectory()
    folder_label.config(text="Folder: " + str(folderpath))
    pdffiles = len([entry for entry in os.listdir(folderpath) if os.path.isfile(os.path.join(folderpath, entry))])

# Function to start the search
def start():
    global searching
    searching = True
    status_label.config(text="Searching...")
    response_widget.config(state=NORMAL)  # Enable the text widget to update
    response_widget.delete(1.0, END)  # Clear previous results
    if choice == 1:
        threading.Thread(target=find_in_PDF).start()
    elif choice == 2:
        threading.Thread(target=find_in_folder).start()

# Function to stop the search
def stop_search():
    global searching
    searching = False
    status_label.config(text="Search interrupted!")
    response_widget.config(state=NORMAL)
    response_widget.insert(END, "\nSearch was interrupted!\n")
    response_widget.config(state=DISABLED)

# function to find the submitted text in the selected PDF file
def find_in_PDF():
    item = entry.get()
    doc = PyPDF2.PdfFileReader(filepath)
    pages = doc.getNumPages()
    list_pages = []
    for i in range(pages):
        if not searching:  # Check if search was interrupted
            break
        current_page = doc.getPage(i)
        text = current_page.extractText()
        if regex.findall(item, text):
            count_page = len(regex.findall(item, text))
            list_pages.append((count_page, i + 1))
    count = len(list_pages)
    total = sum([tup[0] for tup in list_pages])
    answer = f"The text <{item}> was found {total} times on {count} pages.\nHere is the list of the occurrences (num_occ, page): \n\n"
    
    # Update the text widget with the results
    response_widget.insert(END, answer)
    response_widget.insert(END, list_pages)
    response_widget.config(state=DISABLED)  # Disable the text widget after updating
    status_label.config(text="Search completed!")  # Change status to completed
    choice = 0

# function to find the submitted text in the selected folder
def find_in_folder():
    item = entry.get()
    files = os.listdir(folderpath)
    pos_x = 400  # positional variables of the response widget
    pos_y = 0
    h = int(700 / pdffiles) - 20
    for listitem in files:
        if not searching:  # Check if search was interrupted
            break
        file_name = folderpath + "/" + listitem
        doc = PyPDF2.PdfFileReader(file_name)
        pages = doc.getNumPages()
        list_pages = []
        for i in range(pages):
            if not searching:  # Check if search was interrupted
                break
            current_page = doc.getPage(i)
            text = current_page.extractText()
            if regex.findall(item, text):
                count_page = len(regex.findall(item, text))
                list_pages.append((count_page, i + 1))
        count = len(list_pages)
        total = sum([tup[0] for tup in list_pages])
        answer1 = f"The book <{listitem}> has {pages} pages.\n"
        answer2 = f"The text <{item}> was found {total} times on {count} different pages.\nHere is the list of the occurrences (num_occ, page): \n\n"
        
        # Update the text widget with the results
        response_widget.insert(END, answer1)
        response_widget.insert(END, answer2)
        response_widget.insert(END, list_pages)
        response_widget.insert(END, "\n" + "-"*50 + "\n")  # Add separator for clarity
        pos_y = pos_y + h + 20  # allows to adapt response widgets to number of searched files
    response_widget.config(state=DISABLED)  # Disable the text widget after updating
    status_label.config(text="Search completed!")  # Change status to completed
    choice = 0

# Stile dei bottoni e delle etichette
style = ttk.Style()
style.configure("TButton", relief="flat", width=20, padding=10, font=("Arial", 12, "bold"))
style.map("TButton",
          foreground=[("active", "#ffffff")],
          background=[("active", "#0066cc")])

# Frame per il layout dei bottoni
button_frame = Frame(win, bg="#e0f7fa")  # Cambiato lo sfondo in un blu chiaro
button_frame.pack(pady=10)  # Ridotto lo spazio verticale tra i bottoni e gli altri elementi

# Widgets per la selezione del file PDF
label1 = Label(file_folder_frame, text="Click to select a PDF FILE", fg="#0066cc", bg="#e0f7fa", font=('Segoe UI', 13, "bold"))
label1.grid(row=0, column=0, padx=10, pady=5)  # Ridotto lo spazio tra etichetta e bottone
button1 = ttk.Button(file_folder_frame, text="Browse PDF file", command=open_file)
button1.grid(row=0, column=1, padx=10, pady=5)  # Ridotto lo spazio tra etichetta e bottone
button1.configure(style="TButton")

# Widgets per la selezione della cartella
label3 = Label(file_folder_frame, text="Click to select a FOLDER", fg="#0066cc", bg="#e0f7fa", font=('Segoe UI', 13, "bold"))
label3.grid(row=1, column=0, padx=10, pady=5)  # Ridotto lo spazio tra etichetta e bottone
button2 = ttk.Button(file_folder_frame, text="Browse Folder", command=open_folder)
button2.grid(row=1, column=1, padx=10, pady=5)  # Ridotto lo spazio tra etichetta e bottone
button2.configure(style="TButton")

# Labels per mostrare il file o la cartella selezionata
file_label = Label(win, text="No file selected", fg="#333333", bg="#e0f7fa", font=('Segoe UI', 12))
file_label.pack(pady=5)  # Ridotto lo spazio tra etichetta e altre sezioni

folder_label = Label(win, text="No folder selected", fg="#333333", bg="#e0f7fa", font=('Segoe UI', 12))
folder_label.pack(pady=5)  # Ridotto lo spazio tra etichetta e altre sezioni

# Widgets per inserire il testo da cercare
subm2 = Label(win, text="Insert text to find and click 'Submit'", fg="#0066cc", bg="#e0f7fa", font=('Segoe UI', 13, "bold"))
subm2.pack(pady=10)
word = Entry(win, textvariable=entry, fg="red", font="Georgia 11")
word.pack(pady=5)
button_subm2 = ttk.Button(win, text="Submit", command=start)
button_subm2.pack(pady=5)  # Ridotto lo spazio tra il bottone e il testo inserito
button_subm2.configure(style="TButton")

# Bottone per fermare la ricerca
stop_button = ttk.Button(win, text="Stop Search", command=stop_search)
stop_button.pack(pady=5)
stop_button.configure(style="TButton")

# Etichetta di stato per mostrare lo stato della ricerca
status_label = Label(win, text="", fg="#0066cc", bg="#e0f7fa", font=('Segoe UI', 12))
status_label.pack(pady=5)  # Ridotto lo spazio tra la label di stato e gli altri elementi

# Area di visualizzazione per i risultati
response_widget = Text(win, font="Consolas 9", state=DISABLED, height=60, width=120, wrap=WORD, bg="#f5f5f5", bd=1, relief="solid", highlightbackground="#0066cc", highlightthickness=2)
response_widget.pack(pady=10)  # Spazio tra il widget di testo e gli altri elementi



# Avvia il main loop di Tkinter
win.mainloop()
