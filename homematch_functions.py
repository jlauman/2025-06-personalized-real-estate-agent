import json
import os

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
# from langchain.prompts import PromptTemplate
# from langchain.chains.question_answering import load_qa_chain
from langchain_core.prompts import ChatPromptTemplate
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
        similar_documents = vector_db.similarity_search_with_relevance_scores(answer, k=5)
        for document, score in similar_documents:
            if score >= SIMILARITY_SCORE_MINIMUM:
                record_uuid = document.metadata["record_uuid"]
                if not record_uuid in documents:
                    documents[record_uuid] = set()
                documents[record_uuid].add(index)
    return documents


def filter_similar_documents(documents: dict[str, set], min_matches: int) -> dict[str, set[int]]:
    filtered_documents = {k:v for k, v in documents.items() if len(v) >= min_matches}
    return filtered_documents


def personalize_listing(listing: str, answers: list[str]):
    llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0.25, 
        max_completion_tokens=2000,
        max_retries=2,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful and knowledgeable real estate agent."),
        ("human", """
            Generate a description of the real estate listing (below as "Real Estate Listing") 
            that personalizes the listing for the customer based on their search criteria
            (below as "Search Criteria"). Parse the real estate listing as a JSON document.
            When generating the personalized description retain the factual information from the
            real estate listing. Do not use the term "search criteria" in the description.
         
            Real Estate Listing:
            {listing}
         
            Search Criteria:
            {answers}
         """),
    ])

    chain = prompt | llm
    result = chain.invoke({
        "listing": listing,
        "answers": "\n".join(answers),
    })
    if result.content:
        return result.content
    return "Personalized descripton is not available."


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
    documents_by_uuid: dict[str, str] = {
        doc.metadata["record_uuid"]:doc.page_content for doc in documents
    }

    vector_db = load_vector_db(documents)

    similar_documents_ids = build_similar_documents(vector_db, answers)
    filtered_documents_ids = filter_similar_documents(similar_documents_ids, 3)

    print("=======================================")
    print(filtered_documents_ids)

    personalized_descriptions = {}
    for record_uuid, answer_indexes in filtered_documents_ids.items():
        listing = documents_by_uuid[record_uuid]
        filtered_answers = [answers[i] for i in answer_indexes]
        result = personalize_listing(listing, filtered_answers)
        personalized_descriptions[record_uuid] = {
            "record_uuid": record_uuid,
            "filtered_answers": filtered_answers,
            "description": result,
        }

    print("----------------------------------------")
    print(personalized_descriptions)


if __name__ == "__main__":
    main()