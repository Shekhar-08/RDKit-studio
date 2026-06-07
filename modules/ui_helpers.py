import streamlit as st
import base64


def render_svg(svg_str: str, max_width: str = "100%"):
    """Render an SVG string inside a responsive glassmorphic container."""
    b64 = base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')
    html = f"""
    <div class="chemical-card" style="display: flex; justify-content: center; align-items: center;
         background: rgba(10,18,42,0.72); border-radius: 12px; padding: 16px;">
        <img src="data:image/svg+xml;base64,{b64}"
             style="max-width: {max_width}; height: auto; display: block;" />
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def card_header(title: str, subtitle: str = None, badge: str = None):
    """Render a premium section header with optional badge and subtitle."""
    badge_html    = f'<span class="badge-teal">{badge}</span>' if badge else ''
    subtitle_html = (
        f'<div style="color:#94a3b8;font-size:0.9rem;margin-top:4px;">{subtitle}</div>'
        if subtitle else ''
    )
    st.markdown(f"""
        <div style="margin-bottom:20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <h3 style="margin:0;font-weight:600;color:#ffffff;font-size:1.25rem;">{title}</h3>
                {badge_html}
            </div>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, col=None):
    """Render a styled metric card (pass a Streamlit column object to render inside it)."""
    html = f"""
    <div class="chemical-card" style="padding:16px !important;margin-bottom:10px !important;">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
    if col:
        col.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)
