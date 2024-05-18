import cv2
import datetime
import sqlite3
import keyboard

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
   
size = (frame_width, frame_height) 
result = cv2.VideoWriter('filename.avi',  
                         cv2.VideoWriter_fourcc(*'MJPG'), 
                         10, size) 

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    # recording
    if keyboard.is_pressed('r') or is_recording:
        is_recording = True
        result.write(frame)

    if keyboard.is_pressed('p'):
        print("Accessing the records")
        data = c.execute("SELECT * FROM files").fetchall()
        for row in data:
            print(row[0])


    if is_recording:
        frame = cv2.circle(frame, (frame_width-60,50), 6, (0, 0, 255), -1)

    # stop recording
    if keyboard.is_pressed('s'):
        is_recording = False
        result.release()

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
        break

# When everything is done, release the capture
# out.release() 
video_capture.release()
cv2.destroyAllWindows()