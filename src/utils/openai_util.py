from openai import OpenAI
import json

import pprint

import os


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_completion(prompt, system_prompt="You are a helpful assistant, that replies with a valid JSON", model="gpt-4-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt },
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    return response.choices[0].message.content
