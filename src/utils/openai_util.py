import base64

from openai import OpenAI
import json
import requests

import pprint

import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a helpful solution architect with immense knowlege of devops, 
    infrastructure. Use the pip package, `diagrams`, and generate the code for an infrastructure. diagram
    for the infra described below. 
    Remember in `diagrams` cloud provider imports are lower case. aws not AWS etc. 
    Every grouping of elements is a Cluster (with Cluster("VPC"): etc (imported as diagrams.Cluster)
    IMPORTANT & CRITICAL NOTE:
     1) The code and imports should be wrapped in a well formatted python function, which can be written to a file.
     2) The response has to be a valid JSON of format: {func: <python code>, fname: <name of function>}
     3) The name of the diagram should always be Infra Diagram.
     4) ALL IMPORTS MUST BE INSIDE the FUNCTION
     5) The function should return the diagram object (Eg: 
     with Diagram("Infra Diagram", show=False, filename='outputs/filebro') as diag:
        dns = Route53("Route53")
     return diag
     6) func: Should only be a python method WITH NO INDENT
     """

GEN_TF_CODE_SYSTEM_PROMPT = """Below is an architecture diagram's code generated in the diagrams library in python.
I want you to convert this code to terraform code. You are free to make any assumptions,
try to make the code parametrised, so we can fill them with values. RESPOND WITH ONLY THE CODE, NO explanation text.
"""


def get_completion(messages=[{"role": "system", "content": "You are a helpful assistant that replies with valid json"}],
                   model="gpt-4-turbo",
                   response_format={"type": "json_object"},
                   stream=False):
    print(model, messages, response_format)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        response_format=response_format,
        stream=stream
    )
    return response


# Path to your image

def get_terraform_code(base64_image='', model="gpt-4o"):
    base64_image = base64.b64encode(base64_image).decode('utf-8')

    # Getting the base64 string
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text",
                     "text": "Convert this architectural diagram to terraform code. You are free to make any assumptions, try to make the code parametrised, so we can fill them with values. RESPOND WITH ONLY THE CODE, NO explanation text"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ],
            }
        ],
        stream=True
    )

    return response
