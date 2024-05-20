import cv2
import datetime
import sqlite3
import keyboard
import os
os.add_dll_directory(r'C:\Program Files\VideoLAN\VLC')
import vlc

# Connect to the database
conn = sqlite3.connect('records.db')

# Create a cursor
c = conn.cursor()

# Create a table for security camera recording metadata
c.execute("""CREATE TABLE IF NOT EXISTS  meta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,
    date_time TEXT
)""")

# Create a table to store the video file
c.execute('''CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    data BLOB NOT NULL
)''')

# Commit the command
conn.commit()

print("------------------------------------------------------------")
print("Welcome to the Security Camera System")
print("Press 'r' to start recording")
print("Press 's' to stop recording")
print("Press 'q' to quit")
print("------------------------------------------------------------")

is_recording = False
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
video_capture = cv2.VideoCapture(0)
frame_width = int(video_capture.get(3)) 
frame_height = int(video_capture.get(4)) 
video_file = False
is_saving = False

data = c.execute("SELECT * FROM meta").fetchall()

unique_id = len(data) + 1
   
size = (frame_width, frame_height) 

def save_video():
    global is_saving
    global video_file
    global unique_id
    global result
    global is_recording

    if is_recording:
        is_recording = False
        video_file = False
        result.release()
        if not is_saving:
            is_saving = True
            if c.execute("SELECT * FROM files WHERE name = ?", ('record_'+str(unique_id)+'.avi',)).fetchall():
                print("File already exists")
            # Insert a meta
            c.execute("INSERT INTO meta (file_name, date_time) VALUES (?, ?)", ('record_'+str(unique_id)+'.avi', datetime.datetime.now()))
            conn.commit()

            # Insert a file
            file_data = open('recordings/record_'+str(unique_id)+'.avi', 'rb').read()
            c.execute('''INSERT INTO files (name, data) VALUES (?, ?)''', ('record_'+str(unique_id)+'.avi', file_data))
            conn.commit()

            unique_id += 1
            is_saving = False
            print("Saved recording in the database..")
    else:
        print("No recording to stop")

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # recording
    if keyboard.is_pressed('r') or is_recording:
        if not video_file:
            result = cv2.VideoWriter('recordings/record_'+str(unique_id)+'.avi',  
                            cv2.VideoWriter_fourcc(*'MJPG'), 
                            10, size) 
        is_recording = True
        video_file = True
        result.write(frame)

    if is_recording:
        frame = cv2.circle(frame, (frame_width-60,50), 12, (0, 0, 255), -1)

    # stop recording
    if keyboard.is_pressed('s'):
        save_video()

    if keyboard.is_pressed('p'):
        # Print the records
        print("------------------------------------------------------------")
        print("Records")
        print("------------------------------------------------------------")
        data = c.execute("SELECT * FROM meta").fetchall()
        for record in data:
            print(f"ID: {record[0]}")
            print(f"File Name: {record[1]}")
            print(f"Date Time: {record[2]}")
            print("------------------------------------------------------------")

        print("Enter the ID of the record you want to view or press 'q' to quit")
        record_id = input("Enter the ID: ")
        if record_id == 'q':
            continue
        record = c.execute("SELECT * FROM files WHERE id = ?", (record_id,)).fetchone()
        # Open the video file in video player
        if record:
            with open("temp.avi", 'wb') as output_file:
                output_file.write(record[2])
            media = vlc.MediaPlayer("temp.avi")
            media.play()
            


    # NightVision
    time = datetime.datetime.now()
    if time.hour >= 18 or time.hour <= 6:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    faces = faceCascade.detectMultiScale(
        frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(20, 20),
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi_gray = frame[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        if is_recording:
            save_video()
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()