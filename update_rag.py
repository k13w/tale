#!/usr/bin/env python3
"""
Script para atualizar o Vector Store da RAG
Uso: python3 update_rag.py
"""

import sys
from rag import DocumentProcessor

def main():
    print("=" * 60)
    print("🔄 ATUALIZANDO VECTOR STORE DA RAG")
    print("=" * 60)

    try:
        # Criar processador
        processor = DocumentProcessor(docs_path="./docs")

        # Carregar documentos
        print("\n📚 Passo 1: Carregando documentos da pasta ./docs...")
        docs = processor.load_documents()

        if not docs:
            print("❌ Nenhum documento encontrado!")
            print("   Adicione arquivos .txt, .md ou .pdf na pasta ./docs")
            return 1

        print(f"   ✅ {len(docs)} documento(s) carregado(s)")

        # Criar chunks
        print("\n✂️  Passo 2: Dividindo documentos em chunks...")
        chunks = processor.chunk_documents(chunk_size=1000, chunk_overlap=200)
        print(f"   ✅ {len(chunks)} chunks criados")

        # Criar vector store
        print("\n🔍 Passo 3: Criando embeddings e vector store...")
        print("   (isso pode demorar alguns segundos...)")
        vector_store = processor.create_vector_store(chunks)

        if not vector_store:
            print("❌ Erro ao criar vector store!")
            return 1

        # Salvar vector store
        print("\n💾 Passo 4: Salvando vector store em disco...")
        processor.save_vector_store("./vector_store")

        print("\n" + "=" * 60)
        print("✅ VECTOR STORE ATUALIZADO COM SUCESSO!")
        print("=" * 60)
        print(f"\n📊 Estatísticas:")
        print(f"   - Documentos processados: {len(docs)}")
        print(f"   - Chunks indexados: {len(chunks)}")
        print(f"   - Localização: ./vector_store/")
        print(f"\n💡 Agora sua RAG está atualizada com a documentação mais recente!")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

