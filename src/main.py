from rag import BankingRAG


QUESTIONS = [
    "What is the difference between a savings account and a current account?",
    "What should I do if I see an unauthorized card transaction?",
    "What is an EMI?",
]


if __name__ == "__main__":
    rag = BankingRAG()
    print(f"Indexed {rag.index_documents()} chunks")
    for question in QUESTIONS:
        print(f"\nQ: {question}")
        print(f"A: {rag.answer(question)}")
