import streamlit as st
import os
import google.generativeai as genai

# --- [설정] ---
# 만약 에러가 계속된다면, 여기서 새로운 API 키를 발급받아 교체하세요.
GOOGLE_API_KEY = "AIzaSyCdyr7CbuHNIff8PWYWRNwcw4hSVf6FWok"
genai.configure(api_key=GOOGLE_API_KEY)
DATA_FILE = "rules.txt"
# --------------

st.set_page_config(page_title="사내규정 챗봇", page_icon="🤖")
st.title("📂 엠에이티플러스 사내규정 챗봇")

# 1. 파일 읽기 함수
def get_rules():
    # Streamlit Cloud 환경에서도 파일을 정확히 찾도록 경로를 설정합니다.
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

rules_text = get_rules()

# 2. 모델 설정 (가장 안정적인 gemini-pro 사용)
@st.cache_resource
def load_model():
try:
    # 가장 표준적이고 튼튼한 모델명입니다.
    model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
    # 연결 테스트
    model.generate_content("test")
except:
    try:
        # 두 번째 대안
        model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    except Exception as e:
        st.error(f"모델 연결에 실패했습니다. (상세에러: {e})")
        return None

if rules_text:
    model = load_model()
    
    if model:
        st.success("✅ 규정 확인 완료! 질문을 입력하세요.")
    
        # 대화 세션 초기화
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 기존 대화 표시
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 사용자 입력
        if user_input := st.chat_input("규정에 대해 물어보세요"):
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("답변 생성 중..."):
                    # 규정 전문을 컨텍스트로 직접 넣어 질문합니다.
                    prompt = f"다음 사내 규정을 바탕으로 질문에 답하세요:\n\n[규정 내용]\n{rules_text}\n\n질문: {user_input}"
                    try:
                        response = model.generate_content(prompt)
                        ans = response.text
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    except Exception as e:
                        st.error(f"AI 응답 에러: {e}")
                        st.info("API 키가 만료되었거나 모델 권한이 없을 수 있습니다. 새로운 키를 발급받아보세요.")
else:
    st.error(f"'{DATA_FILE}' 파일을 찾을 수 없습니다.")
    st.info("GitHub에 rules.txt 파일이 app.py와 같은 위치에 있는지 확인해주세요.")

