import imutils # This is a library that makes it easier to work with OpenCV
import cv2 # OpenCV library for computer vision
import numpy as np # NumPy library for numerical operations
import os # Os library to clear the command prompt 
import sqlite3 # SQLite3 library to store the video files
import datetime # Datetime module to get the current date and time

# Number of frames to pass before changing the frame to compare the current
# frame against
FRAMES_TO_PERSIST = 10

# Minimum boxed area for a detected motion to count as actual motion
# Use to filter out noise or small objects
MIN_SIZE_FOR_MOVEMENT = 2000

# Minimum length of time where no motion is detected it should take
#(in program cycles) for the program to declare that there is no movement
MOVEMENT_DETECTED_PERSISTENCE = 100

# Create capture object
cap = cv2.VideoCapture(0) # Then start the webcam

# Init frame variables
first_frame = None
next_frame = None

# Init display font and timeout counters
font = cv2.FONT_HERSHEY_SIMPLEX
delay_counter = 0
movement_persistent_counter = 0

# Connect to the database
conn = sqlite3.connect('records.db') # Create a database file
# Create a cursor
c = conn.cursor() # Create a cursor object using the cursor method

video_file = False
data = c.execute("SELECT * FROM files").fetchall() # Get all the records from the database
unique_id = len(data) + 1 # Unique ID for the video file
frame_width = int(cap.get(3))  # Get the frame width
frame_height = int(cap.get(4))  # Get the frame height
size = (frame_width, frame_height)  # Set the frame size
is_recording = False # Recording flag
is_saving = False # Saving flag

print("----------------------------------------------------------------")
print("MOTION DETECTION INITIALIZED")
print("----------------------------------------------------------------")
print("Press 'q' to quit")

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

while True:

    # Set transient motion detected as false
    transient_movement_flag = False
    
    # Read frame
    ret, main_frame = cap.read()
    text = "Unoccupied"

    # If there's an error in capturing
    if not ret:
        print("CAPTURE ERROR")
        continue

    # Resize and save a greyscale version of the image
    frame = imutils.resize(main_frame, width = 750)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Blur it to remove camera noise (reducing false positives)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # If the first frame is nothing, initialise it
    if first_frame is None: first_frame = gray    

    delay_counter += 1

    # Otherwise, set the first frame to compare as the previous frame
    # But only if the counter reaches the appriopriate value
    # The delay is to allow relatively slow motions to be counted as large
    # motions if they're spread out far enough
    if delay_counter > FRAMES_TO_PERSIST:
        delay_counter = 0
        first_frame = next_frame

    # Set the next frame to compare (the current frame)
    next_frame = gray

    # Compare the two frames, find the difference
    frame_delta = cv2.absdiff(first_frame, next_frame)
    thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

    # Fill in holes via dilate(), and find contours of the thesholds
    thresh = cv2.dilate(thresh, None, iterations = 2)
    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop over the contours
    for cn in cnts:

        # Save the coordinates of all found contours
        (x, y, w, h) = cv2.boundingRect(cn)
        
        # If the contour is too small, ignore it, otherwise, there's transient
        # movement
        if cv2.contourArea(cn) > MIN_SIZE_FOR_MOVEMENT:
            transient_movement_flag = True
            
            # Draw a rectangle around big enough movements
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # The moment something moves momentarily, reset the persistent
    # movement timer.
    if transient_movement_flag == True:
        movement_persistent_flag = True
        movement_persistent_counter = MOVEMENT_DETECTED_PERSISTENCE

    # As long as there was a recent transient movement, say a movement
    # was detected    
    if movement_persistent_counter > 0:
        text = "Movement Detected " + str(movement_persistent_counter)
        movement_persistent_counter -= 1
    else:
        text = "No Movement Detected"

    # start recording when motion is detected and stop when motion stops
    if movement_persistent_counter > 80 and not is_saving:
        if not video_file: # Check if the video file is not created
            result = cv2.VideoWriter('recordings/record_'+str(unique_id)+'.avi',  
                                cv2.VideoWriter_fourcc(*'MJPG'), 
                                10, size)  # Create a video file. Here 1st argument is the file name, 2nd argument is the codec, 3rd argument is the frames per second, and 4th argument is the frame size
        is_recording = True 
        video_file = True 
        result.write(main_frame)  # Write the frame to the video file
    
    # stop recording when motion stops
    else:
        if video_file and is_recording:
            save_video()
        
    if is_recording:
        frame = cv2.circle(frame, (frame_width-60,50), 12, (0, 0, 255), -1) # Draw a red circle to indicate recording
        

    # Print the text on the screen, and display the raw and processed video 
    # feeds
    cv2.putText(frame, str(text), (10,35), font, 0.75, (255,255,255), 2, cv2.LINE_AA)
    
    # Convert the frame_delta to color for splicing
    frame_delta = cv2.cvtColor(frame_delta, cv2.COLOR_GRAY2BGR)

    # Splice the two video frames together to make one long horizontal one
    cv2.imshow("frame", np.hstack((frame_delta, frame)))

    # Interrupt trigger by pressing q to quit the open CV program
    ch = cv2.waitKey(1)
    if ch & 0xFF == ord('q'):
        # go back to the main menu
        if is_recording:
            save_video()
       
        
        break

# Cleanup when closed
cv2.destroyAllWindows()
cap.release()
os.system('cls')
os.system('python main.py')