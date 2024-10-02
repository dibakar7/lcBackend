import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import AzureOpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
OPENAI_API_KEY = "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"
# os.environ["OPENAI_API_VERSION"] = "2024-05-01-preview"
# os.environ["AZURE_OPENAI_ENDPOINT"] = "https://tecosys.openai.azure.com/"
# os.environ["AZURE_OPENAI_API_KEY"] = OPENAI_API_KEY
file_path = os.path.join(os.path.dirname(__file__), 'IPC.pdf')
loader = PyPDFLoader(file_path)
documents = loader.load()
# Split the text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=200)
texts = text_splitter.split_documents(documents)
embeddings = OpenAIEmbeddings(api_key="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")
faiss_db = FAISS.from_documents(texts, embeddings)
faiss_db.save_local("ipc_vector_db_open")
