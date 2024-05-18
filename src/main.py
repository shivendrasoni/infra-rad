import datetime

import streamlit as st


import json
from src.utils.openai_util import get_completion, SYSTEM_PROMPT, get_terraform_code
from dotenv import load_dotenv
load_dotenv()

st. set_page_config(layout="wide")

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
        print("Error in dynamic function invocation\n", error)
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

def show(prompt):


    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT })
    st.session_state.messages.append({"role": "user", "content": prompt})
    res = get_completion(messages=st.session_state.messages)
    res_json = json.loads(res)
    return res_json

@st.experimental_fragment
def show_terraform_code():
    b = st.button("Generate Terraform Code")
    if b:
        stream = get_terraform_code(st.session_state.image)
        stream_value =  st.write_stream(stream)
        # Close the stream
        stream.close()

        st.download_button('Download Terraform Code', stream_value, mime = 'text', file_name='terraform_plan.tf')

def render_code(code):
    user = 'user_1'
    #filename of format user_1_timestamp
    filename = f"{user}_{str(datetime.datetime.now())}.py"
    count = 0
    while True:
        resp, error = run_functions_static(code)
        if not error:
            st.session_state.image = resp._repr_png_()
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": code['func']})
            write_or_append_to_file_in_dir(filename, code['func'], 'outputs')
            break
        else:
            st.session_state.messages.append({"role": "user", "content": f"I got the error:\n {str(error)}"})
            res = get_completion(messages=st.session_state.messages)
            code = json.loads(res)
            count += 1

        if count >= 5 and error is not None:
            raise Exception("Error in generating code")
            break



st.title("Infra Bot")

def render_ui():
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "image" not in st.session_state:
        st.session_state.image = None
    chat, image = st.columns(2)

    with chat:
        prompt = st.chat_input("What do you want to build?")
        # Display chat messages from history on app rerun
        if len(st.session_state.messages)>1:
            for message in st.session_state.messages[1:]:
                with st.chat_message(message["role"]):
                    if message["role"] == "user":
                        st.markdown(message["content"])
                    else:
                        st.code(message["content"])

        # React to user input
        if prompt:
            # Display user message in chat message container
            st.chat_message("user").markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            code_val = show(prompt)
            render_code(code_val)

            response = code_val['func']
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.code(response)

    with image:
        if st.session_state.image is None:
            st.info("No image generated yet")
        else:
            st.image(st.session_state.image)
            show_terraform_code()

render_ui()