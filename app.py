from dotenv import load_dotenv
load_dotenv()
import os
from chunking import *
from vector_db import *
from rerank import *
from llm_response import *

import pprint

import anthropic

client = anthropic.Anthropic(
    # This is the default and can be omitted
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

def save_jsonl(data: list, filename: str):
    """
    Saves a list of dictionaries to a JSONL (JSON Lines) file.

    :param data: List of dictionaries to save.
    :param filename: Name of the JSONL file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for entry in data:
                json.dump(entry, f)
                f.write("\n")  # Each entry is on a new line
        print(f"Saved {len(data)} records to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")

# Initialize the VectorDB
base_db = VectorDB("base_db")

if base_db.load_vector_db():
     print("db loaded")
     q = "who is significant other ?"
     reranked_chunks = retrieve_rerank(q,base_db,5)
     chat = LLMResponse(client)
     print( chat.generate_response(q, reranked_chunks) ) 
else:
    print("db not loaded")
    # file_path = "data/local/birthright_citizenship.txt"
    file_path_list=[]
    folder_path = "data/local/Ted1/"
    all_chunks = []
    for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                file_path_list.append(file_path)
    chunk_file_path = ""
    # # chunk
    for f in file_path_list:
        chunks = create_chunks_from_file(
            file_path= f,
            chunk_size=900,
            chunk_overlap=100
            )
        chunk_file_path = f+ "_chunk.jsonl"
        save_jsonl(chunks, chunk_file_path)
        all_chunks.extend(chunks)
        print (len(chunks))
        
        


    # # # Load and process the data
    base_db.load_data(all_chunks)
