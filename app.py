import streamlit as st
import feedparser
from datetime import datetime, timedelta
import edge_tts
import asyncio
import tempfile

st.set_page_config(layout="wide")
st.title("X 语音电台")

if "users" not in st.session_state:
    st.session_state.users = ["elonmusk", "sama"]

with st.sidebar:

    st.header("用户列表")

    new_user = st.text_input("添加用户（不用@）")

    if st.button("添加用户"):
        if new_user:
            st.session_state.users.append(new_user)

    for u in st.session_state.users:
        st.write(u)

    hours = st.number_input("最近多少小时", 1, 48, 6)

    voice = st.selectbox(
        "语音",
        [
            "en-US-JennyNeural",
            "zh-CN-XiaoxiaoNeural"
        ]
    )

async def make_audio(text, voice):
    tts = edge_tts.Communicate(text, voice=voice)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    await tts.save(tmp.name)

    return tmp.name

if st.button("开始朗读"):

    now = datetime.utcnow()
    cutoff = now - timedelta(hours=hours)

    posts = []

    for user in st.session_state.users:

        feed = feedparser.parse(
            f"https://nitter.net/{user}/rss"
        )

        for entry in feed.entries:

            published = datetime(*entry.published_parsed[:6])

            if published > cutoff:
                posts.append(
                    f"{user}: {entry.title}"
                )

    if posts:

        for p in posts:
            st.write(p)

        text = "。".join(posts[:20])

        audio = asyncio.run(
            make_audio(text[:1000], voice)
        )

        st.audio(audio)

    else:
        st.warning("没有新内容")