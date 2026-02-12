import streamlit as st
import os
import google.generativeai as genai

# --- [설정] ---
# 방금 새로 발급받으신 'mat-bot' 프로젝트의 키입니다.
GOOGLE_API_KEY = "AIzaSyAPs5m_OKSBtDa4rKDpXb5RGG94ZpYrT6A"
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

if rules_text:
    # 새 프로젝트 키는 gemini-1.5-flash 모델을 완벽하게 지원합니다.
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.success("✅ 규정집 로드 완료! 질문을 시작하세요.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("규정에 대해 물어보세요"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                prompt = f"다음 규정을 바탕으로 답변해줘:\n{rules_text}\n\n질문: {user_input}"
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"죄송합니다. 에러가 발생했습니다: {e}")
else:
    st.error(f"'{DATA_FILE}' 파일을 찾을 수 없습니다. GitHub 저장소를 확인해주세요.")
