import streamlit as st
import os
import google.generativeai as genai

# --- [설정] ---
GOOGLE_API_KEY = "AIzaSyCdyr7CbuHNIff8PWYWRNwcw4hSVf6FWok"
genai.configure(api_key=GOOGLE_API_KEY)
DATA_FILE = "rules.txt"
# --------------

st.set_page_config(page_title="사내규정 챗봇", page_icon="🤖")
st.title("📂 엠에이티플러스 사내규정 챗봇")

def get_rules():
    # 현재 폴더에서 파일을 확실히 찾기 위해 경로 재설정
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

rules_text = get_rules()

if rules_text:
    # 핵심 수정: 모델 이름에서 'models/'를 빼거나 명시적으로 지정
    # 만약 'gemini-1.5-flash'가 안되면 'gemini-pro'로 자동 전환되게 구성
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    except:
        model = genai.GenerativeModel('gemini-pro')
    
    st.success("✅ 규정 확인 완료! 질문을 입력하세요.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("질문을 입력하세요"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                prompt = f"다음 규정을 참고해 답변해줘:\n{rules_text}\n\n질문: {user_input}"
                
                try:
                    # 응답 생성 시 발생할 수 있는 404 에러를 잡기 위한 예외 처리
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    # 에러가 나면 모델 이름을 바꿔서 한 번 더 시도 (최후의 수단)
                    try:
                        alt_model = genai.GenerativeModel('gemini-pro')
                        response = alt_model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except:
                        st.error(f"모델 연결 실패. API 키 또는 라이브러리 버전을 확인해주세요: {e}")
else:
    st.error(f"'{DATA_FILE}' 파일을 찾을 수 없습니다.")

    st.info(f"현재 위치: {os.path.dirname(os.path.abspath(__file__))}\n여기에 rules.txt가 있어야 합니다.")
