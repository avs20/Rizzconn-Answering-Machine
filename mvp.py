import sqlite3
from sentence_transformers import SentenceTransformer
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.rerankers import ColbertReranker
from send_openai import get_coherent_answer
# Initialize the embedding model
model_name = "BAAI/bge-small-en-v1.5"
embedding_model = SentenceTransformer(model_name)

# Create a Model to store attributes for filtering

# Create a Model to store attributes for filtering
# class Document(LanceModel):
#     text: str = model.SourceField()
#     vector: Vector(384) = model.VectorField()
#     category: str

# Initialise the embedding model
model_registry = get_registry().get("sentence-transformers")
model = model_registry.create(name="BAAI/bge-small-en-v1.5")

class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(384) = model.VectorField()
    filename: str
    username: str



# Connect to the LanceDB and create a table
db = lancedb.connect(".my_db")
tbl = db.create_table("my_table", schema=Document, exist_ok=True)

# Function to read chunks from the SQLite database
def read_chunks_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT talkname, filename, chunk, username FROM text_chunks")
    chunks = cursor.fetchall()
    conn.close()
    return chunks

# # Read chunks from the database
# db_path = 'rag.db'  # Replace with your actual database path
# chunks = read_chunks_from_db(db_path)

# # Prepare documents for embedding and storing in LanceDB
# docs = []
# for talkname, filename, chunk, username in chunks:
#     docs.append({
#         "text": chunk,
#         "filename": talkname,
#         "username": username
#     })

# # Add documents to the LanceDB table
# tbl.add(docs)
# # Generate the full-text (tf-idf) search index
# tbl.create_fts_index("text")
# Initialise a reranker
reranker = ColbertReranker()

# Function to log the interaction to the SQLite database
def log_interaction(question, chunks, coherent_answer, feedback=None, additional_feedback=None, db_path='rag.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interactions (question, chunks, coherent_answer, feedback, additional_feedback)
        VALUES (?, ?, ?, ?, ?)
    ''', (question, "\n\n".join(chunks), coherent_answer, feedback, additional_feedback))
    conn.commit()
    conn.close()


# Function to call your system API and get the response
def search_question(question):
    query = question
    results = (tbl.search(query, query_type="hybrid")  # Hybrid means text + vector
               .limit(10)  # Get 10 results from first-pass retrieval
               .rerank(reranker=reranker))
    
    if results:
        documents = results.to_pydantic(Document)
        context_chunks = [doc.text for doc in documents]
        result =  get_coherent_answer(question, context_chunks)
        log_interaction(question, context_chunks, result)
        return result
    else:
        return "No answer found."
    # if results:
    #     documents = results.to_pydantic(Document)
    #     return [[doc.text, doc.filename, doc.username] for doc in documents]
    # else:
    #     return []

# # Define the query
# query = "What is Chihiro's new name given to her by the witch?"

# # Perform the search and rerank the results
# results = (tbl.search(query, query_type="hybrid")  # Hybrid means text + vector
#            .limit(10)  # Get 10 results from first-pass retrieval
#            .rerank(reranker=reranker)
#           )

# # Print the results
# print(results)
# print(results.to_pydantic(Document))
