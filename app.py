import streamlit as st
import os
import google.generativeai as genai

# --- [설정] ---
# 이미 깃허브에 올리신 API 키를 그대로 사용합니다.
GOOGLE_API_KEY = "AIzaSyCdyr7CbuHNIff8PWYWRNwcw4hSVf6FWok"
genai.configure(api_key=GOOGLE_API_KEY)
DATA_FILE = "rules.txt"
# --------------

st.set_page_config(page_title="사내규정 챗봇", page_icon="🤖")
st.title("📂 엠에이티플러스 사내규정 챗봇")

def get_rules():
    # 현재 실행 파일 위치를 기준으로 rules.txt를 찾습니다.
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), DATA_FILE)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

rules_text = get_rules()

if rules_text:
    # [핵심 수정] 404 에러 방지를 위한 3단계 모델 연결 로직
    if "model" not in st.session_state:
        try:
            # 1순위: 가장 권장되는 최신 이름
            st.session_state.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            # 테스트 호출 (실제 모델이 있는지 확인)
            st.session_state.model.generate_content("hi") 
        except:
            try:
                # 2순위: 대체 이름
                st.session_state.model = genai.GenerativeModel('gemini-1.5-flash')
                st.session_state.model.generate_content("hi")
            except:
                # 3순위: 가장 안정적인 기본 모델
                st.session_state.model = genai.GenerativeModel('gemini-pro')

    st.success("✅ 규정 확인 완료! 질문을 입력하세요.")

    # 대화 기록 관리
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
                prompt = f"다음 규정 내용을 바탕으로 답해줘:\n\n{rules_text}\n\n질문: {user_input}"
                try:
                    response = st.session_state.model.generate_content(prompt)
                    ans = response.text
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                except Exception as e:
                    st.error(f"죄송합니다. 답변을 생성할 수 없습니다. (에러: {e})")
else:
    st.error(f"'{DATA_FILE}' 파일을 찾을 수 없습니다.")
    st.info(f"현재 위치: {os.path.dirname(os.path.abspath(__file__))}\n이 폴더에 rules.txt 파일이 있어야 합니다.")
