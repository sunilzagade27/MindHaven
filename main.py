import time
import streamlit as st
import json
import os
import datetime
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
import openai
from openai import OpenAI


st.set_page_config(page_title="Aimood Chatbot", page_icon="🧠")

# File paths
MOOD_FILE = "mood_log.json"
COMMUNITY_FILE = "community_posts.json"

# Load or initialize mood log
if os.path.exists(MOOD_FILE):
    with open(MOOD_FILE, "r") as f:
        mood_log = json.load(f)
else:
    mood_log = {}

# Load or initialize community posts
if os.path.exists(COMMUNITY_FILE):
    with open(COMMUNITY_FILE, "r") as f:
        community_posts = json.load(f)
else:
    community_posts = []

st.set_page_config(page_title="MindHeaven", page_icon="🧠")
st.title("🧠 MindHaven – Daily Mental Health Check-In")

st.write("How are you feeling today? Choose the emoji that best represents your mood:")


moods = {
    "😊 Happy": """
        You're in a good place today — enjoy it. Hold onto what made you smile, even the little stuff.
        Maybe take a walk or call someone just to share the vibe.

        🎵 Song: "Walking on Sunshine" – Katrina and the Waves

        Move:
        - Stretch up tall.
        - Sway side to side or do a little dance.
        - Let yourself feel light, even if just for a minute.
    """,

    "😐 Okay": """
        It’s one of those “fine” days — not bad, not great. That’s okay.
        Let it be simple. Maybe take 5 minutes just to be still and notice your surroundings.

        🎵 Song: "Weightless" – Marconi Union

        Reset:
        - Roll your shoulders.
        - Breathe in slowly, then out.
        - Just sit. Nothing to fix. Let it be.
    """,

    "😢 Sad": """
        Some days just feel heavy. You don’t need to push it away.
        Maybe write down what’s weighing on you or just rest quietly.

        🎵 Song: "Fix You" – Coldplay

        Rest:
        - Lie on your back.
        - Open your chest and breathe.
        - Stay as long as you want.
    """,

    "😠 Angry": """
        You’re fired up — something clearly hit a nerve. That’s real.
        Better to move that energy than keep it bottled.

        🎵 Song: "Stronger" – Kanye West

        Move it out:
        - 20 jumping jacks.
        - Punch the air. Hard.
        - Then sit. Breathe it out.
    """,

    "😰 Anxious": """
        Everything might feel too loud or too fast right now.
        Try grounding yourself in your breath and surroundings.

        🎵 Song: "Sunrise" – Norah Jones

        Slow down:
        - Inhale for 4 seconds
        - Hold 4
        - Exhale 4
        - Hold 4
        - Repeat.
        - Look around. Name 3 things you see.
    """,

    "😴 Tired": """
        You’re worn out, and that’s okay. Maybe don’t ask more of yourself than necessary today.
        Close your eyes for a bit if you can.

        🎵 Song: "Night Owl" – Galimatias

        Rest:
        - Lie down.
        - Hug your knees to your chest.
        - Rock side to side.
        - Let your jaw unclench. Let go a little.
    """
}



selected_mood = st.radio("", list(moods.keys()))

if st.button("✔️ Log Mood"):
    today = str(datetime.date.today())
    mood_log[today] = selected_mood
    with open(MOOD_FILE, "w") as f:
        json.dump(mood_log, f)
    st.success("Mood logged for today ✅")

st.subheader("💬 Suggestion:")
st.info(moods[selected_mood])

# --- Community Mood Wall Section ---
st.markdown("---")
st.subheader("🌍 Community Mood Wall")

with st.form("community_post_form"):
    community_mood = st.selectbox("Share your mood anonymously:", list(moods.keys()))
    message = st.text_area("Say something supportive or share how you're feeling (optional)", max_chars=200)
    submitted = st.form_submit_button("Post to Community")

if submitted:
    post = {
        "id": random.randint(100000, 999999),
        "timestamp": datetime.datetime.now().isoformat(),
        "mood": community_mood,
        "message": message.strip(),
        "support_count": 0
    }
    community_posts.append(post)
    with open(COMMUNITY_FILE, "w") as f:
        json.dump(community_posts, f)
    st.success("Thank you for sharing! Your post has been added.")


if community_posts:
    st.write(f"### Recent Posts ({len(community_posts)})")
    for post in sorted(community_posts, key=lambda x: x["timestamp"], reverse=True):
        ts = datetime.datetime.fromisoformat(post["timestamp"]).strftime("%Y-%m-%d %H:%M")
        st.markdown(f"**{ts}** — {post['mood']}")
        if post["message"]:
            st.write(post["message"])
        support_key = f"support_{post['id']}"
        if st.button(f"❤️ Support ({post['support_count']})", key=support_key):
            post["support_count"] += 1
            with open(COMMUNITY_FILE, "w") as f:
                json.dump(community_posts, f)
            st.experimental_rerun()
else:
    st.info("No community posts yet. Be the first to share your mood!")

# --- Mood History and Chart Section ---
st.markdown("---")
st.subheader("📈 Mood History")

if mood_log:
    for date, mood in sorted(mood_log.items(), reverse=True):
        st.write(f"**{date}** — {mood}")

    dates = sorted(mood_log.keys())
    mood_names = list(moods.keys())
    mood_to_num = {mood: i for i, mood in enumerate(mood_names)}
    y_values = [mood_to_num[mood_log[date]] for date in dates]

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(dates, y_values, marker='o', linestyle='-')
    ax.set_yticks(range(len(mood_names)))
    ax.set_yticklabels(mood_names)
    ax.set_xlabel("Date")
    ax.set_title("Mood Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No mood data yet. Check in above!")



# --- Support Resources ---
st.markdown("---")
st.subheader("🆘 Support Resources")
st.write("""
- [Mental Health America](https://mhanational.org/) – Education and support  
- [Crisis Text Line](https://www.crisistextline.org/) – Text HOME to 741741  
- [National Suicide Prevention Lifeline](https://988lifeline.org/) – Call or text 988  
- [Therapy Matcher](https://www.psychologytoday.com/) – Find a therapist near you  
""")


st.title("MindHaven ChatBot🧠💡")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})