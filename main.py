from datetime import timedelta
from timeit import default_timer as timer
import os
import asyncio
import glob
from os import getcwd
from openai import AsyncOpenAI
from base64 import b64encode
from dotenv import load_dotenv

load_dotenv()
API_HOST: str | None = os.getenv("API_HOST")
API_PORT: str | None = os.getenv("API_PORT")
API_VERSION: str | None = os.getenv("API_VERSION")
API_KEY: str | None = os.getenv("API_KEY")
MODEL_NAME: str | None = os.getenv("MODEL_NAME")  # Model must support vision


def prompt_user(dir_name: str, extension: str) -> str | None:
    try:
        files = glob.glob(dir_name + extension)
        for idx, x in enumerate(files):
            print(f"{idx}: {x}")
        user_selection = input("Enter the number corresponding to your choice: ")
        selected_file = files[int(user_selection)]
        return selected_file

    except Exception as e:
        print(f"Invalid selection. {e}. Please try again.")
        return None


def main():
    user_selection = prompt_user(getcwd() + "/images/", "*.jpg")
    if user_selection is not None:
        prompt = """ Act as a precise data extraction system analyzing the image provided. Extract ONLY non-null, valid information explicitly visible in the image content.
        Analyze the input image thoroughly for explicit, observable data points relevant to the task domain (e.g., text segments, numbers, timestamps).
        Exclude any speculative responses ("could be..."), assumptions ("might represent..."), or empty fields ("N/A", "none", "not found").
        Format valid data strictly into a structured JSON object with keys corresponding to required fields (e.g. "height" or "address") only.

        If a field cannot be validated (e.g., missing text, ambiguous elements), omit it entirely from the response instead of including placeholder values like null or "not found".
        Consideration:
        - The image containing the data maybe be surrounded by a larger object

        Do not wrap the json codes in JSON markers
        """

        start = timer()
        asyncio.run(process_image(prompt, user_selection))
        end = timer()
        print(f"Time taken: {timedelta(seconds=end - start)}")


def base64_image(file: str) -> str | None:
    if file is not None or file != "":
        with open(file, "rb") as image_file:
            encoded_image = b64encode(image_file.read()).decode("utf-8")
        return f"data:image/jpg;base64,{encoded_image}"


async def process_image(prompt: str, selected_file: str):
    base64 = base64_image(selected_file)
    if base64 is not None:
        client = AsyncOpenAI(
            api_key=f"{API_KEY}", base_url=f"{API_HOST}:{API_PORT}/{API_VERSION}"
        )
        response = await client.chat.completions.create(
            model=f"{MODEL_NAME}",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": base64},
                        },
                    ],
                }
            ],
        )
        llm_response = response.choices[0].message.content
        assert llm_response is not None
        llm_response = llm_response.strip()
        print(llm_response)


if __name__ == "__main__":
    main()
