import streamlit as st
from agent.react_agent import ReactAgent

st.title("智能客服")
st.divider()

if "message" not in st.session_state:
    st.session_state["message"]=[]


if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 在页面最下方提供用户输入栏
prompt = st.chat_input()

if prompt:
    # 在页面输出用户的提问
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages=[]

    with st.spinner("AI正在思考 ... "):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        def capture(generator, capture_list):
            for chunk in generator:
                capture_list.append(chunk)

                for char in chunk:
                    yield char

        res=st.chat_message("assistant").write_stream(res_stream)
        st.session_state["message"].append({"role": "assistant", "content": res})
        st.rerun()