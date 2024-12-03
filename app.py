import streamlit as st
import pandas as pd
import openai
import os
from datetime import datetime
import speech_recognition as sr
import pyttsx3

# OpenAI API 키 입력받기
openai_api_key = st.text_input("OpenAI API 키를 입력하세요:", type="password")

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    st.success("API 키가 성공적으로 설정되었습니다.")
else:
    st.warning("API 키를 입력해주세요.")

# 기본 일정 데이터프레임
if "events" not in st.session_state:
    st.session_state["events"] = pd.DataFrame(columns=["Date", "Time", "Event", "Priority"])

# 일정 추가 기능
def add_event(date, time, event, priority):
    new_event = {
        "Date": date,
        "Time": time,
        "Event": event,
        "Priority": priority
    }
    st.session_state["events"] = st.session_state["events"].append(new_event, ignore_index=True)

# 우선순위 기준으로 자동 정렬
def prioritize_schedule():
    return st.session_state["events"].sort_values(by=["Priority"], ascending=[False])

# 일정 추가 UI
st.title('일정 관리 앱')

# 날짜, 시간, 일정 제목, 우선순위 입력
selected_date = st.date_input("일정을 추가할 날짜를 선택하세요", datetime.today())
event_title = st.text_input("일정 제목을 입력하세요")
event_time = st.time_input("일정을 시작할 시간을 선택하세요", datetime.now().time())
priority = st.slider("우선순위 (1이 가장 높음)", 1, 5)

# 일정 추가 버튼
if st.button("일정 추가"):
    if event_title:
        add_event(selected_date, event_time, event_title, priority)
        st.success(f"{event_title} 일정이 추가되었습니다!")
    else:
        st.warning("일정 제목을 입력해주세요.")

# 일정 우선순위 정렬
sorted_events = prioritize_schedule()
st.write("### 일정 목록 (우선순위 순)")
st.dataframe(sorted_events)

# 음성 인식 및 알림 기능
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# 음성으로 일정 추가
def listen_for_event():
    with sr.Microphone() as source:
        print("음성으로 일정을 입력하세요...")
        audio = recognizer.listen(source)

    try:
        event = recognizer.recognize_google(audio, language="ko-KR")
        print(f"인식된 음성: {event}")
        return event
    except sr.UnknownValueError:
        print("음성을 인식할 수 없습니다.")
        return None

# 음성 알림
def voice_reminder(message):
    engine.say(message)
    engine.runAndWait()

# 음성 명령을 통한 일정 추가
if st.button("음성으로 일정 추가"):
    event = listen_for_event()
    if event:
        st.write(f"음성으로 추가된 일정: {event}")
        voice_reminder(f"{event} 일정이 추가되었습니다.")
        add_event(selected_date, event_time, event, priority)

# AI 일정 분석 (OpenAI)
def analyze_schedule(schedule_text):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="gpt-3.5-turbo",
        prompt=f"다음 일정을 분석하여 비효율적인 부분과 개선 방법을 제시하세요: {schedule_text}",
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# 일정 분석 버튼
if st.button("일정 분석하기"):
    schedule_text = " ".join(st.session_state["events"]["Event"].values)
    analysis_result = analyze_schedule(schedule_text)
    st.write(f"AI 분석 결과: {analysis_result}")

# 주간/월간 시간 추적 보고서
def generate_report(df, period='weekly'):
    if period == 'weekly':
        df['Week'] = pd.to_datetime(df['Date']).dt.isocalendar().week
        report = df.groupby('Week').size()
    elif period == 'monthly':
        df['Month'] = pd.to_datetime(df['Date']).dt.month
        report = df.groupby('Month').size()
    return report

# 보고서 출력 (주간)
weekly_report = generate_report(st.session_state["events"], 'weekly')
st.write("### 주간 보고서")
st.write(weekly_report)

# 사용자 맞춤형 테마 설정
theme_color = st.selectbox("앱 테마 색상을 선택하세요", ["기본", "어두운 모드", "밝은 모드"])

if theme_color == "어두운 모드":
    st.markdown("""
    <style>
    body {
        background-color: #2e2e2e;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
elif theme_color == "밝은 모드":
    st.markdown("""
    <style>
    body {
        background-color: #f0f0f0;
        color: black;
    }
    </style>
    """, unsafe_allow_html=True)
