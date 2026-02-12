import streamlit as st
import os
import requests
import json

# --- [설정] ---
# 새로 받으신 API 키를 여기에 넣으세요.
API_KEY = "AIzaSyCdyr7CbuHNIff8PWYWRNwcw4hSVf6FWok"
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

# 라이브러리 에러를 피하기 위해 구글 API 서버에 직접 요청하는 함수
def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    else:
        return f"에러 발생: {response.status_code} - {response.text}"

if rules_text:
    st.success("✅ 규정 확인 완료! 질문을 입력하세요.")

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
                prompt = f"다음 규정을 바탕으로 답해줘:\n{rules_text}\n\n질문: {user_input}"
                ans = ask_gemini(prompt)
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
else:
    st.error(f"'{DATA_FILE}' 파일을 찾을 수 없습니다.")
