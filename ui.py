import PyQt5.QtWidgets as qt # Import the PyQt5 module for the GUI
import sys # Import the sys module to access the command line arguments
import sqlite3 # Import the SQLite3 library to store the video files
import os # Import the OS library to start the video file in the video player and remove the temp file

class RecordViewer(qt.QWidget): # Create a class RecordViewer
    def __init__(self):
        super().__init__()
        self.initUI() # Call the initUI method

    def initUI(self): # Create a method initUI
        self.setWindowTitle('Record Viewer') # Set the window title
        self.setGeometry(100, 100, 800, 600) # Set the window geometry

        self.layout = qt.QVBoxLayout() # Create a vertical layout
        self.setLayout(self.layout) # Set the layout

        self.records = qt.QListWidget() # Create a list widget
        self.layout.addWidget(self.records) # Add the list widget to the layout

        self.view_button = qt.QPushButton('View Record') # Create a button to view the record
        self.layout.addWidget(self.view_button) # Add the button to the layout

        self.view_button.clicked.connect(self.view_record) # Connect the button to the view_record method

        self.show() # Show the window

    def view_record(self):
        record_id = self.records.currentItem().text() # Get the current item from the list widget
        record = c.execute("SELECT * FROM files WHERE id = ?", (record_id,)).fetchone() # Get the record from the database

        if record: # Check if the record exists
            with open("temp.avi", 'wb') as output_file: # Open the temp file to write the video file
                output_file.write(record[2]) # Write the record to the temp file

            # Open the video file in video player
            os.startfile('temp.avi') # Open the temp file in the video player
        else:
            print("Record not found")

if __name__ == '__main__':

    app = qt.QApplication(sys.argv) # Create an application
    viewer = RecordViewer()     # Create an instance of the RecordViewer class
    sys.exit(app.exec_()) # Execute the application