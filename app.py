import json
import asyncio
from pydantic import BaseModel
from typing import List
import openai
import os 
from openai import AsyncOpenAI
from dotenv import load_dotenv
from serp import search_google_web_automation
from my_functions import get_article_from_url, generate_ideas

# Load environment variables
load_dotenv()

# Constants
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY is None:
    raise ValueError("Please set the OPENAI_API_KEY in .env file.")

openai.api_key = OPENAI_API_KEY
async_openai_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
)

# Template for the prompt to be used later
prompt = "extract 5-10 content ideas from the [post], and return the list in json format, [post]: {post}"

# Pydantic model for data validation
class Ideas(BaseModel):
    ideas: List[str]

# Function to generate paragraphs for each idea using OpenAI's GPT-3
async def generate_paragraph(idea):
    response = openai.Completion.create(
        prompt=idea,
        max_tokens=150,  # Adjust as needed
        temperature=0.7  # Adjust for creativity level
    )
    paragraph = response.choices[0].text.strip()
    return paragraph

# Main asynchronous function
async def main():
    search_query = "AI in marketing"
    NUMBER_OF_RESULTS = 10

    try:
        search_results = search_google_web_automation(search_query, NUMBER_OF_RESULTS)
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return

    all_ideas_with_paragraphs = []

    for result in search_results:
        try:
            result_url = result["url"]
            result_content = get_article_from_url(result_url)

            if result_content:
                result_prompt = prompt.format(post=result_content)
                ideas_object = await generate_ideas(result_prompt, Ideas)

                if ideas_object and ideas_object.ideas:
                    for idea in ideas_object.ideas:
                        paragraph = await generate_paragraph(idea)
                        all_ideas_with_paragraphs.append({'idea': idea, 'paragraph': paragraph})
        except Exception as e:
            print(f"Error processing search result {result}: {e}")

    json_output = json.dumps(all_ideas_with_paragraphs, indent=4)
    print(json_output)

if __name__ == "__main__":
    asyncio.run(main())
