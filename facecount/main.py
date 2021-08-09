# Created by kor_a at 04/08/2021
import face_recognition
import cv2
import numpy as np
import sqlite3
import datetime

conn = sqlite3.connect('InOut_Times.db')

print("Connection established")

cursor = conn.cursor()

sql = '''CREATE TABLE LOGS(
NAME CHAR(30),
INOUT CHAR(1),
TIME CHAR(30)
)'''
#cursor.execute(sql)
#print("Table created")

width, height = 800, 600
cap = cv2.VideoCapture(0)

giris_zaman = ""
cikis_zaman = ""
giris_dakika = ""
cikis_dakika = ""
person_name = ""

video_capture = cv2.VideoCapture(0)

orkun_image = face_recognition.load_image_file("faces/orkun_final.jpg")
elon_image = face_recognition.load_image_file("faces/elon_final.jpg")

orkun_face_encoding = face_recognition.face_encodings(orkun_image, num_jitters=5)[0]
elon_face_encoding = face_recognition.face_encodings(elon_image, num_jitters=5)[0]

known_face_encodings = [
    orkun_face_encoding,
    elon_face_encoding
]

known_face_names = [
    "Orkun Koray GUNGOR",
    "Elon MUSK"
]

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
giris = 0
cikis = 0

while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    height, width, channels = frame.shape
    centerX = int(width / 2)
    centerY = int(height / 2)
    Time_now = datetime.datetime.now()

    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "unknown"

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                face_names.append(name)

    process_this_frame = not process_this_frame

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        center = (int((int(right)+int(left))*2), int((int(top)+int(bottom))*2))

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.circle(frame, center, 5, (0, 0, 255), -1)
        anlık_zaman_dakika = Time_now.strftime("%M")

        if name == "Orkun Koray GUNGOR":
            if ((center[0] <= 306 and giris_dakika != anlık_zaman_dakika) and (cikis_dakika != anlık_zaman_dakika)):
                giris_zaman = Time_now.strftime("%c")
                giris_dakika = Time_now.strftime("%M")
                print(f'{name} {Time_now.strftime("%c")} zamanında giriş yaptı.')
                cursor.execute('''INSERT INTO LOGS(NAME, INOUT, TIME) VALUES (?,'I',?)''', (name, giris_zaman))
                conn.commit()

            if ((center[0] > 306 and cikis_dakika != anlık_zaman_dakika) and (giris_dakika != anlık_zaman_dakika)):
                cikis_zaman = Time_now.strftime("%c")
                cikis_dakika = Time_now.strftime("%M")
                print(f'{name} {Time_now.strftime("%c")} zamanında çıkış yaptı.')
                cursor.execute('''INSERT INTO LOGS(NAME, INOUT, TIME) VALUES (?,'O',?)''', (name, cikis_zaman))
                conn.commit()

        if name == "Elon MUSK":
            if ((center[0] <= 306 and giris_dakika != anlık_zaman_dakika) and (cikis_dakika != anlık_zaman_dakika)):
                giris_zaman = Time_now.strftime("%c")
                giris_dakika = Time_now.strftime("%M")
                print(f'{name} {Time_now.strftime("%c")} zamanında giriş yaptı.')
                cursor.execute('''INSERT INTO LOGS(NAME, INOUT, TIME) VALUES (?,'I',?)''', (name, giris_zaman))
                conn.commit()

            if ((center[0] > 306 and cikis_dakika != anlık_zaman_dakika) and (giris_dakika != anlık_zaman_dakika)):
                cikis_zaman = Time_now.strftime("%c")
                cikis_dakika = Time_now.strftime("%M")
                print(f'{name} {Time_now.strftime("%c")} zamanında çıkış yaptı.')
                cursor.execute('''INSERT INTO LOGS(NAME, INOUT, TIME) VALUES (?,'O',?)''', (name, cikis_zaman))
                conn.commit()

    first_point = (centerY+70, 0)
    second_point = (centerY+70, height)
    cv2.line(frame, first_point, second_point, (0, 0, 255), 5)

    cv2.imshow('recognition', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

conn.commit()
conn.close()

video_capture.release()
cv2.destroyAllWindows()