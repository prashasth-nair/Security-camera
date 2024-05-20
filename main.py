import cv2 # OpenCV library for computer vision
import datetime # Datetime module to get the current date and time
import sqlite3 # SQLite3 library to store the video files
import keyboard # Keyboard library to detect the key press
import os   # OS library to start the video file in the video player and remove the temp file

# Connect to the database
conn = sqlite3.connect('records.db') # Create a database file

# Create a cursor
c = conn.cursor() # Create a cursor object using the cursor method

# Create a table to store the video file
c.execute('''CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    data BLOB NOT NULL,
    date_time TEXT

)''')

# Commit the command
conn.commit() # Commit the changes to the database

print("------------------------------------------------------------")
print("Welcome to the Security Camera System")
print("Press 'r' to start recording")
print("Press 's' to stop recording")
print("Press 'q' to quit")
print("------------------------------------------------------------")

is_recording = False # Recording flag
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') # Load the face cascade
video_capture = cv2.VideoCapture(0) # Start the video capture
frame_width = int(video_capture.get(3))  # Get the frame width
frame_height = int(video_capture.get(4))  # Get the frame height
video_file = False # Video file flag
is_saving = False # Saving flag

data = c.execute("SELECT * FROM files").fetchall() # Get all the records from the database

unique_id = len(data) + 1 # Unique ID for the video file
   
size = (frame_width, frame_height)  # Set the frame size


def save_video(): # Function to save the video
    # Declare the global variables
    global is_saving 
    global video_file
    global unique_id
    global result
    global is_recording

    if is_recording: # Check if the recording is in progress
        is_recording = False # Set the recording flag to False
        video_file = False # Set the video file flag to False
        result.release() # Release the video file
        if not is_saving: # Check if the video is already saving
            is_saving = True  # Set the saving flag to True
            if c.execute("SELECT * FROM files WHERE name = ?", ('record_'+str(unique_id)+'.avi',)).fetchall(): # Check if the file already exists
                print("File already exists")

            # Insert a file
            file_data = open('recordings/record_'+str(unique_id)+'.avi', 'rb').read() # Read the video file
            c.execute('''INSERT INTO files (name, data,date_time) VALUES (?, ?, ?)''', ('record_'+str(unique_id)+'.avi', file_data, datetime.datetime.now())) # Insert the video file into the database
            conn.commit() # Commit the changes to the database

            unique_id += 1 # Increment the unique ID
            is_saving = False # Set the saving flag to False
            print("Saved recording in the database..")
    else:
        print("No recording to stop")

def main():
    # Declare the global variables
    global video_file
    global is_recording
    global unique_id
    global result

    while True:
        # Capture frame-by-frame
        frame = video_capture.read()  # Read the video capture

        # recording
        if keyboard.is_pressed('r') or is_recording:
            if not video_file: # Check if the video file is not created
                result = cv2.VideoWriter('recordings/record_'+str(unique_id)+'.avi',  
                                cv2.VideoWriter_fourcc(*'MJPG'), 
                                10, size)  # Create a video file. Here 1st argument is the file name, 2nd argument is the codec, 3rd argument is the frames per second, and 4th argument is the frame size
            is_recording = True 
            video_file = True 
            result.write(frame)  # Write the frame to the video file

        if is_recording:
            frame = cv2.circle(frame, (frame_width-60,50), 12, (0, 0, 255), -1) # Draw a red circle to indicate recording

        # stop recording
        if keyboard.is_pressed('s'):
            save_video()

        if keyboard.is_pressed('p'):
            # Print the records
            print("------------------------------------------------------------")
            print("Records")
            print("------------------------------------------------------------")
            data = c.execute("SELECT * FROM files").fetchall()
            for record in data:
                print(f"ID: {record[0]}")
                print(f"File Name: {record[1]}")
                print(f"Date Time: {record[3]}")
                print("------------------------------------------------------------")

            print("Enter the ID of the record you want to view or press 'q' to quit")

            record_id = input("Enter the ID: ")

            if record_id == 'q':
                print("Quitting Database..")
                continue

            record = c.execute("SELECT * FROM files WHERE id = ?", (record_id,)).fetchone() # Get the record from the database using the ID
            # Open the video file in video player
            if record: # Check if the record exists
                with open("temp.avi", 'wb') as output_file: # Open the temp file
                    output_file.write(record[2])     # Write the record to the temp file
                os.startfile('temp.avi') # Open the temp file in the video player
            else:   # If the record does not exist
                print("Record not found") # Print the message

        # NightVision
        current_time = datetime.datetime.now()
        if current_time.hour >= 18 or current_time.hour <= 6: # Check if the current time is between 6 PM and 6 AM
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convert the frame to grayscale
        
        faces = faceCascade.detectMultiScale(
            frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20),
        ) # Detect the faces in the frame. Here 1st argument is the frame, 2nd argument is the scale factor, 3rd argument is the minimum neighbors, and 4th argument is the minimum size of the face

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2) # Draw a rectangle around the face

        # Display the resulting frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            if is_recording:
                save_video()
            # if temp file exists delete it
            if os.path.exists("temp.avi"):
                os.remove("temp.avi")
            break

    # When everything is done, release the capture
    video_capture.release() # Release the video capture
    cv2.destroyAllWindows() # Close the video window

if __name__ == "__main__":
    # try block to handle the KeyboardInterrupt exception when the user presses 'Ctrl+C'
    try:
        main()
        conn.close()

    except KeyboardInterrupt: # Handle the KeyboardInterrupt exception
        conn.close()
        print("Quitting the system..")
        # if temp file exists delete it
        if os.path.exists("temp.avi"): 
            os.remove("temp.avi")
        exit(0)