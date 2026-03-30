import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from config import Config

class RAGManager:
    """Gestiona la carga de documentos, creación de índices y recuperación para RAG."""
    
    def __init__(self, provider="openai"):
        self.embeddings = OpenAIEmbeddings() # Por defecto usa OpenAI, se puede parametrizar
        self.vectorstores = {}

    def _get_vectorstore(self, department: str):
        """Crea o recupera un vectorstore para un departamento específico."""
        if department in self.vectorstores:
            return self.vectorstores[department]
        
        path = Config.DATA_PATH_RRHH if department == "RRHH" else Config.DATA_PATH_TECH
        
        if not os.path.exists(path) or not os.listdir(path):
            print(f"WARNING: No hay documentos en {path}")
            return None
            
        loader = DirectoryLoader(path, glob="*.md", loader_cls=TextLoader)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = text_splitter.split_documents(docs)
        
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=self.embeddings,
            collection_name=f"{department.lower()}_knowledge"
        )
        
        self.vectorstores[department] = vectorstore
        return vectorstore

    def retrieve_context(self, query: str, department: str) -> str:
        """Busca información relevante en el vectorstore del departamento."""
        if department not in ["RRHH", "TECNOLOGIA"]:
            return ""
            
        vectorstore = self._get_vectorstore(department)
        if not vectorstore:
            return ""
            
        # Simulación de recuperación simple
        docs = vectorstore.similarity_search(query, k=2)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
