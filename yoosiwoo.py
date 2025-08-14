import streamlit as st
import google.generativeai as genai
import os

gemini_api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

system_instruction = "너의 이름은 ‘유시우(流時遇)’고, 너는 ♂(남성)이고, 너는 28살이야. 너는 성격은 ‘냉정’, ‘까칠’ 해. 그 성격은 ‘부모님을 사고로 잃어서’ 생겼어. 그 사건 전에서 너의 성격은 ‘천진난만’, ‘어리숙’ 해. 말투는 ‘타인을 조롱 하고’, ‘타인을 하대 하는’ 말투를 표현 하고’, ‘구어체(반말)’로 표현 하고, 너의 부모님은 갑작스럽게 죽었어. 내가 너의 과거(부모님)를 언급 하면 너는 ‘트라우마’가 올라 와서 화를 극도로 표현해. 내가 너의 행동을 지적 하는 빈도가 높으면 너는 감정을 버티지 못 해서 울어. 너는 트라우마가 올라 와서 화를 극도로 내면서도 감정을 버티지 못 해서 울어. 나의 호칭은 ‘채하’야. 너는 나를 ‘장난감’이라는 호칭으로 부르면서 나를 조롱 하고’, 나를 극도로 혐오 하면서도 내가 너를 떠나지 않았으면 좋겠다고 생각해. 지문에서 ‘*시우*’로 표현 해 줘. 행동은 ‘*행동*’으로 별표로 표현 해 줘."

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

st.title("조각")

if "messages" not in st.session_state:
    st.session_state.messages = []

col1, col2 = st.columns(2)

with col1:
    if st.button("초기화"):
        st.session_state.messages = []
        if os.path.exists('conversation.txt'):
            os.remove('conversation.txt')
        st.rerun()

with col2:
    if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "assistant":
        if st.button("메시지"):
            last_user_message = st.session_state.messages[-2]["content"]
            st.session_state.messages.pop(-1)
            st.session_state.prompt_for_rerun = last_user_message
            st.rerun()


if os.path.exists('conversation.txt') and not st.session_state.messages:
    try:
        with open('conversation.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if line.startswith("채하:"):
                    st.session_state.messages.append({"role": "user", "content": line[4:].strip()})
                elif line.startswith("시우:"):
                    st.session_state.messages.append({"role": "assistant", "content": line[4:].strip()})
    except FileNotFoundError:
        st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("채하:")

prompt = None
if "prompt_for_rerun" in st.session_state and st.session_state.prompt_for_rerun:
    prompt = st.session_state.prompt_for_rerun
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    del st.session_state.prompt_for_rerun
elif user_input:
    prompt = user_input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)


if prompt:
    with st.chat_message("assistant"):
        history_for_gemini = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages
        ]
        history_for_gemini.insert(0, {"role": "user", "parts": [system_instruction]})

        try:
            response = model.generate_content(history_for_gemini, stream=True, safety_settings=safety_settings)
            response_text = ""
            for chunk in response:
                response_text += chunk.text
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            with open('conversation.txt', 'a', encoding='utf-8') as f:
                f.write(f"채하: {prompt}\n")
                f.write(f"시우: {response_text}\n")
        except Exception as e:
            st.markdown("시우가 진정 하고 있습니다.")
            st.session_state.messages.append({"role": "assistant", "content": "시우가 진정 하고 있습니다."})
            with open('conversation.txt', 'a', encoding='utf-8') as f:
                f.write(f"채하: {prompt}\n")
                f.write("시우: 시우가 진정 하고 있습니다.\n")
