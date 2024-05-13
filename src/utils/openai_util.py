from openai import OpenAI
import json

import pprint

import os


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_completion(messages=[{"role": "system", "content": "You are a helpful assistant that replies with valid json"}], model="gpt-4-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content






