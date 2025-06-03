import os
import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from pprint import pprint

# langchain reads the OPENAI_API_KEY environment variable.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY and len(OPENAI_API_KEY) > 32


class Home(BaseModel):
    record_uuid: str = Field(description="random uuid for record identification")
    price_us_dollars: int = Field(description="price of the home in US dollars")
    lot_size_acres: str = Field(description="lot size in acres")
    house_size_sq_ft: int = Field(description="house size in square feet")
    bedroom_count: int = Field(description="number of bedrooms")
    bathroom_count: int = Field(description="number of bathrooms")
    home_description: str = Field(description="description of the house")
    area_description: str = Field(description="description of the neighborhood")


def main():
    model = ChatOpenAI(model="o4-mini")

    query = """
    Generate a list of 3 homes typical for an urban and suburban area of 1 million people.
    The home prices should range from $250k to $750k.
    The description of the house should be at least 3 sentences and include a description of the kitchen, bedrooms, and overall finish of the house.
    The description of the neighborhood should be at least 2 sentences and include surrounding businesses and access to public transportation.
    """

    parser = JsonOutputParser(pydantic_object=Home)

    prompt = PromptTemplate(
        template="Answer the query like a helpful real estate agent.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser

    output = chain.invoke({"query": query})

    pprint(output)
    with open("home_profiles.json", "w") as file:
        json.dump(output, file)


if __name__ == "__main__":
    main()