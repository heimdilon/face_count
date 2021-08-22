# Created by kor_a at 13/08/2021
import face_recognition
import cv2
import numpy as np
import sqlite3
import datetime
from tkinter import *
from PIL import ImageTk, Image
from tkinter import messagebox
import os, sys
import pandas as pd
from tkinter.ttk import *


#Connect Databases
Times_database = sqlite3.connect('InOut_Times.db')
Names_database = sqlite3.connect('names.db')


Times_cursor = Times_database.cursor()
Names_cursor = Names_database.cursor()

namesql = '''
CREATE TABLE IF NOT EXISTS ALLNAMES(
NAME CHAR(30)
)
'''

timesql = '''
CREATE TABLE IF NOT EXISTS LOGS(
NAME CHAR(30),
INOUT CHAR(1),
TIME CHAR(30)
)'''

Names_cursor.execute(namesql)
Times_cursor.execute(timesql)


def create_path(faces_path):
    """
    Creates path with given parameter
    :param faces_path: path to create
    :return:
    """
    try:
        isExist = os.path.exists(faces_path)
        if not isExist:
            os.makedirs(faces_path)
    except Exception as e:
        messagebox.showerror("Path Creation Error", str(e))


path_to_create = f'{os.getcwd()}/faces'

create_path(path_to_create)

root = Tk()

root.title("Face Recognition")
root.geometry('720x720+0+0')
root.configure(background='black')

app = Frame(root)
app.grid()

lmain = Label(app)
lmain.grid()

width, height = 0,0

in_time = ""
out_time = ""

in_minute = ""
out_minute = ""

person_name = ""

face_locations = []
face_encodings = []
face_names = []
name = ""
process_this_frame = True

try:
    video_capture = cv2.VideoCapture(0)
except Exception as e:
    messagebox.showerror("Video Capture Error", str(e))


def load_faces():
    """
    Load Face names and images in faces file
    :return:
    """
    try:
        global known_face_encodings
        global known_face_names

        known_face_encodings = []

        dirpath = f'{os.getcwd()}/faces/'

        if len(f'{os.getcwd()}/faces') == 0:
            no_image = Label(root, text="No Image To Load")
            no_image.grid(column=1, row=0)

        for image in sorted(os.listdir(dirpath), key=lambda x: os.path.getctime(dirpath+x)):
            person_image = face_recognition.load_image_file(f'faces/{image}')
            person_encode = face_recognition.face_encodings(person_image, num_jitters=5)[0]
            known_face_encodings.append(person_encode)
            if len(known_face_encodings) == len(os.listdir(f'{os.getcwd()}/faces')):
                break


        Names_cursor.execute('''SELECT * FROM ALLNAMES''')
        rows = [r[0] for r in Names_cursor]

        known_face_names = rows
    except Exception as e:
        messagebox.showerror("Load Faces and Names Error", str(e))

load_faces()

in_minutes = {}
out_minutes = {}

def load_names_in_dicts():
    """
    Dictionaries For each person's last in and out time
    :return:
    """
    try:
        for keys in known_face_names:
            in_minutes[f'{keys}'] = ""
            out_minutes[f'{keys}'] = ""
    except Exception as e:
        messagebox.showerror("Load Names to Dicts Error", str(e))

load_names_in_dicts()


def video_stream():
    """
    Find persons in image and stream
    Saves in and out time in "InOut_Times.db"
    :return:
    """
    global frame
    global Time_now
    _, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    height, width, channels = frame.shape
    centerX = int(width / 2)
    centerY = int(height / 2)
    first_point = (centerY + 70, 0)
    second_point = (centerY + 70, height)
    cv2.line(frame, first_point, second_point, (0, 0, 255), 5)

    Time_now = datetime.datetime.now()
    global  process_this_frame

    if process_this_frame:
        global face_locations
        global face_names
        global in_time, out_time, in_minute, out_minute, person_name
        global known_face_names

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                face_names.append(name)

    process_this_frame = not process_this_frame

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        center = (int( ( int( right ) + int( left ) ) * 2 ), int( (int( top ) + int( bottom )) * 2 ) )

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
        time_now_minute = Time_now.strftime("%M")

        if name != "":
            if (( center[0] <= 306 and in_minutes[f'{name}'] != time_now_minute ) and (out_minutes[f'{name}'] != time_now_minute)):
                in_time = Time_now.strftime("%c")
                in_minutes[f'{name}'] = Time_now.strftime("%M")
                print(f'{name} {Time_now.strftime("%c")} Entered.')
                Times_cursor.execute('''INSERT INTO LOGS(NAME, INOUT, TIME) VALUES (?, 'I', ?)''', (name, in_time))
                Times_database.commit()

            if (( center[0] > 306 and out_minutes[f'{name}'] != time_now_minute) and (in_minutes[f'{name}'] != time_now_minute)):
                out_time = Time_now.strftime("%c")
                out_minutes[f'{name}'] = Time_now.strftime("%M")
                print(f'{name} {Time_now.strftime("%c")} Out.')
                Times_cursor.execute('''INSERT INTO LOGS(NAME, INOUT, TIME) VALUES (?, 'O', ?)''', (name, out_time))
                Times_database.commit()

    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(1, video_stream)

def saved():
    """
    Saves image and given name for face recognition
    :return:
    """
    try:
        x, cleanframe = video_capture.read()
        new_image = cv2.cvtColor(cleanframe, cv2.COLOR_BGR2GRAY)
        if image_name.get() == "":
            messagebox.showerror('Name Error', 'Enter a name first.')
        else:
            cv2.imwrite(f"{os.getcwd()}/faces/{image_name.get()}.jpg", new_image)
            messagebox.showinfo('Tebrikler', 'Resim Kayıt Edildi.')
            Names_cursor.execute('''INSERT INTO ALLNAMES(NAME) VALUES (?)''', (f'{image_name.get()}',))
            Names_database.commit()
    except Exception as e:
        messagebox.showerror("Save Image Error", str(e))

def showdb():
    """
    Shows last 15 item in "InOut_Times.db" on different window
    :return:
    """
    try:
        db_window = Tk()
        db_window.title("Entery Times")
        db_window.geometry("500x400")
        data = Times_cursor.execute('''SELECT * FROM LOGS ORDER BY ROWID DESC LIMIT 15''')
        i = 0
        for names in data:
            for j in range(len(names)):
                e = Label(db_window, text=names[j], width=25, relief="sunken", anchor="w")
                e.grid(row=i, column=j)
            i = i+1
        db_window.mainloop()
    except Exception as e:
        messagebox.showerror("Show Database Error", str(e))



def saveData():
    """
    Saves current data in "InOut_Times.db" as csv file
    :return:
    """
    try:
        date_time = Time_now.strftime("%m_%d_%Y__%H_%M_%S")
        save_db = pd.read_sql("SELECT * FROM LOGS", Times_database)
        save_db.to_csv(f'{date_time}.csv', index=False)
        messagebox.showinfo("Success", "File created")
    except Exception as e:
        messagebox.showerror("Data Save Error", str(e))


def deletePerson():
    """
    Deletes chosen person from face recognition and reload faces
    :return:
    """
    try:
        delete_window = Tk()
        delete_window.title("Delete")
        delete_window.geometry("300x400")

        combo = Combobox(delete_window)
        combo.grid(column=0, row=0)
        comboValues = tuple(known_face_names)
        combo['values'] = comboValues
        combo.current(0)

        def Delete_Pe():
            try:
                os.remove(f'{os.getcwd()}/faces/{combo.get()}.jpg')
                Names_cursor.execute('''DELETE FROM ALLNAMES WHERE NAME = (?)''', (f'{combo.get()}',))
                Names_database.commit()
                load_faces()
                load_names_in_dicts()
            except Exception as e:
                messagebox.showerror("Delete Person Error", str(e))

        deleteButton = Button(delete_window, text="Delete Person", command=Delete_Pe)
        deleteButton.grid(column=1, row=0)

    except Exception as e:
        messagebox.showerror("Delete Person Window Error", str(e))


def restart_names():
    """
    Relaod faces and dictionaries
    :return:
    """
    try:
        load_faces()
        load_names_in_dicts()
    except Exception as e:
        messagebox.showerror("Restart Names Error", str(e))

enter_name = Label(root, text="Enter image name")
enter_name.grid(column=0, row=1)

image_name = Entry(root, width=10)
image_name.grid(column=0, row=2)

save_image = Button(root, text="Save Image", command=saved)
save_image.grid(column=0, row=3)

restart_main = Button(root, text="Reload Faces", command=restart_names)
restart_main.grid(column=0, row=4)

show_database = Button(root, text="Show Entry Database", command=showdb)
show_database.grid(column=0, row=5)

save_data_to_excel = Button(root, text="Save Data to Current Directory", command=saveData)
save_data_to_excel.grid(column=0, row=6)

delete_person = Button(root, text="Delete Person", command=deletePerson)
delete_person.grid(column=0, row=7)

exit_button = Button(root, text="Exit Program", command=root.destroy)
exit_button.grid(column=0, row=8)

"""
If video_stream fails show message box
"""
try:
    video_stream()
except Exception as e:
        messagebox.showerror("Video Stream Error", str(e))

root.mainloop()

Times_database.commit()
Names_database.commit()

Times_database.close()
Names_database.close()

sys.exit()
