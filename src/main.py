import datetime
import streamlit as st
import json
from utils.openai_util import get_completion, SYSTEM_PROMPT, get_terraform_code, GEN_TF_CODE_SYSTEM_PROMPT
from dotenv import load_dotenv
from code_editor import code_editor

load_dotenv()
st.set_page_config(layout="wide")


def invoke_dynamic_function_from_string(func_str, func_name, *args, **kwargs):
    try:
        global_vars = {}
        local_vars = {}
        exec(func_str, global_vars, local_vars)
        func = local_vars.get(func_name)
        if not func:
            raise ValueError(f"Function {func_name} not found in the provided code.")
        return func(*args, **kwargs), None
    except Exception as error:
        print("Error in dynamic function invocation\n", error)
        return None, error


def run_functions_static(function_descriptor):
    function_string = function_descriptor['func']
    function_name = function_descriptor['fname']
    result, error = invoke_dynamic_function_from_string(function_string, function_name)
    return result, error


def write_or_append_to_file_in_dir(file_name, content, dir_path):
    with open(f"{dir_path}/{file_name}", "a") as f:
        f.write(content)


def show():
    res = get_completion(messages=st.session_state.messages)
    res_json = json.loads(res.choices[0].message.content)
    return res_json


@st.experimental_fragment
def show_terraform_code():
    b = st.button("Generate Terraform Code")
    if b:
        gen_tf_code_messages = [
            {"role": "system", "content": GEN_TF_CODE_SYSTEM_PROMPT},
            {"role": "user", "content": st.session_state.code['func']}
        ]
        response_format = {"type": "text"}
        stream = get_completion(messages=gen_tf_code_messages, response_format=response_format, stream=True)

        stream_value = st.write_stream(stream)
        stream.close()
        st.download_button('Download Terraform Code', stream_value, mime='text', file_name='terraform_plan.tf')


def render_code(code):
    user = 'user_1'
    filename = f"{user}_{str(datetime.datetime.now())}.py"
    count = 0
    while True:
        resp, error = run_functions_static(code)
        if not error:
            st.session_state.image = resp._repr_png_()
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


st.title("InfraRad")
st.markdown("Build your infrastructure with a single click!")
st.divider()


def render_diagram_button(response_dict):
    bx = st.button("Update Diagram", key='generate_diagram')
    if bx:
        res, error = run_functions_static(response_dict)
        st.session_state.image = res._repr_png_()


def render_ui():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if "image" not in st.session_state:
        st.session_state.image = None
    if "code" not in st.session_state:
        st.session_state.code = None

    chat, image = st.columns(2)

    with chat:
        prompt = st.chat_input("What do you want to build?")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            code_val = show()
            st.session_state.code = code_val
            render_code(code_val)

        if st.session_state.code:
            editor_btns = [{
                "name": "Run",
                "feather": "Play",
                "primary": True,
                "hasText": True,
                "showWithIcon": True,
                "commands": ["submit"],
                "style": {"bottom": "0.44rem", "right": "0.4rem"}
            }]
            response_dict = code_editor(st.session_state.code['func'], lang="python", buttons=editor_btns,
                                        options={'showLineNumbers': True})
            if len(response_dict['id']) != 0 and (
                    response_dict['type'] == "selection" or response_dict['type'] == "submit"):
                render_diagram_button({
                    "func": response_dict['text'],
                    "fname": st.session_state.code['fname']
                })

        st.subheader("Chat History")
        for message in st.session_state.messages[1:]:
            if message["role"] == "user":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    with image:
        if st.session_state.image is None:
            st.info("No image generated yet")
        else:
            st.image(st.session_state.image)
            show_terraform_code()


render_ui()
