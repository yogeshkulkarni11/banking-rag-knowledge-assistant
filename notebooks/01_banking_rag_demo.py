"""Notebook-style demo that can be opened as a Python notebook/script in VS Code."""

from src.rag import BankingRAG

rag = BankingRAG()
rag.index_documents()

question = "What should I do if I see an unauthorized card transaction?"
print(rag.answer(question))

print("\nRetrieved evidence:")
for item in rag.retrieve(question):
    print(f"- {item['source']} | distance={item['distance']:.4f}")
