import datetime

import streamlit as st

# We will use the `diagrams` package to generate a diagram for the described infrastructure.
# First, let's import the necessary modules from `diagrams`.

import json
from src.utils.openai_util import get_completion
from dotenv import load_dotenv
load_dotenv()

def invoke_dynamic_function_from_string(func_str, func_name, *args, **kwargs):
    # Create a dictionary for globals and locals
    try:

        global_vars = {}
        local_vars = {}

        # Execute the function string in the global namespace
        exec(func_str, global_vars, local_vars)

        # Extract the function from local variables
        func = local_vars.get(func_name)
        if not func:
            raise ValueError(f"Function {func_name} not found in the provided code.")

        # Call the function with the provided arguments
        return func(*args, **kwargs), None

    except Exception as error:
        print("Error in dynamic function invocation\n")
        print(func_str)
        return None, error

def run_functions_static(function_descriptor):
    function_string = function_descriptor['func']
    function_name = function_descriptor['fname']
    result, error = invoke_dynamic_function_from_string(function_string, function_name)
    return result, error

def write_or_append_to_file_in_dir(file_name, content, dir_path):
    with open(f"{dir_path}/{file_name}", "a") as f:
        f.write(content)

user = "user_1"
prompt =  st.text_input("Enter your prompt", value =None)
def show():
    system_prompt = """You are a helpful assistant with immense knowlege of devops, 
    infrastructure. Use the pip package, `diagrams`, and generate the code for an infrastructure. diagram
    for the infra described below. 
    Remember in `diagrams` cloud provider imports are lower case. aws not AWS etc. Every grouping of elements is a 
    Cluster (with Cluster("VPC"): etc
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
    messages=[
        {"role": "system", "content": system_prompt },
        {"role": "user", "content": prompt}
    ]
    res = get_completion(messages=messages)
    res_json = json.loads(res)
    return res_json, messages

@st.experimental_fragment
def render_code(code, messages_list):
    st.code(code['func'])
    #filename of format user_1_timestamp
    filename = f"{user}_{str(datetime.datetime.now())}.py"
    b = st.button('Save Code')
    if b:
        count = 0
        while True:
            resp, error = run_functions_static(code)
            if not error:
                st.image(resp._repr_png_())
                write_or_append_to_file_in_dir(filename, code['func'], 'outputs')
                break
            else:
                messages_list.append({"role": "user", "content": f"I got the error:\n {str(error)}"})
                res = get_completion(messages=messages_list)
                code = json.loads(res)
                count += 1

            if count >= 5 and error is not None:
                raise Exception("Error in generating code")
                break




if prompt is not None:
    code_val, messages = show()
    render_code(code_val, messages)