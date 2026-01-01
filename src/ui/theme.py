def inject_global_theme(st):
    """
    注入全局 CSS（暗色背景等），保证视觉和现在完全一致
    """
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
