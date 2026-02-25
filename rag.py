import os
import json
from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain.schema import Document

class DocumentProcessor:
    """Processa e indexa documentos para RAG"""

    def __init__(self, docs_path: str = "./docs", model_name: str = "nomic-embed-text"):
        self.docs_path = docs_path
        self.model_name = model_name
        self.embeddings = OllamaEmbeddings(model=model_name)
        self.vector_store = None
        self.documents = []

    def load_documents(self) -> List[Document]:
        """Carrega documentos da pasta"""
        os.makedirs(self.docs_path, exist_ok=True)

        if not os.path.exists(self.docs_path) or not os.listdir(self.docs_path):
            print(f"⚠️  Nenhum documento encontrado em {self.docs_path}")
            return []

        documents = []

        # Carregar PDFs
        pdf_files = list(Path(self.docs_path).glob("**/*.pdf"))
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                documents.extend(docs)
                print(f"✓ PDF carregado: {pdf_file.name}")
            except Exception as e:
                print(f"✗ Erro ao carregar {pdf_file.name}: {e}")

        # Carregar TXT e MD
        for ext in ["*.txt", "*.md"]:
            text_files = list(Path(self.docs_path).glob(f"**/{ext}"))
            for text_file in text_files:
                try:
                    loader = TextLoader(str(text_file), encoding='utf-8')
                    docs = loader.load()
                    documents.extend(docs)
                    print(f"✓ Arquivo carregado: {text_file.name}")
                except Exception as e:
                    print(f"✗ Erro ao carregar {text_file.name}: {e}")

        self.documents = documents
        return documents

    def chunk_documents(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        """Divide documentos em chunks"""
        if not self.documents:
            self.load_documents()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        chunks = splitter.split_documents(self.documents)
        print(f"✓ {len(chunks)} chunks criados")
        return chunks

    def create_vector_store(self, chunks: Optional[List[Document]] = None) -> FAISS:
        """Cria índice FAISS"""
        if chunks is None:
            chunks = self.chunk_documents()

        if not chunks:
            print("⚠️  Nenhum chunk disponível para indexação")
            return None

        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        print(f"✓ Vector store criado com {len(chunks)} documentos")
        return self.vector_store

    def save_vector_store(self, path: str = "./vector_store"):
        """Salva índice FAISS em disco"""
        if self.vector_store:
            self.vector_store.save_local(path)
            print(f"✓ Vector store salvo em {path}")
        else:
            print("⚠️  Nenhum vector store para salvar")

    def load_vector_store(self, path: str = "./vector_store") -> Optional[FAISS]:
        """Carrega índice FAISS do disco"""
        try:
            self.vector_store = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
            print(f"✓ Vector store carregado de {path}")
            return self.vector_store
        except Exception as e:
            print(f"✗ Erro ao carregar vector store: {e}")
            return None

    def search(self, query: str, k: int = 3) -> List[Document]:
        """Busca documentos relevantes"""
        if not self.vector_store:
            self.create_vector_store()

        if not self.vector_store:
            return []

        results = self.vector_store.similarity_search(query, k=k)
        return results

    def build_context(self, query: str, k: int = 3) -> str:
        """Constrói contexto a partir dos documentos"""
        results = self.search(query, k=k)

        if not results:
            return "Nenhum documento relevante encontrado."

        context = "Contexto dos documentos:\n\n"
        for i, doc in enumerate(results, 1):
            context += f"[Documento {i}]\n{doc.page_content}\n\n"

        return context

