import streamlit as st
import os
import google.generativeai as genai

# --- [설정] ---
# 방금 새로 발급받으신 API 키를 여기에 정확히 입력하세요.
GOOGLE_API_KEY = "AIzaSyCdyr7CbuHNIff8PWYWRNwcw4hSVf6FWok"
genai.configure(api_key=GOOGLE_API_KEY)
DATA_FILE = "rules.txt"
# --------------

st.set_page_config(page_title="사내규정 챗봇", page_icon="🤖")
st.title("📂 엠에이티플러스 사내규정 챗봇")

# 파일 로드 함수 (Streamlit Cloud 경로 최적화)
def get_rules():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

rules_text = get_rules()

# 모델 로드 함수 (404 에러 방지용 3단계 로직)
@st.cache_resource
def load_validated_model():
    # 시도할 모델명 리스트 (구글 API가 인식하는 표준 명칭들)
    model_candidates = [
        'models/gemini-1.5-flash-latest', 
        'models/gemini-1.5-flash', 
        'models/gemini-pro'
    ]
    
    for name in model_candidates:
        try:
            model = genai.GenerativeModel(name)
            # 실제로 대답이 가능한지 테스트 (여기서 에러나면 다음 모델로)
            model.generate_content("ping") 
            return model
        except:
            continue
    return None

if rules_text:
    model = load_validated_model()
    
    if model:
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
                    prompt = f"다음 규정을 바탕으로 답변해:\n{rules_text}\n\n질문: {user_input}"
                    try:
                        response = model.generate_content(prompt)
                        st.markdown(response.text)
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                    except Exception as e:
                        st.error(f"AI 응답 에러: {e}")
    else:
        st.error("❌ 구글 AI 모델 연결에 모두 실패했습니다. API 키의 유효성을 확인해주세요.")
else:
    st.error(f"'{DATA_FILE}' 파일을 찾을 수 없습니다. GitHub에 파일이 있는지 확인해주세요.")
