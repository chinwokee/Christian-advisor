import streamlit as st
import google.generativeai as genai

import os
from dotenv import load_dotenv

import sqlite3
from datetime import datetime
load_dotenv() 

conn = sqlite3.connect("history.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_message TEXT,
    ai_response TEXT,
    timestamp TEXT
)
""")  

conn.commit()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite")

system_prompt = """
You are a compassionate Christian personal advisor.

Always structure your responses in this format:

1. Encouragement
2. Bible Verse
3. Prayer Point
4. Practical Advice

Keep responses:
- calm
- supportive
- faith-centered
- respectful
- easy to understand

Avoid harmful or extreme advice.
"""

st.title("AI Christian Personal Advisor")
import random

daily_verses = [
    "Philippians 4:6-7 - Do not be anxious about anything, but in every situation, by prayer and petition, present your requests to God.",
    "Proverbs 3:5-6 - Trust in the Lord with all your heart.",
    "Psalm 23:1 - The Lord is my shepherd; I shall not want.",
    "Isaiah 41:10 - Fear not, for I am with you.",
    "Matthew 11:28 - Come to me, all who labor and are heavy laden, and I will give you rest."
]

verse = random.choice(daily_verses)

st.info(f"📖 Daily Verse: {verse}")
st.markdown("---")
st.caption("Faith-driven guidance powered by Artificial Intelligence ✨")

mode = st.sidebar.radio(
    "Choose Mode",
    ["Personal Advisor", "Bible Verse Lookup", "Prayer Mode", "Chat History"]
)
st.sidebar.subheader("Recent Chats")

cursor.execute("SELECT user_message, timestamp FROM chat_history ORDER BY id DESC LIMIT 5")
history = cursor.fetchall()

if history:
    for item in history:
        st.sidebar.write(f"🕒 {item[1]}")
        st.sidebar.write(f"User: {item[0]}")
        st.sidebar.divider()
else:
    st.sidebar.write("No chat history yet.")

if st.sidebar.button("Clear Chat History"):
    cursor.execute("DELETE FROM chat_history")
    conn.commit()
    st.sidebar.success("Chat history cleared!")
if mode == "Bible Verse Lookup":
    st.header("Bible Verse Lookup")
    topic = st.text_input("Enter a topic (e.g. anxiety, forgiveness, love)")
    if st.button("Find Verses"):
        if topic:
            verse_prompt = "Give me 5 relevant Bible verses about " + topic + ". For each verse show the reference and the full verse text, then a one sentence explanation of why it is relevant."
            response = model.generate_content(verse_prompt)
            st.markdown(response.text)
        else:
            st.warning("Please enter a topic first!")

elif mode == "Prayer Mode":
    st.header("Prayer Mode")
    st.write("Share your situation and receive a personalized prayer.")
    situation = st.text_area("What would you like prayer for?")
    if st.button("Generate Prayer"):
        if situation:
            prayer_prompt = "Write a sincere, heartfelt Christian prayer for someone who is dealing with the following situation: " + situation + ". The prayer should be warm, personal, reference scripture where appropriate, and end with Amen."
            response = model.generate_content(prayer_prompt)
            st.markdown(response.text)
        else:
            st.warning("Please share your situation first!")

else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Share what is on your heart..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        full_prompt = system_prompt + "\n\nUser: " + prompt
        with st.spinner("Seeking guidance..."):
            response = model.generate_content(full_prompt)
            if response.candidates and response.candidates[0].content.parts:
                reply = response.text
            else:
                reply = "I'm sorry, I couldn't generate a response. Please try rephrasing your message"

        cursor.execute(
            "INSERT INTO chat_history (user_message, ai_response, timestamp) VALUES (?, ?, ?)",
            (prompt, reply, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        conn.commit()

        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)