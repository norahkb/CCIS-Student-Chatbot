# Import required modules
import csv # Import the 'CSV' module for working with CSV files
import sqlite3 # Import the 'sqlite3' module for working with SQLite databases



def uploadToDB(filename,table): 
    # file name is the file name .csv
    # table is the table type ex:"section"
    
    print("uploading to db") # Print a message to indicate the upload process
    
    # Connect to the SQLite database 'university.db' located in the 'instance' directory using the object connection 
    connection = sqlite3.connect('instance/university.db')

    # Create a cursor object to execute SQL queries
    # used to interact with the database and execute SQL queries, It's an essential tool for working with databases using the sqlite3 module in Python. 
    cursor = connection.cursor()
    # Open the uploded specified CSV file
    file = open(filename)

    # Reading the contents of the uploded specified CSV file
    contents = csv.reader(file)

    # Construct the SQL INSERT query based on the specified table
    if table=="technicalsupport":
        insert_records = "INSERT INTO Technical_Support (name,telephone_number,email,description) VALUES(?,?,?,?)"
        insertExecute(contents, cursor, insert_records)

    if table=="instructor":
        insert_records = "INSERT INTO instructor (first_name,middle_name ,last_name,position ,course_number,section_number ,email ,office_telephone_number,office_floor ,office_number) " \
                         "VALUES(?,?,?,?,?,?,?,?,?,?)"
        insertExecute(contents, cursor, insert_records)

    if table == "majorplan":
        insert_records = "INSERT INTO major_plan (name,    courses_names,    courses_numbers,    total_courses,    total_hours,    name_acronym,    total_levels) " \
                         "VALUES(?,?,?,?,?,?,?)"
        insertExecute(contents, cursor, insert_records)

    if table == "level":
        insert_records = "INSERT INTO level (level_code,    level_number,    level_major,    no_of_optional_courses,    no_of_mandatory_courses,    leve_courses_names,    leve_courses_numbers,    min_term_hours,    max_term_hours) " \
                         "VALUES(?,?,?,?,?,?,?,?,?)"
        insertExecute(contents, cursor, insert_records)

    if table == "course":
        insert_records = "INSERT INTO course (course_name,    course_number,    course_description,    course_requirements,    course_dependent,    major,    expected_term,    no_of_hours,    course_type,    no_of_available_sections) " \
                         "VALUES(?,?,?,?,?,?,?,?,?,?)"
        insertExecute(contents, cursor, insert_records)


    if table == "section":
        insert_records = "INSERT INTO section (course_name,    course_number,    section_number,    major,    no_of_hours,    reference_number,    seats,    classroom,    daytime_days,    daytime_time) " \
                         "VALUES(?,?,?,?,?,?,?,?,?,?)"
        insertExecute(contents, cursor, insert_records)
  
    # Commit the changes to the database
    connection.commit()

    # Close the database connection
    connection.close()

#insertExecute(new file, old database, method of the data to write in cursor)
def insertExecute(contents, cursor, insert_records):
    """Executes the INSERT query for multiple rows."""
      # Execute the INSERT query with the data from the CSV file
    cursor.executemany(insert_records, contents)
    #executemany is many executes for the full insert_recordes to the full old file
