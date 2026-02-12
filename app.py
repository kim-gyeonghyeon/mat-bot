import streamlit as st
import os
import google.generativeai as genai

# --- [설정] ---
GOOGLE_API_KEY = "AIzaSyA8AeFMqW3vsuFahBwDgntk5ERwz0xwoo8"
genai.configure(api_key=GOOGLE_API_KEY)
DATA_FILE = "rules.txt"
# --------------

st.set_page_config(page_title="사내규정 챗봇", page_icon="🤖")
st.title("📂 엠에이티플러스 사내규정 챗봇")

def get_rules():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

rules_text = get_rules()

# 모델 연결 함수: 404 에러를 잡기 위해 여러 이름을 시도합니다.
def load_model():
    model_names = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'models/gemini-1.5-flash',
        'gemini-pro'
    ]
    for name in model_names:
        try:
            m = genai.GenerativeModel(name)
            # 실제로 작동하는지 테스트 호출
            m.generate_content("test")
            return m
        except:
            continue
    return None

if rules_text:
    if "chat_model" not in st.session_state:
        st.session_state.chat_model = load_model()

    if st.session_state.chat_model:
        st.success("✅ 규정 확인 완료! 질문을 입력하세요.")
    else:
        st.error("❌ 현재 구글 AI 모델에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("규정에 대해 물어보세요"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        if st.session_state.chat_model:
            with st.chat_message("assistant"):
                with st.spinner("답변 생성 중..."):
                    prompt = f"다음 규정을 바탕으로 답하세요:\n{rules_text}\n\n질문: {user_input}"
                    try:
                        response = st.session_state.chat_model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"답변 생성 실패: {e}")
        else:
            st.error("모델이 연결되지 않았습니다.")
else:
    st.error(f"'{DATA_FILE}' 파일을 찾을 수 없습니다.")

