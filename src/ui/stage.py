from typing import Iterable, Mapping


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


def _build_subtitle_block(subtitles: Iterable[Mapping[str, object]], lab_mode: bool) -> str:
    if not lab_mode:
        return ""

    lines = []
    for entry in list(subtitles)[:15]:
        start_time = entry.get("startTime") or entry.get("start") or 0
        text = escape_html(str(entry.get("text", "")).strip())
        timestamp = format_timestamp(start_time)
        if text:
            lines.append(f"{timestamp} {text}")

    if not lines:
        return ""

    subtitle_lines_html = "<br/>".join(lines)
    return f"""
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


def render_stage(st, video_url: str, lab_mode: bool) -> None:
    fog_opacity = 0.55 if lab_mode else 0.15
    panel_opacity = 1.0 if lab_mode else 0.0
    glow = "0 0 30px rgba(120,180,255,0.25)" if lab_mode else "none"

    subtitles = st.session_state.get("subtitles", [])
    subtitle_block_html = _build_subtitle_block(subtitles, lab_mode)

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
