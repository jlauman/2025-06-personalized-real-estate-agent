import json
import os

from langchain.document_loaders.json_loader import JSONLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain


# langchain reads the OPENAI_API_KEY environment variable.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY and len(OPENAI_API_KEY) > 32

documents = JSONLoader(
    file_path="./home_profiles.json",
    jq_schema=".[]",
    text_content=False,
).load()

# attach document ids to each document
for document in documents:
    id = json.loads(document.page_content)["record_uuid"]
    document.id = id

splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
split_documents = splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
db = Chroma.from_documents(split_documents, embeddings)

query = "moderately priced urban bungalow."

similar_documents = db.similarity_search(query, k=1)
prompt = PromptTemplate(
    template="Return one or more document ID values as a JSON list of strings for the question: {query}\nContext: {context}",
    input_variables=["query", "context"],
)

llm = OpenAI(temperature=0)
chain = load_qa_chain(llm, prompt=prompt, chain_type="stuff")
result = chain.run(input_documents=similar_documents, query=query)
print(json.loads(result))
