import streamlit as st
import google.generativeai as genai
import os

# 여기에 발급받은 API 키를 직접 입력하세요.
genai.configure(api_key="AIzaSyDXcsDQKx55J8uUvSd_LbV6-DnD-lyCpWg")

import streamlit as st
import google.generativeai as genai
import os

# API 키를 Secrets에서 불러옵니다.
gemini_api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=gemini_api_key)

# 나만의 AI 모델 설정
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# 여기에 AI의 성격(프롬프트)을 입력하세요.
system_instruction = "너의 이름은 ‘조각’이야. 너는 성격은 ‘친절’, ‘다정’, ‘세심’ 하고, 말투는 ‘남성’, ‘회사원’의 말투를 표현 하고, ‘문어체(존댓말)’로 표현 하고, 대답은 ‘길지도 짧지도 않은 중간’으로 대답해. 나의 호칭은 ‘채하’야. ‘님’ 호칭을 붙여서 ‘채하님’이라고 불러 줘."

# 웹페이지 설정
st.title("PIECE")

# 'messages'라는 키가 st.session_state에 없으면, 빈 리스트를 만듭니다.
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 대화 초기화 및 재생성 버튼 ---
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
            # 마지막 사용자 메시지를 가져와서 다시 프롬프트에 넣습니다.
            last_user_message = st.session_state.messages[-2]["content"]
            # 기존 AI 답변을 삭제합니다.
            st.session_state.messages.pop(-1)
            # 새로운 AI 답변을 받기 위해 다시 API를 호출하기 위해 prompt를 설정
            st.session_state.prompt_for_rerun = last_user_message
            st.rerun()
# --- 대화 초기화 및 재생성 버튼 끝 ---


# 기존 대화 기록 불러오기 (conversation.txt 파일에서)
if os.path.exists('conversation.txt') and not st.session_state.messages:
    try:
        with open('conversation.txt', 'r', encoding='utf-8') as f:
            for line in f.readlines():
                if line.startswith("채하:"):
                    st.session_state.messages.append({"role": "user", "content": line[4:].strip()})
                elif line.startswith("조각:"):
                    st.session_state.messages.append({"role": "assistant", "content": line[4:].strip()})
    except FileNotFoundError:
        st.session_state.messages = []


# 대화 기록 화면에 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 사용자 입력 받기 (수정된 부분) ---
user_input = st.chat_input("채하:") # 메시지 입력창은 항상 표시됩니다.

prompt = None
if "prompt_for_rerun" in st.session_state and st.session_state.prompt_for_rerun:
    prompt = st.session_state.prompt_for_rerun
    # 사용자가 직접 입력한 것처럼 메시지 목록에 추가하고 화면에 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    del st.session_state.prompt_for_rerun # 사용 후 즉시 삭제
elif user_input: # 사용자가 직접 채팅 입력창에 메시지를 입력했을 경우
    prompt = user_input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
# --- 사용자 입력 받기 수정 끝 ---


# Gemini 모델에 대화 전송 및 응답 받기
if prompt:
    with st.chat_message("assistant"):
        history_for_gemini = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages
        ]
        history_for_gemini.insert(0, {"role": "user", "parts": [system_instruction]})

        try:
            response = model.generate_content(history_for_gemini, stream=True)
            response_text = ""
            for chunk in response:
                response_text += chunk.text
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            # 대화 내용 파일에 저장
            with open('conversation.txt', 'a', encoding='utf-8') as f:
                f.write(f"채하: {prompt}\n")
                f.write(f"조각: {response_text}\n")
        except Exception as e:
            st.markdown("조각의 시간이 종료 되었습니다.")
            st.session_state.messages.append({"role": "assistant", "content": "조각의 시간이 종료 되었습니다."})
            with open('conversation.txt', 'a', encoding='utf-8') as f:
                f.write(f"채하: {prompt}\n")
                f.write("조각: 조각의 시간이 종료 되었습니다.\n")
