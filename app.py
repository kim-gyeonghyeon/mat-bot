import streamlit as st
import os
import requests
import json

# --- [설정] ---
# 경현님의 mat-bot 프로젝트에서 만든 새 키입니다.
API_KEY = "AIzaSyAPs5m_OKSBtDa4rKDpXb5RGG94ZpYrT6A"
DATA_FILE = "rules.txt"
# --------------

st.set_page_config(page_title="사내규정 챗봇", page_icon="🤖")
st.title("🖥️ 엠에이티플러스 CHAT-BOT")

def get_rules():
    # rules.txt 파일을 읽어오는 함수입니다.
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

rules_text = get_rules()

def ask_gemini(prompt):
    # [무적 설정] 경현님의 특별한 'Gemini 3 Pro' 모델 전용 주소입니다.
    url = url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            # 혹시 Pro 모델이 안될 경우를 대비한 2차 시도 (Flash 모델)
            alt_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={API_KEY}"
            alt_res = requests.post(alt_url, headers=headers, data=json.dumps(data))
            if alt_res.status_code == 200:
                return alt_res.json()['candidates'][0]['content']['parts'][0]['text']
            return f"에러 발생: {response.status_code}\n모델이 아직 활성화 중일 수 있습니다. 1분 뒤에 새로고침 해주세요."
    except Exception as e:
        return f"연결 에러: {e}"

if rules_text:
    st.success("(●'◡'●) 사내규정에 대해 궁금한 점을 문의해주세요")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 대화 내용 표시
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 질문 입력
    if user_input := st.chat_input("규정에 대해 물어보세요"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("응답을 만드는 중입니다. 잠시만 기다려주세요🖐️"):
                full_prompt = f"다음 사내 규정을 바탕으로 성실하게 답변해줘:\n\n{rules_text}\n\n질문: {user_input}"
                ans = ask_gemini(full_prompt)
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
else:
    st.error("rules.txt 파일을 찾을 수 없습니다. GitHub 저장소에 파일이 있는지 확인해주세요.")


