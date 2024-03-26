from langchain.embeddings import HuggingFaceEmbeddings # Access pre-trained language models from Hugging Face
from langchain.vectorstores import FAISS # Efficiently index and search high-dimensional vectors
from sentence_transformers import SentenceTransformer # Create meanings for sentences or paragraphs
from sklearn.metrics.pairwise import cosine_similarity# Measure similarity between vectors
import numpy as np # Perform numerical computations and array operations
from sklearn.feature_extraction.text import CountVectorizer # Convert text into numerical vectors
import requests # Send HTTP requests to interact with web services or APIs

def run_q(query): #takes a query as input
    
    # Store the path to the FAISS database
    DB_FAISS_PATH = 'C:\\Users\\juri2\\Desktop\\uni\\2023\\second term 2023-2024\\GP2\\new new\\stud_chatbot\\dp_faiss'
    
    # Load a pre-trained sentence embedding model
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2', model_kwargs={'device': 'cpu'})

    # Load the FAISS database with the specified embeddings
    ndb = FAISS.load_local(DB_FAISS_PATH, embeddings)
    
    results = ndb.search(query, k=1,search_type="similarity")  # Search for the most similar document (adjust k for more results)
    res = results[0].page_content # Extract the page content of the most similar result
    return res,query # Return the retrieved content and the original query
    
    # It retrieves the page content of the most similar document.
    # It returns both the retrieved content and the original query, potentially for further processing or display.

#End Function 

def query_model(payload):
    
    # API endpoint for a large language model
    API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    
    # Authentication header for the API
    headers = {"Authorization": "Bearer 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"}

    # Send a POST request to the API with the given payload
    response = requests.post(API_URL, headers=headers, json=payload)
    
    # Return the response as JSON
    return response.json()

    #It takes a payload that likely contains your question
    #It uses the specified API URL and authentication header to send a POST request to the LLM.
    #It sends the payload to the LLM, and recives a response in JSON format
    #acts as a middleman between you and the LLM, facilitating communication and retrieving potential answers or improvements to your questions.
    
#End Function

def improve_query(query):
    
    # Retrieve similar content and the query from the FAISS database and saves it in two varibals 
    sim,query = run_q(query)
    
    # Construct a prompt for the language model, providing context
    prompt = "given this data: \n" + sim + "\n" + "\n" + query  + " Don't add any information but fromat the answer in a humannly answer way."
    
    # Split the retrieved similar content into an array
    sim_arr = sim.split(",")
    
    # Query the language model with the prompt
    output = query_model({"inputs": prompt,})
    
    # Extract the generated text from the response, handling potential errors
    try:
        response = output[0].get('generated_text')
    except:
        response = " " *len(prompt) +  "Sorry I could not understand the question."
    # Remove the prompt from the generated response
    response = response[len(prompt):]
    return response,sim_arr
    # it enhance your query and find an answer
    # In essence, it tries to leverage existing knowledge and clarify your question's context to get a more relevant and accurate answer from the LLM.

#End Function 

def method2(query,sim_arr):
    try:        
        # Filter and format the similar content into a dictionary
        sim_arr = [d for d in sim_arr if " : " in d]
        data = {d.split(" : ")[0].replace("_"," "):d.split(" : ")[1]  for d in sim_arr}
        dk = list(data.keys())
        
        # Prepare the original query and a concise version for comparison
        og_query = query + "\nThe answer is: "
        query = " ".join(query.split(" ")[3:6])

        # Use CountVectorizer to create numerical representations of the text        
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(dk + [query])
        
        # Calculate cosine similarity between the query and the keys in the data
        cosine_similarities = cosine_similarity(X[:-1], X[-1].reshape(1, -1))
        
        # If similarity is low, prompt for a rephrased query
        if max(cosine_similarities) < 0.2: return "Sorry I could not understand the question. can you please rephrase it like this: \nwhat is/are the [what you want to know] of the [what you want to know about]?"
        
        # Find the most similar key and retrieve its corresponding value
        most_similar_index = cosine_similarities.argmax()
        most_similar_string = dk[most_similar_index]
        res = og_query +data[most_similar_string]
        return res
    except:
        return "Sorry I could not understand the question. can you please rephrase it like this: \n what is/are the [what you want to know] of the [what you want to know about]?"
    # function in your code offers an alternative approach to answering your question, but it might not be the primary method and can sometimes prompt you to rephrase your query
    # tries to answer your question by finding relevant keywords in the provided context and matching them to your query based on word usage.
#End Function 
 
def get_answer(query):
    
    # Call improve_query to potentially enhance the query and retrieve similar content
    response,sim_arr = improve_query(query)
    
    # Call method2 to attempt an alternative answering method
    ms = method2(query,sim_arr)
    
    # Return both responses for potential comparison or selection
    return response , ms #the two answers 

    #orchestrates the search for an answer by utilizing complementary methods and providing you with the options it can gather, empowering you to decide the most suitable response
    #acts as the main coordinator in your code, bringing together the efforts of other functions to provide you with an answer to your query
