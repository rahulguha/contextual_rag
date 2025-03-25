import os
import json
from typing import List, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import anthropic
from dotenv import load_dotenv
load_dotenv()
# anthropic_api_key = ""
# if anthropic_api_key is None:
#             anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
def create_chunks_from_file(file_path: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[str]:
    """
    Reads a text file and splits it into chunks for RAG.
    
    :param file_path: Path to the text file.
    :param chunk_size: Maximum chunk size in characters.
    :param chunk_overlap: Number of overlapping characters between chunks.
    :return: List of text chunks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    episode_name=""
    podcast_name=""
    episode_link=""
    doc_text=""
    with open(file_path, "r", encoding="utf-8") as file:
        doc_text = file.read()
        js = json.loads(doc_text)
        episode_name = js["Episode Name"]
        podcast_name = js["Podcast Name"]
        episode_link = js["Episode Link"]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        length_function=len
    )
    
    chunks = text_splitter.split_text(doc_text)
    print(f"Number of chunks: {len(chunks)}")
    updated_chunks = []
    chunk_num = 1
    for c in chunks: # [:5]:
        contextualized_text, usage = situate_context(doc_text, c)
        chunk_num += 1
        print(f"Chunk #: {chunk_num}, Input Tokens: {usage.input_tokens} , Output Tokens: {usage.output_tokens} , Total Tokens: {usage.input_tokens + usage.output_tokens}, Cache Read: {usage.cache_read_input_tokens}, Cache Creation: {usage.cache_creation_input_tokens} ")
        c = create_json_object(chunk_num, episode_name, podcast_name, episode_link, contextualized_text, c)
        updated_chunks.append(c)
    return updated_chunks

def create_json_object(chunk_num, episode_name, podcast_name, episode_link,context, chunk_text):
    """
    Creates a JSON object (Python dictionary) with specified data.
    Returns:
        A Python dictionary representing the JSON object.
    """

    data = {
         "Chunk Number": chunk_num,
        "Episode Name": episode_name,
        "Podcast Name": podcast_name,
        "Episode Link": episode_link,
        "Context": context,
        "chunk_text": chunk_text
    }
    return data


def situate_context(doc: str, chunk: str) -> tuple[str, Any]:
        DOCUMENT_CONTEXT_PROMPT = """
        <document>
        {doc_content}
        </document>
        """

        CHUNK_CONTEXT_PROMPT = """
        Here is the chunk we want to situate within the whole document
        <chunk>
        {chunk_content}
        </chunk>

        Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
        Answer only with the succinct context and nothing else.
        """

        # response = self.anthropic_client.beta.prompt_caching.messages.create(
        response = anthropic_client.beta.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.0,
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": DOCUMENT_CONTEXT_PROMPT.format(doc_content=doc),
                            "cache_control": {"type": "ephemeral"} #we will make use of prompt caching for the full documents
                        },
                        {
                            "type": "text",
                            "text": CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk),
                        },
                    ]
                },
            ],
            extra_headers={"anthropic-beta": "prompt-caching-2024-07-31"}
        )
        return response.content[0].text, response.usage