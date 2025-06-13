import json
import os

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
# from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document


# langchain reads the OPENAI_API_KEY environment variable.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY and len(OPENAI_API_KEY) > 32


SIMILARITY_SCORE_MINIMUM = 0.1


def load_documents() -> list[Document]:
    documents = JSONLoader(
        file_path="./listings.json",
        jq_schema=".[]",
        text_content=False,
    ).load()

    # attach document ids to each document
    for document in documents:
        record_uuid = json.loads(document.page_content)["record_uuid"]
        document.metadata["record_uuid"] = record_uuid

    return documents


def load_vector_db(documents: list[Document]):
    persist_directory = "./listings_chromadb"

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    if os.path.exists(persist_directory):
        print("load_vector_db: existing vector database")
        vector_db = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
        )
    else:
        print("load_vector_db: creating vector database")
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_documents = splitter.split_documents(documents)

        vector_db = Chroma.from_documents(
            documents=split_documents, 
            embedding=embeddings,
            persist_directory="./listings_chromadb",
        )
        vector_db.persist()

    return vector_db


def build_similar_documents(vector_db, answers: list[str]) -> dict[str, set]:
    documents = dict()
    for index, answer in enumerate(answers):
        # similar_documents = vector_db.similarity_search(answer, k=3)
        similar_documents = vector_db.similarity_search_with_relevance_scores(answer, k=10)
        for document, score in similar_documents:
            if score >= SIMILARITY_SCORE_MINIMUM:
                record_uuid = document.metadata["record_uuid"]
                if not record_uuid in documents:
                    documents[record_uuid] = set()
                documents[record_uuid].add(index)
    return documents


def filter_similar_documents(documents: dict[str, set], min_matches: int) -> dict[str, set]:
    filtered_documents = {k:v for k, v in documents.items() if len(v) >= min_matches}
    return filtered_documents


# def something():
#     llm = ChatOpenAI(
#         model="gpt-4o", 
#         temperature=0.25, 
#         max_completion_tokens=2000
#     )
#     query = "moderately priced urban bungalow"
#     similar_documents = db.similarity_search(query, k=3)
#     prompt = PromptTemplate(
#         template="Return one or more document ID values as a JSON list of strings for the question: {query}\nContext: {context}",
#         input_variables=["query", "context"],
#     )

#     chain = load_qa_chain(llm, prompt=prompt, chain_type="stuff")
#     result = chain.invoke(input={"input_documents": similar_documents, "query": query})
#     print(result)
#     # print(json.loads(result))


def main():
    subjects = [
        "size",
        "factors",
        "amenities",
        "transportation",
        "neighborhood",
    ]

    questions = [   
        "How big do you want your house to be?",
        "What are 3 most important things for you in choosing this property?",
        "Which amenities would you like?",
        "Which transportation options are important to you?",
        "How urban do you want your neighborhood to be?",
    ]

    answers = [
        "A comfortable three-bedroom house with a spacious kitchen and a cozy living room.",
        "A quiet neighborhood, good local schools, and convenient shopping options.",
        "A backyard for gardening, a two-car garage, and a modern, energy-efficient heating system.",
        "Easy access to a reliable bus line, proximity to a major highway, and bike-friendly roads.",
        "A balance between suburban tranquility and access to urban amenities like restaurants and theaters.",
    ]

    documents = load_documents()
    documents_by_uuid = {doc.metadata["record_uuid"]:json.loads(doc.page_content) for doc in documents}

    vector_db = load_vector_db(documents)

    similar_documents = build_similar_documents(vector_db, answers)
    filtered_documents = filter_similar_documents(similar_documents, 3)

    from pprint import pprint
    pprint(filtered_documents)


if __name__ == "__main__":
    main()