import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv

from transcribe.bibigpt import get_subtitle
from src.ui.stage import render_stage
from src.ui.theme import inject_global_theme

load_dotenv()


def main():
    st.set_page_config(page_title="Sync (同频) - Portal Lab", layout="centered")

    inject_global_theme(st)

    st.title("Sync (同频) — Don't just watch physics. Play with it.")

    if "lab_mode" not in st.session_state:
        st.session_state.lab_mode = True  # 默认直接进入，符合你黑客松 demo 节奏
    if "subtitles" not in st.session_state:
        st.session_state.subtitles = []
    if "subtitle_error" not in st.session_state:
        st.session_state.subtitle_error = None

    col_a, col_b, col_c, col_d = st.columns([3, 1, 1, 1])
    with col_a:
        video_url = st.text_input(
            "视频链接（先用 YouTube/B站可访问链接；黑客松先跑通视觉）",
            value="https://www.youtube.com/embed/z5U843Ob8xw",
        )
    with col_b:
        st.session_state.lab_mode = st.toggle("进入实验室", value=st.session_state.lab_mode)
    with col_c:
        audio_language = st.selectbox(
            "字幕语言",
            ["auto", "zh", "en", "ja", "ko"],
            index=0,
        )
    with col_d:
        fetch_clicked = st.button("获取字幕")

    if fetch_clicked:
        try:
            subtitles = get_subtitle(video_url, audio_language)
            if subtitles:
                st.session_state.subtitles = subtitles
                st.session_state.subtitle_error = None
            else:
                st.session_state.subtitles = []
                st.session_state.subtitle_error = {
                    "message": "未找到字幕。",
                    "status_code": None,
                    "body_snippet": None,
                }
        except RuntimeError as exc:
            st.session_state.subtitles = []
            st.session_state.subtitle_error = {
                "message": str(exc),
                "status_code": getattr(exc, "status_code", None),
                "body_snippet": getattr(exc, "body_snippet", None),
            }

    subtitle_error = st.session_state.get("subtitle_error")
    if subtitle_error:
        message = subtitle_error.get("message", "字幕获取失败")
        status_code = subtitle_error.get("status_code")
        body_snippet = subtitle_error.get("body_snippet")
        details = []
        if status_code is not None:
            details.append(f"Status code: {status_code}")
        if body_snippet is not None:
            snippet = body_snippet if body_snippet else "(empty)"
            details.append(f"Response snippet: {snippet}")
        if details:
            message = f"{message}\n\n" + "\n".join(details)
        st.error(message)

    render_stage(st, video_url, st.session_state.lab_mode)

    st.divider()

    # --- 2) 先做一个“真实可交互”的小实验（暂时在舞台下方，下一步我们把它浮到视频上） ---
    st.subheader("快速验证：你已经能“操控”一个物理系统了")
    a = st.slider("参数 a（控制波形频率）", 0.5, 10.0, 2.0, 0.1)

    x = np.linspace(0, 2 * np.pi, 600)
    y = np.sin(a * x)

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("y = sin(a·x)")
    st.pyplot(fig)

    st.caption("里程碑1完成标志：你看到上方‘视频变暗 + 迷雾 + 浮层实验室’，下方滑块能改变曲线。")


if __name__ == "__main__":
    main()
