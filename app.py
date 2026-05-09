import streamlit as st
from playwright.sync_api import sync_playwright
import edge_tts
import asyncio
import tempfile

st.set_page_config(layout="wide")

st.title("X 语音电台（Playwright版）")

if "users" not in st.session_state:
    st.session_state.users = ["elonmusk"]

with st.sidebar:

    st.header("用户")

    new_user = st.text_input("添加用户")

    if st.button("添加") and new_user:
        st.session_state.users.append(new_user)

    st.write(st.session_state.users)

    voice = st.selectbox(
        "语音",
        [
            "en-US-JennyNeural",
            "zh-CN-XiaoxiaoNeural"
        ]
    )

# ===== Playwright 抓取 =====
def get_posts(users):

    posts = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        for user in users:

            url = f"https://x.com/{user}"

            try:
                page.goto(url, timeout=60000)

                page.wait_for_timeout(5000)

                articles = page.locator("article").all()

                for a in articles[:5]:

                    text = a.inner_text()

                    if len(text) > 20:
                        posts.append(
                            f"{user}: {text}"
                        )

            except Exception as e:
                posts.append(
                    f"{user}: 获取失败"
                )

        browser.close()

    return posts

# ===== TTS =====
async def make_audio(text, voice):

    tts = edge_tts.Communicate(
        text,
        voice=voice
    )

    tmp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    await tts.save(tmp.name)

    return tmp.name

# ===== 主逻辑 =====
if st.button("开始朗读"):

    with st.spinner("正在抓取 X 内容..."):

        posts = get_posts(
            st.session_state.users
        )

    if posts:

        st.subheader("内容")

        for p in posts:
            st.write(p)

        text = "。".join(posts[:10])

        audio = asyncio.run(
            make_audio(text[:1500], voice)
        )

        st.audio(audio)

    else:
        st.warning("没有抓到内容")
