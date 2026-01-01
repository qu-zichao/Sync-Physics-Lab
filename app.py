import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv

from transcribe.bibigpt import get_subtitle

load_dotenv()


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_timestamp(value: object) -> str:
    if value is None:
        return "00:00"
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return "00:00"
    if seconds > 10_000:
        seconds /= 1000.0
    seconds = max(0, int(seconds))
    minutes = seconds // 60
    remaining = seconds % 60
    return f"{minutes:02d}:{remaining:02d}"


st.set_page_config(page_title="Sync (同频) - Portal Lab", layout="centered")

st.markdown(
    """
<style>
/* 让页面更“科幻”一点：暗色背景 */
html, body, [data-testid="stAppViewContainer"] {
  background: radial-gradient(1200px 600px at 20% 0%, rgba(70,80,120,0.35), transparent 60%),
              radial-gradient(900px 500px at 90% 20%, rgba(120,70,120,0.25), transparent 55%),
              #070A12;
  color: #EAEAF2;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Sync (同频) — Don't just watch physics. Play with it.")

# --- 状态：是否进入实验室（第二空间） ---
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

# --- 1) “视频入口 + 迷雾 + 实验室浮层”整体舞台 ---
fog_opacity = 0.55 if st.session_state.lab_mode else 0.15
panel_opacity = 1.0 if st.session_state.lab_mode else 0.0
glow = "0 0 30px rgba(120,180,255,0.25)" if st.session_state.lab_mode else "none"

subtitle_block_html = ""
if st.session_state.lab_mode and st.session_state.subtitles:
    lines = []
    for entry in st.session_state.subtitles[:15]:
        start_time = entry.get("startTime") or entry.get("start") or 0
        text = escape_html(str(entry.get("text", "")).strip())
        timestamp = format_timestamp(start_time)
        if text:
            lines.append(f"{timestamp} {text}")
    if lines:
        subtitle_lines_html = "<br/>".join(lines)
        subtitle_block_html = f"""
        <div style="
          margin-top:12px;
          background: rgba(10,14,28,0.45);
          border: 1px solid rgba(255,255,255,0.10);
          border-radius: 16px;
          padding: 12px 14px;
          box-shadow: 0 10px 35px rgba(0,0,0,0.30);
          pointer-events:auto;
        ">
          <div style="font-size:13px; opacity:0.85;">SUBTITLES</div>
          <div style="
            margin-top:6px;
            font-size:12px;
            line-height:1.45;
            max-height:180px;
            overflow-y:auto;
          ">{subtitle_lines_html}</div>
        </div>
        """

stage_html = f"""
<div style="position:relative; width:100%; max-width:980px; margin: 0 auto;">
  <div style="position:relative; padding-top:56.25%; border-radius:18px; overflow:hidden; box-shadow:{glow};">
    <iframe
      src="{video_url}"
      title="video"
      style="position:absolute; inset:0; width:100%; height:100%; border:0;"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      allowfullscreen>
    </iframe>

    <!-- 迷雾层 -->
    <div style="
      position:absolute; inset:0;
      background:
        radial-gradient(800px 500px at 20% 30%, rgba(255,255,255,0.10), transparent 60%),
        radial-gradient(900px 600px at 80% 40%, rgba(120,180,255,0.10), transparent 60%),
        linear-gradient(180deg, rgba(0,0,0,{fog_opacity}), rgba(0,0,0,{fog_opacity}));
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      transition: all 300ms ease;
    "></div>

    <!-- 实验室浮层面板（先做视觉，下一步我们把真实控件“搬进来”） -->
    <div style="
      position:absolute; left:16px; top:16px; right:16px;
      opacity:{panel_opacity};
      transition: opacity 250ms ease;
      pointer-events:none;
    ">
      <div style="
        display:flex; gap:12px; align-items:flex-start;
      ">
        <div style="
          flex:1;
          background: rgba(10,14,28,0.55);
          border: 1px solid rgba(140,180,255,0.22);
          border-radius: 16px;
          padding: 12px 14px;
          box-shadow: 0 10px 35px rgba(0,0,0,0.35);
        ">
          <div style="font-size:13px; opacity:0.85;">VIRTUAL LAB</div>
          <div style="font-size:18px; font-weight:700; margin-top:4px;">参数控制台</div>
          <div style="margin-top:8px; font-size:13px; opacity:0.85;">
            现在你不是在“看”，你在“操控”物理。
          </div>
          <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
            <span style="font-size:12px; padding:4px 8px; border-radius:999px; background: rgba(120,180,255,0.12); border:1px solid rgba(120,180,255,0.20);">g</span>
            <span style="font-size:12px; padding:4px 8px; border-radius:999px; background: rgba(255,160,220,0.10); border:1px solid rgba(255,160,220,0.18);">v0</span>
            <span style="font-size:12px; padding:4px 8px; border-radius:999px; background: rgba(160,255,190,0.08); border:1px solid rgba(160,255,190,0.16);">θ</span>
          </div>
        </div>

        <div style="
          width:260px;
          background: rgba(10,14,28,0.45);
          border: 1px solid rgba(255,255,255,0.10);
          border-radius: 16px;
          padding: 12px 14px;
          box-shadow: 0 10px 35px rgba(0,0,0,0.30);
        ">
          <div style="font-size:13px; opacity:0.85;">SYNC STATUS</div>
          <div style="margin-top:6px; font-size:13px; line-height:1.35; opacity:0.90;">
            • 视频：已加载<br/>
            • 实验室：已开启<br/>
            • 下一步：接字幕 → 识别模型
          </div>
        </div>
        {subtitle_block_html}
      </div>
    </div>

  </div>
</div>
"""
st.components.v1.html(stage_html, height=560)

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
