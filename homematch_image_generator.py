import os
import json
import time
import httpx

from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAI

# after images are generated, scale them down to reduce bytes.
# magick mogrify -resize 512x512 *.jpg

# langchain reads the OPENAI_API_KEY environment variable.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
assert OPENAI_API_KEY and len(OPENAI_API_KEY) > 32


# DallEAPIWrapper does not support gpt-image-1, and
# is flaky -- this script can be safely restarted.
def main():
    homes = []
    with open("listings.json", "r") as file:
        homes = json.load(file)
    
    for home in homes:
        record_uuid = home["record_uuid"]
        description = home["home_description"]
        file_name = f"listing_images/{record_uuid}.jpg"

        if os.path.exists(file_name):
            continue

        print(description, "\n")

        openai_llm = OpenAI(temperature=0.9)
        prompt = PromptTemplate(
            input_variables=["description"],
            template="""
                Generate realistic photo of the front of a residential dwelling.
                Do not render indoor furniture outside of the house.
                Ensure all rooms of the house are surrounded by walls.
                The home is described as: {description}
            """
        )

        chain = prompt | openai_llm

        image_url = DallEAPIWrapper(
            model="dall-e-3",
            quality="standard",
            size="1024x1024"
        ).run(chain.invoke({"description": description}))
        print(image_url, "\n")

        response = httpx.get(image_url)
        with open(file_name, "wb") as file:
            file.write(response.content)
        
        time.sleep(5)


if __name__ == "__main__":
    main()