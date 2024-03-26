import numpy as np #NumPy library, powerful tool for numerical computing, assigning it to np, allow access its functionalities more easily in your code.
import os #import the OS modle, gives functions for interacting with the operating system (acsseing and editing files)
import json #import jason modle,for JSON is common format for storing and exchanging data.
#JSON is perfect for storing temporary data, used for transmitting data in web applications (sending some data from the server to the client, so it can be displayed on a web page).
import sqlite3 #used for interacting with SQLite databases, SQLite is lightweight, embedded database can be used to store and manage data within Python applications.
# langchain offers a rich set of features for natural language processing (NLP)
from langchain.embeddings import HuggingFaceEmbeddings # provides access to pre-trained text embeddings from Hugging Face's, often used for tasks like text classification, semantic similarity, and information retrieval.
from langchain.vectorstores import FAISS # library for efficient similarity search and clustering of dense vectors. It's often used to store and retrieve text embeddings quickly and scalably.
from langchain.document_loaders import PyPDFLoader, DirectoryLoader 
#PyPDFLoader: This class is designed for loading text content from PDF files.
#DirectoryLoader: This class loads text content from files within a specified directory.
from langchain.text_splitter import RecursiveCharacterTextSplitter # used for splitting text into smaller chunks or tokens, which can be useful for language modeling tasks or other NLP (Natural Language Processing) applications.

def ceate_db(): #Creates a FAISS database!, from text data extracted from a SQLite database.
    DB_FAISS_PATH = 'dp_faiss' #object theat holds the folder of Faiss class info
    
    if len(os.listdir('dp_faiss')) > 0:#Check if the FAISS database already exists
        return # If it does, return without doing anything further (if there is )
    
    conn = sqlite3.connect('instance\\university.db') #load the SQLite database in the object conn
    c = conn.cursor() #loop through every table and get every row and column

    #get the data from the SQLlite table names
    c.execute("SELECT name FROM sqlite_master WHERE type='table';") #.exscute() allows us to use SQL commands to the DB
    tables = c.fetchall() #gets all rows and saves them in tables
    #loop through every table
    full_text = ""
    for table in tables: #loop for every table in univrsity.db except the stats table
        #get the column names
        if table[0] == "stats": # Skip the "stats" table
            continue
        c.execute("SELECT * FROM " +table[0] ) #not a stats tabke (go to the )
        #get the column names
        columns = [description[0] for description in c.description] #extracts the column names from the cursor description and stores them in a list named columns
        text = f"{table[0]} : \n" #variable text will now hold the value of the string, (assuming table[0] holds the value "users"): -users : \n- 
        #loop through every row
        for row in c.fetchall():# fetch the table fully 
            r = ""
            for i in range(len(row)): #load a row in the r varibal
                r+= f"{columns[i]} : {row[i]}, " #using the colums varibal from before to use as a pointer 
            #LOOP END
            text += f"{r}\n" # add the r varibal rows in the text varibal
        #LOOP END
        full_text += text + "\n" # full table
    #LOOP END
    
    file_path = f"data\data.md" #store the SQL data and store it in the data.md file
    #why use the .md file type here ? one of the most widely used formats for storing formatted data. It easily integrates with Web technologies
    
    # Save extracted text data as a Markdown file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(full_text) #put the full_text in the data.md file 
    os.makedirs('data', exist_ok=True) #creates a folder called data but if there is a one already then they don't create one
    DATA_PATH = 'data/' #creates a variable named DATA_PATH and assigns it the value 'data/'. This variable will be used later in the code to refer to the "data" directory
    DB_FAISS_PATH = 'dp_faiss'#creats variable named DB_FAISS_PATH and assigns it the value 'dp_faiss', points to the location where the FAISS database
    
        # Load text from the Markdown file
    print('Loading documents...')
    loader = DirectoryLoader(DATA_PATH, glob='*.md',)
    print('Splitting documents...')
    documents = loader.load()
        # Split text into smaller chunks
    print("splitting documents")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
        # Generate text embeddings using a pre-trained model
    print("creating embeddings")
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})
        
        # Create a FAISS database for efficient retrieval and similarity search
    db = FAISS.from_documents(texts, embeddings)
        # Save the FAISS database
    print("saving db")
    db.save_local(DB_FAISS_PATH)