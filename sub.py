import streamlit as st
import openai
import datetime
import pandas as pd
import random
import json
from gtts import gTTS
import os
import time
from googletrans import Translator
from pydub import AudioSegment
from pydub.playback import play

# Set default language to Korean
st.set_page_config(page_title="일정 관리 앱", page_icon="🗓️", layout="centered")

# OpenAI Key input
openai.api_key = st.text_input('OpenAI API 키를 입력하세요', type='password')

# Function for multilingual support
def translate_text(text, target_language='ko'):
    translator = Translator()
    return translator.translate(text, dest=target_language).text

# Function to convert text to speech
def text_to_speech(text, lang='ko'):
    tts = gTTS(text=text, lang=lang)
    audio_file = f"audio_{random.randint(1, 10000)}.mp3"
    tts.save(audio_file)
    audio = AudioSegment.from_mp3(audio_file)
    play(audio)
    os.remove(audio_file)

# AI-based schedule analysis using OpenAI GPT-3.5-turbo
def ai_schedule_analysis(user_schedule):
    try:
        prompt = f"다음 일정을 분석하고 개선하거나 최적화할 방법을 제시하세요:\n{user_schedule}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        analysis = response['choices'][0]['message']['content'].strip()
        return analysis
    except Exception as e:
        st.error(f"OpenAI API 오류: {e}")
        return "AI 분석 실패."

# AI-based report generation using OpenAI GPT-3.5-turbo
def ai_generate_report(schedule):
    try:
        prompt = f"다음 일정을 기반으로 주간 또는 월간 보고서를 작성하세요:\n{schedule}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )
        report = response['choices'][0]['message']['content'].strip()
        return report
    except Exception as e:
        st.error(f"보고서 생성 중 오류 발생: {e}")
        return "보고서 생성 실패."

# Function to suggest rest times
def suggest_rest_time(schedule):
    busy_hours = sum([item['duration'] for item in schedule if item['type'] == 'work'])
    if busy_hours > 6:
        return "오늘은 바쁜 일정입니다! 1-2시간마다 짧은 휴식을 고려하세요."
    else:
        return "일정이 균형 잡혀 있습니다. 잘 하고 계십니다!"

# Schedule management
if 'schedule' not in st.session_state:
    st.session_state.schedule = []

# UI to add a task
with st.form("schedule_form"):
    task_name = st.text_input("작업 이름")
    task_type = st.selectbox("작업 유형", ["업무", "회의", "휴식", "기타"])
    task_duration = st.number_input("소요 시간 (분)", min_value=0, max_value=1440, value=60)
    task_date = st.date_input("작업 날짜", value=datetime.date.today())  # Date Picker
    task_time = st.time_input("작업 시간", value=datetime.time(9, 0))

    submitted = st.form_submit_button("작업 추가")
    if submitted:
        task = {
            "name": task_name,
            "type": task_type,
            "duration": task_duration,
            "date": task_date.strftime('%Y-%m-%d'),  # Store date as string
            "time": task_time.strftime('%H:%M')
        }
        st.session_state.schedule.append(task)
        st.success(f"{task_name}이(가) {task_date} {task_time}에 추가되었습니다.")

# Display schedule
st.subheader("당신의 일정")
schedule_df = pd.DataFrame(st.session_state.schedule)
st.table(schedule_df)

# Schedule analysis and optimization
if st.button("일정 분석 및 최적화"):
    user_schedule = "\n".join([f"{task['date']} {task['time']} - {task['name']} ({task['type']}, {task['duration']}분)" for task in st.session_state.schedule])
    analysis = ai_schedule_analysis(user_schedule)
    st.write(f"AI 분석: {analysis}")

# Fatigue analysis
if st.button("피로 분석"):
    rest_suggestions = suggest_rest_time(st.session_state.schedule)
    st.write(f"휴식 제안: {rest_suggestions}")

# Notifications system
notification_methods = ['소리', '진동', '푸시 알림']
notification_choice = st.selectbox("알림 방법 선택", notification_methods)

if notification_choice == "소리":
    if st.button("음성 알림 듣기"):
        text_to_speech("이것은 당신의 음성 알림입니다. 작업을 잊지 마세요!")
    else:
        st.write("음성 알림 버튼을 눌러주세요.")

# Weekly/Monthly Reports
report_choice = st.radio("보고서 생성", ['주간 보고서', '월간 보고서'])
if st.button("보고서 생성"):
    # Generate AI-based report based on the schedule
    schedule_text = "\n".join([f"{task['date']} {task['time']} - {task['name']} ({task['type']}, {task['duration']}분)" for task in st.session_state.schedule])
    report = ai_generate_report(schedule_text)
    st.write(f"AI 보고서: {report}")

# Time Management Challenge Feature
challenge_goal = st.text_input("시간 관리 도전 설정", "이번 주 회의 3개 완료하기")
if st.button("도전 시작"):
    st.session_state.challenge_goal = challenge_goal
    st.success(f"도전 시작: {challenge_goal}")

# Rest Management Feature
rest_choice = st.radio("휴식 관리", ['휴식 제안 받기', '휴식 알림 설정'])
if rest_choice == '휴식 제안 받기':
    st.write(suggest_rest_time(st.session_state.schedule))
else:
    rest_time = st.time_input("휴식 시간 설정", value=datetime.time(15, 0))
    st.session_state.schedule.append({
        "name": "휴식",
        "type": "rest",
        "duration": 15,
        "date": datetime.date.today().strftime('%Y-%m-%d'),  # Default to today's date for rest
        "time": rest_time.strftime('%H:%M')
    })
    st.success(f"{rest_time}에 휴식 시간이 추가되었습니다.")

# Customizable Themes (Simple example with color)
theme_color = st.selectbox("테마 색상 선택", ["라이트", "다크"])
if theme_color == "다크":
    st.markdown("""
        <style>
            body {
                background-color: #333;
                color: white;
            }
        </style>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body {
                background-color: white;
                color: black;
            }
        </style>
        """, unsafe_allow_html=True)

# Show the current schedule
st.subheader("현재 일정:")
st.write(st.session_state.schedule)
