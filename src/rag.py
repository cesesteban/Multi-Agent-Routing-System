import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import Config

class RAGManager:
    """Gestiona la carga de documentos, creación de índices y recuperación para RAG."""
    
    def __init__(self):
        # Utiliza embeddings locales para no requerir API Key de OpenAI
        print("  [RAG] Inicializando embeddings locales (HuggingFace)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.vectorstores = {}

    def _get_vectorstore(self, department: str):
        """Crea o recupera un vectorstore para un departamento específico."""
        if department in self.vectorstores:
            return self.vectorstores[department]
        
        # Mapeo de departamentos a rutas
        paths = {
            "RRHH": Config.DATA_PATH_RRHH,
            "TECNOLOGIA": Config.DATA_PATH_TECH,
            "FINANZAS": Config.DATA_PATH_FINANZAS,
            "RECLAMOS": Config.DATA_PATH_RECLAMOS,
            "GENERAL": Config.DATA_PATH_GENERAL
        }
        
        path = paths.get(department)
        if not path or not os.path.exists(path) or not os.listdir(path):
            print(f"WARNING: No hay documentos o ruta inválida para {department} en {path}")
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
        valid_departments = ["RRHH", "TECNOLOGIA", "FINANZAS", "RECLAMOS", "GENERAL"]
        if department not in valid_departments:
            return ""
            
        vectorstore = self._get_vectorstore(department)
        if not vectorstore:
            return ""
            
        # Simulación de recuperación simple
        docs = vectorstore.similarity_search(query, k=2)
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
