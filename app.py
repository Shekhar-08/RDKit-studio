import streamlit as st
import pandas as pd
import base64
import os
from rdkit import Chem
from modules.ui_helpers import render_svg, card_header, metric_card
from modules import (
    io_module, structure_module, substructure_module,
    transformation_module, fingerprint_module, descriptor_module, reaction_module
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
# Fixed: Using the public raw GitHub link so Streamlit Cloud can display the icon tab
LOGO_B64 = "https://github.com/Shekhar-08/RDKit-studio/blob/main/RDKit_logo.png?raw=true"

st.set_page_config(
    page_title="RDKit Studio",
    page_icon=LOGO_B64,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# LOAD EMBEDDED ASSETS (BASE64 ENCODING FIX)
# ─────────────────────────────────────────────
# Fixed: Fetching background image at runtime and converting to base64 data URI.
# This bypasses Streamlit Cloud's CSP which blocks external URLs in CSS pseudo-elements.
import urllib.request

@st.cache_data(show_spinner=False)
def get_bg_base64():
    url = "https://github.com/Shekhar-08/RDKit-studio/blob/main/Rdkit_background.png?raw=true"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read()
        return base64.b64encode(data).decode("utf-8")
    except Exception:
        return None

_bg_raw = get_bg_base64()
BG_B64 = f"data:image/png;base64,{_bg_raw}" if _bg_raw else "https://github.com/Shekhar-08/RDKit-studio/blob/main/Rdkit_background.png?raw=true"
AUTHOR_B64 = "https://avatars.githubusercontent.com/u/210685307?s=400&u=116167314105ea4825f635fe91de751cc2cda4f5&v=4"

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Global reset — force every Streamlit wrapper transparent ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="block-container"],
.main, .block-container,
section.main > div,
div.stApp, div[class^="appview-container"],
div[class*="appview"], div[class*="main"] {{
    font-family: 'Outfit', sans-serif !important;
    color: #ffffff !important;
    background: transparent !important;
    background-color: transparent !important;
    font-size: 1.12rem !important;
}}

/* ── Targets standard inner text blocks, labels, and regular markdown ── */
p, span, label, .stMarkdown p {{
    font-size: 1.12rem !important;
}}

/* ── Real DOM background div (pseudo-elements are blocked on Streamlit Cloud) ── */
#rdkit-bg-div {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: url('{BG_B64}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    filter: brightness(0.42) saturate(1.4);
    z-index: -9999;
    pointer-events: none;
}}

/* ── Dark overlay div ── */
#rdkit-overlay-div {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: linear-gradient(135deg,
        rgba(2,8,22,0.60) 0%,
        rgba(4,14,38,0.55) 60%,
        rgba(2,10,28,0.62) 100%);
    z-index: -9998;
    pointer-events: none;
}}

/* ── Hide sidebar, default header, decoration, footer ── */
[data-testid="stSidebar"],
[data-testid="stSidebarNav"],
header[data-testid="stHeader"],
div[data-testid="stDecoration"],
footer {{ display: none !important; }}
#MainMenu {{ visibility: hidden !important; }}

/* ── Main block padding ── */
.block-container {{
    padding: 0 2rem 2rem 2rem !important;
    max-width: 1440px !important;
    margin: 0 auto !important;
}}

/* ── TOP NAVBAR ── */
.navbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 28px;
    background: rgba(2, 6, 18, 0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(56,189,248,0.18);
    position: sticky;
    top: 0;
    z-index: 999;
    margin: 0 -2rem 24px -2rem;
    box-shadow: 0 4px 40px rgba(0,0,0,0.6);
}}
.navbar-left {{
    display: flex;
    align-items: center;
    gap: 14px;
}}
.navbar-left img {{
    height: 68px;
    width: auto;
    object-fit: contain;
    filter: drop-shadow(0 0 14px rgba(56,189,248,0.6)) drop-shadow(0 2px 8px rgba(0,0,0,0.8));
}}
.navbar-brand {{
    font-size: 1.35rem;
    font-weight: 700;
    background: linear-gradient(135deg, #38bdf8 0%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    white-space: nowrap;
}}
.navbar-tagline {{
    font-size: 0.68rem;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    margin-top: 2px;
}}
.navbar-right {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.8rem;
    color: #ffffff;
    font-weight: 500;
}}

/* ── Streamlit nav-button row (functional) ── */
div[data-testid="stHorizontalBlock"] > div > div > div > div > button {{
    background: rgba(255,255,255,0.04) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    font-size: 1.00rem !important;
    font-weight: 500 !important;
    font-family: 'Outfit', sans-serif !important;
    padding: 7px 4px !important;
    transition: all 0.2s ease !important;
}}
div[data-testid="stHorizontalBlock"] > div > div > div > div > button:hover {{
    background: rgba(56,189,248,0.14) !important;
    border-color: rgba(56,189,248,0.5) !important;
    color: #38bdf8 !important;
}}

/* ── HERO ── */
.hero-section {{
    text-align: center;
    padding: 56px 20px 36px;
}}
/* Fixed: Increased the size from 200px to 340px to eliminate empty space and make the center logo stand out beautifully */
.hero-logo {{
    width: 940px;
    height: 240px;
    object-fit: contain;
    filter: drop-shadow(0 0 35px rgba(56,189,248,0.75)) drop-shadow(0 6px 20px rgba(0,0,0,0.95));
    margin-bottom: 32px;
    animation: float 4s ease-in-out infinite;
}}
@keyframes float {{
    0%, 100% {{ transform: translateY(0px); }}
    50%       {{ transform: translateY(-12px); }}
}}
.hero-title {{
    font-size: 3.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #2986cc 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.04em;
    line-height: 1.1;
    margin-bottom: 14px;
    filter: drop-shadow(0 2px 12px rgba(0,0,0,0.9));
}}
.hero-subtitle {{
    font-size: 1.18rem;
    color: #ffffff;
    max-width: 680px;
    margin: 0 auto 34px;
    line-height: 1.65;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
}}
.hero-badges {{
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 40px;
}}
.badge {{
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.3);
    color: #38bdf8;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}}

/* ── FEATURE GRID ── */
.feature-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin: 28px 0;
}}
.feature-card {{
    background: rgba(4, 10, 28, 0.88);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 16px;
    padding: 24px;
    transition: all 0.3s ease;
}}
.feature-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(56,189,248,0.35);
    box-shadow: 0 12px 40px rgba(56,189,248,0.12);
}}
.feature-icon {{ font-size: 2rem; margin-bottom: 12px; display: block; }}
.feature-title {{ font-size: 1.08rem; font-weight: 700; color: #ffffff; margin-bottom: 10px; letter-spacing: -0.01em; }}
.feature-desc  {{ font-size: 0.88rem; color: #cbd5e1; line-height: 1.6; }}

/* ── GLASS / CHEMICAL CARDS ── */
.glass-card {{
    background: rgba(4, 10, 28, 0.88);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(56,189,248,0.15);
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
}}
.chemical-card {{
    background: rgba(4, 10, 28, 0.88) !important;
    backdrop-filter: blur(18px) !important;
    border: 1px solid rgba(56,189,248,0.15) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
}}
.chemical-svg-container {{
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 10px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}}

/* ── AUTHOR CARD ── */
.author-card {{
    display: flex;
    gap: 28px;
    align-items: flex-start;
    background: rgba(10, 18, 42, 0.82);
    border: 1px solid rgba(56,189,248,0.22);
    border-radius: 20px;
    padding: 32px;
    margin-bottom: 24px;
}}
.author-photo {{
    width: 130px;
    height: 130px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid #38bdf8;
    box-shadow: 0 0 30px rgba(56,189,248,0.4);
    flex-shrink: 0;
}}
.author-photo-placeholder {{
    width: 130px; height: 130px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #34d399);
    display: flex align-items: center; justify-content: center;
    font-size: 3rem; flex-shrink: 0;
    border: 3px solid #38bdf8;
}}
.author-name  {{ font-size: 1.6rem;  font-weight: 700; color: #f0f4f8;  margin-bottom: 4px; }}
.author-role  {{ font-size: 0.95rem; color: #38bdf8;  margin-bottom: 14px; font-weight: 500; }}
.author-bio   {{ font-size: 0.9rem;  color: #cbd5e1;  line-height: 1.7; margin-bottom: 18px; }}
.author-links {{ display: flex; gap: 12px; flex-wrap: wrap; }}
.author-link  {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 7px 16px; border-radius: 8px;
    border: 1px solid rgba(56,189,248,0.3);
    background: rgba(56,189,248,0.08);
    color: #38bdf8 !important; font-size: 0.84rem; font-weight: 500;
    text-decoration: none !important; transition: all 0.2s;
}}
.author-link:hover {{ background: rgba(56,189,248,0.18); border-color: #38bdf8; }}

/* ── INFO ROW ── */
.info-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px; margin: 20px 0;
}}
.info-item {{
    background: rgba(10,18,42,0.7);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 18px 20px;
}}
.info-label {{
    font-size: 0.75rem; color: #94a3b8;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px;
}}
.info-value {{ font-size: 0.95rem; color: #ffffff; font-weight: 600; }}

/* ── FOOTER ── */
.app-footer {{
    text-align: center; padding: 20px; margin-top: 48px;
    border-top: 1px solid rgba(255,255,255,0.07);
    color: #94a3b8; font-size: 0.82rem;
}}
.app-footer a {{ color: #38bdf8; text-decoration: none; }}

/* ── HELP CARDS ── */
.help-card {{
    background: rgba(10, 18, 42, 0.72);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 22px 26px; margin-bottom: 16px;
}}
.help-card h4 {{ color: #38bdf8; font-size: 1rem; margin-bottom: 8px; font-weight: 600; }}
.help-card p, .help-card li {{ color: #cbd5e1; font-size: 0.88rem; line-height: 1.6; }}

/* ── METRIC / BADGE ── */
.metric-value {{
    font-size: 2.2rem !important; font-weight: 700 !important;
    background: linear-gradient(135deg, #38bdf8 0%, #34d399 100%) !important;
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
}}
.metric-label {{
    font-size: 0.82rem !important; color: #94a3b8 !important;
    text-transform: uppercase !important; letter-spacing: 0.06em !important;
}}
.badge-teal {{
    background: rgba(56,189,248,0.1) !important; color: #38bdf8 !important;
    border: 1px solid rgba(56,189,248,0.3) !important;
    padding: 4px 12px !important; border-radius: 9999px !important;
    font-size: 0.75rem !important; font-weight: 600 !important; display: inline-block !important;
}}

/* ── Streamlit widget dark overrides ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {{
    background: rgba(10,18,42,0.85) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}}
.stButton>button {{
    background: linear-gradient(135deg, rgba(56,189,248,0.15) 0%, rgba(52,211,153,0.15) 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(56,189,248,0.3) !important;
    border-radius: 8px !important; font-weight: 500 !important;
    transition: all 0.2s ease !important;
}}
.stButton>button:hover {{
    background: linear-gradient(135deg, rgba(56,189,248,0.3) 0%, rgba(52,211,153,0.3) 100%) !important;
    border-color: #38bdf8 !important; color: #38bdf8 !important;
    box-shadow: 0 0 14px rgba(56,189,248,0.25) !important;
}}
div[data-testid="stMarkdownContainer"] p {{ color: #ffffff !important; }}
button[data-baseweb="tab"] {{ color: #94a3b8 !important; font-family: 'Outfit', sans-serif !important; }}
button[aria-selected="true"] {{ color: #38bdf8 !important; font-weight: 600 !important; }}
h1,h2,h3,h4 {{ color: #ffffff !important; }}
::-webkit-scrollbar {{ width: 7px; }}
::-webkit-scrollbar-track {{ background: rgba(0,0,0,0.2); }}
::-webkit-scrollbar-thumb {{ background: rgba(56,189,248,0.25); border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# ── Inject real DOM divs for background + overlay (pseudo-elements are unreliable on Streamlit Cloud) ──
st.markdown('<div id="rdkit-bg-div"></div><div id="rdkit-overlay-div"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "active_mol" not in st.session_state:
    st.session_state.active_mol  = Chem.MolFromSmiles("CC(C)Cc1ccc(cc1)C(C)C(=O)O")
    st.session_state.active_name = "Ibuprofen"

if "batch_mols" not in st.session_state:
    smiles_list = [
        ("CC(C)Cc1ccc(cc1)C(C)C(=O)O", "Ibuprofen"),
        ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  "Caffeine"),
        ("CC(=O)Oc1ccccc1C(=O)O",           "Aspirin"),
        ("CC(=O)Nc1ccc(O)cc1",              "Acetaminophen"),
    ]
    st.session_state.batch_mols  = [Chem.MolFromSmiles(s) for s, _ in smiles_list]
    st.session_state.batch_names = [n for _, n in smiles_list]
    for m, name in zip(st.session_state.batch_mols, st.session_state.batch_names):
        if m:
            m.SetProp("_Name", name)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def set_page(p):
    st.session_state.page = p

def footer():
    st.markdown("""
    <div class="app-footer">
        🧪 <strong>RDKit Studio</strong> · Built by
        <a href="https://github.com/Shekhar-08" target="_blank">Shekhar Gudda</a> ·
        M.Sc. Bioinformatics, DES Pune University
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TOP NAVBAR  (logo + branding bar)
# ─────────────────────────────────────────────
pages = ["Home", "App", "About", "Help", "Connect"]
icons = ["🏠",   "🧪",  "👤",    "❓",   "📬"]

logo_html = (
    f'<img src="{LOGO_B64}" alt="RDKit Studio Logo">'
    if LOGO_B64
    else '<span style="font-size:2.2rem;">🧪</span>'
)

st.markdown(f"""
<div class="navbar">
  <div class="navbar-left">
    {logo_html}
    <div>
      <div class="navbar-brand">RDKit Studio</div>
      <div class="navbar-tagline">Chemical Intelligence Suite</div>
    </div>
  </div>
  <div class="navbar-right">🔬 v2.0 &nbsp;|&nbsp; RDKit + Streamlit</div>
</div>
""", unsafe_allow_html=True)

# Functional navigation buttons (Streamlit handles clicks)
nav_cols = st.columns(len(pages))
for i, (pg, ic) in enumerate(zip(pages, icons)):
    with nav_cols[i]:
        if st.button(f"{ic} {pg}", key=f"navbtn_{pg}", use_container_width=True):
            set_page(pg)
            st.rerun()

st.markdown("<hr style='border-color:rgba(255,255,255,0.06);margin:0 0 20px'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: HOME
# ─────────────────────────────────────────────
if st.session_state.page == "Home":

    hero_logo = (
        f'<img class="hero-logo" src="{LOGO_B64}" alt="Logo">'
        if LOGO_B64
        else '<div style="font-size:10rem;margin-bottom:20px">🧪</div>'
    )

    st.markdown(f"""
    <div class="hero-section">
        {hero_logo}
        <div class="hero-title">RDKit Chemical Studio</div>
        <div class="hero-subtitle">
            An advanced, interactive cheminformatics research platform powered by RDKit.
            Visualize, analyze, transform, and simulate chemical structures with a single tool.
        </div>
        <div class="hero-badges">
            <span class="badge">🔬 RDKit Powered</span>
            <span class="badge">🧬 Interactive 3D</span>
            <span class="badge">⚗️ Reaction Simulator</span>
            <span class="badge">📊 Descriptor Analysis</span>
            <span class="badge">🎯 Substructure Search</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="feature-icon">🔍</span>
            <div class="feature-title">Active Molecule Viewer</div>
            <div class="feature-desc">Inspect 2D structures, generate 3D conformers, explore atom/bond tables and download as SVG, MOL, or PDB.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">📦</span>
            <div class="feature-title">Batch Dataset Manager</div>
            <div class="feature-desc">Load SDF or SMILES datasets, browse metadata and run diversity picking with MaxMinPicker.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🎯</span>
            <div class="feature-title">Substructure Search</div>
            <div class="feature-desc">Query molecules using SMILES or SMARTS with chirality matching, sidechain constraints and highlighted results.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">✂️</span>
            <div class="feature-title">Edits &amp; Scaffolds</div>
            <div class="feature-desc">Delete or replace substructures, compute Bemis-Murcko scaffolds, BRICS/RECAP fragmentation and MCS.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🧬</span>
            <div class="feature-title">Fingerprints &amp; Similarity</div>
            <div class="feature-desc">Generate Morgan, RDKit, Atom Pair, Torsion and MACCS fingerprints with similarity heatmaps and bit views.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">📈</span>
            <div class="feature-title">Descriptors &amp; Charges</div>
            <div class="feature-desc">Calculate 20+ physicochemical descriptors, Lipinski radar charts and Gasteiger partial charge maps.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">⚗️</span>
            <div class="feature-title">Reaction Simulator</div>
            <div class="feature-desc">Run Reaction SMARTS simulations, apply atom protection groups and download all products as SDF.</div>
        </div>
        <div class="feature-card">
            <span class="feature-icon">🚀</span>
            <div class="feature-title">Cloud Ready</div>
            <div class="feature-desc">Fully deployable on Streamlit Cloud — push to GitHub and share instantly with collaborators worldwide.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    footer()

# ─────────────────────────────────────────────
# PAGE: APP
# ─────────────────────────────────────────────
elif st.session_state.page == "App":

    with st.expander("⚗️ Molecule Input Panel", expanded=False):
        inp_col1, inp_col2, inp_col3 = st.columns([1.2, 1.2, 1])

        with inp_col1:
            input_method = st.radio("Input Method", ["SMILES", "MolBlock Text", "Upload File"], horizontal=True, key="input_method_radio")

        with inp_col2:
            new_mol  = None
            new_name = st.session_state.active_name

            if input_method == "SMILES":
                smi_input = st.text_input("SMILES String", "CC(C)Cc1ccc(cc1)C(C)C(=O)O")
                new_name  = st.text_input("Molecule Name", "Ibuprofen")
                if st.button("✅ Load SMILES"):
                    mol = io_module.mol_from_input(smi_input, "SMILES")
                    if mol:
                        new_mol = mol
                        st.success("Parsed successfully!")
                    else:
                        st.error("Invalid SMILES.")

            elif input_method == "MolBlock Text":
                block_input = st.text_area("Paste MDL Mol Block", height=120)
                new_name    = st.text_input("Molecule Name", "Custom Molecule")
                if st.button("✅ Load MolBlock"):
                    mol = io_module.mol_from_input(block_input, "MolBlock")
                    if mol:
                        new_mol = mol
                        st.success("Parsed!")
                    else:
                        st.error("Invalid MolBlock.")

            else:
                uploaded_file = st.file_uploader("Upload .mol/.sdf/.smi/.txt/.gz", type=["mol","sdf","smi","txt","gz"])
                if uploaded_file:
                    file_bytes = uploaded_file.read()
                    file_name  = uploaded_file.name
                    if file_name.endswith(".mol"):
                        mol = io_module.mol_from_input(file_bytes.decode("utf-8"), "MolBlock")
                        if mol:
                            new_mol = mol
                            new_name = file_name.replace(".mol","")
                    elif file_name.endswith((".sdf",".sdf.gz")):
                        mols, names, fails = io_module.parse_sdf_data(file_bytes, file_name.endswith(".gz"))
                        if mols:
                            st.session_state.batch_mols  = mols
                            st.session_state.batch_names = names
                            new_mol = mols[0]; new_name = names[0]
                            st.success(f"Loaded {len(mols)} molecules ({fails} fails).")
                    elif file_name.endswith((".smi",".txt")):
                        mols, names, fails = io_module.parse_smiles_data(file_bytes.decode("utf-8"))
                        if mols:
                            st.session_state.batch_mols  = mols
                            st.session_state.batch_names = names
                            new_mol = mols[0]; new_name = names[0]
                            st.success(f"Loaded {len(mols)} molecules ({fails} fails).")

        with inp_col3:
            if st.session_state.active_mol:
                st.markdown(f"**🔬 Active:** `{st.session_state.active_name}`")
                try:
                    svg_prev = structure_module.draw_molecule_svg(st.session_state.active_mol, width=200, height=150)
                    st.markdown(f'<div class="chemical-svg-container">{svg_prev}</div>', unsafe_allow_html=True)
                except Exception:
                    pass

    if new_mol is not None:
        st.session_state.active_mol  = new_mol
        st.session_state.active_name = new_name

    st.markdown("---")

    tabs = st.tabs([
        "🔍 Active Molecule",
        "📦 Batch Dataset",
        "🎯 Substructure Search",
        "✂️ Edits & Scaffolds",
        "🧬 Fingerprints",
        "📈 Descriptors & Charges",
        "⚗️ Reactions"
    ])

    # ── TAB 1 ──
    with tabs[0]:
        card_header("Active Molecule Viewer", "2D structure, 3D conformer, atom/bond tables", "Single Mode")
        col_draw, col_info = st.columns([1, 1])

        with col_draw:
            st.markdown("**🖼️ 2D Structure**")
            c1, c2, c3 = st.columns(3)
            add_hs      = c1.checkbox("Add H", value=False, key="toggle_h_main")
            add_indices = c2.checkbox("Atom Idx", value=False)
            add_stereo  = c3.checkbox("Stereo", value=True)
            m_display   = structure_module.toggle_hydrogens(st.session_state.active_mol, add_hs)
            svg_code    = structure_module.draw_molecule_svg(m_display, width=500, height=380, add_indices=add_indices, add_stereo=add_stereo)
            st.markdown(f'<div class="chemical-svg-container">{svg_code}</div>', unsafe_allow_html=True)
            s1, s2 = st.columns(2)
            s1.download_button("⬇️ SVG", svg_code, f"{st.session_state.active_name}.svg", "image/svg+xml")
            molblock_text = io_module.mol_to_molblock(st.session_state.active_mol, st.session_state.active_name)
            s2.download_button("⬇️ MOL", molblock_text, f"{st.session_state.active_name}.mol", "chemical/x-mdl-molfile")

        with col_info:
            st.markdown("**🔮 Interactive 3D Conformer**")
            style_3d = st.selectbox("Rendering Style", ["stick","sphere","line"])
            mol_3d   = structure_module.generate_3d_conformer(st.session_state.active_mol)
            if mol_3d:
                structure_module.render_3dmol_viewer(mol_3d, height=320, style=style_3d)
                st.download_button("⬇️ PDB", Chem.MolToPDBBlock(mol_3d), f"{st.session_state.active_name}_3D.pdb", "chemical/x-pdb")
            else:
                st.warning("Could not generate 3D conformer.")

        st.markdown("---")
        st.subheader("📋 Structural Inspection")
        tab_atoms, tab_bonds = st.tabs(["⚛️ Atoms", "🔗 Bonds"])
        with tab_atoms:
            df_atoms = structure_module.get_atoms_dataframe(st.session_state.active_mol)
            if not df_atoms.empty:
                st.dataframe(df_atoms, use_container_width=True)
                st.download_button("⬇️ Atoms CSV", df_atoms.to_csv(index=False), f"{st.session_state.active_name}_atoms.csv", "text/csv")
        with tab_bonds:
            df_bonds = structure_module.get_bonds_dataframe(st.session_state.active_mol)
            if not df_bonds.empty:
                st.dataframe(df_bonds, use_container_width=True)
                st.download_button("⬇️ Bonds CSV", df_bonds.to_csv(index=False), f"{st.session_state.active_name}_bonds.csv", "text/csv")

        st.markdown("---")
        st.subheader("🖼️ Extract from PNG Metadata")
        png_file = st.file_uploader("Upload RDKit PNG", type=["png"], key="png_meta_uploader")
        if png_file:
            extracted = structure_module.mol_from_png_metadata(png_file.read())
            if extracted:
                st.success("Extracted!")
                if st.button("Set as Active Molecule"):
                    st.session_state.active_mol  = extracted
                    st.session_state.active_name = png_file.name.replace(".png","")
                    st.rerun()
            else:
                st.error("No RDKit metadata found in PNG.")

    # ── TAB 2 ──
    with tabs[1]:
        card_header("Batch Dataset Manager", "Inspect loaded molecules, run diversity picking", "Batch Mode")
        if st.session_state.batch_mols:
            num_mols = len(st.session_state.batch_mols)
            st.write(f"Loaded batch: **{num_mols}** molecules")
            metadata_df = io_module.get_mols_metadata_df(st.session_state.batch_mols, st.session_state.batch_names)
            st.dataframe(metadata_df, use_container_width=True)
            d1, d2, d3 = st.columns(3)
            d1.download_button("⬇️ SDF",    io_module.mols_to_sdf_bytes(st.session_state.batch_mols),    "dataset.sdf",          "chemical/x-mdl-sdfile")
            d2.download_button("⬇️ SMILES", io_module.mols_to_smiles_bytes(st.session_state.batch_mols), "dataset.smi",          "text/plain")
            d3.download_button("⬇️ CSV",    metadata_df.to_csv(index=False),                             "dataset_metadata.csv", "text/csv")
            st.markdown("---")
            st.subheader("🎲 MaxMin Diversity Picker")
            pick_count = st.number_input("Pick N diverse molecules", 1, num_mols, min(3, num_mols))
            if st.button("🚀 Run Diversity Picker"):
                picked_indices = fingerprint_module.pick_diverse_mols(st.session_state.batch_mols, pick_count)
                picked_mols    = [st.session_state.batch_mols[i] for i in picked_indices]
                picked_names   = [st.session_state.batch_names[i] for i in picked_indices]
                st.success(f"Picked {len(picked_indices)} diverse molecules")
                cols = st.columns(len(picked_indices))
                for i, (m, name) in enumerate(zip(picked_mols, picked_names)):
                    cols[i].write(f"**{name}**")
                    svg_pick = structure_module.draw_molecule_svg(m, 200, 170)
                    cols[i].markdown(f'<div class="chemical-svg-container">{svg_pick}</div>', unsafe_allow_html=True)
        else:
            st.info("Upload an SDF or SMILES file in the input panel above.")

    # ── TAB 3 ──
    with tabs[2]:
        card_header("Substructure Search Engine", "Query with SMILES or SMARTS", "Searching")
        col_q, col_opt = st.columns([1.5, 1])
        with col_q:
            q_str  = st.text_input("Query (SMILES or SMARTS)", "ccO")
            q_type = st.radio("Query Language", ["SMARTS","SMILES"], horizontal=True)
        with col_opt:
            use_chirality     = st.checkbox("Match Stereochemistry", False)
            constraint_toggle = st.checkbox("Sidechain Constraints", False)
            constraint_type   = st.selectbox("Constraint Type", ["alkyl","all_carbon","no_nitrogen"], disabled=not constraint_toggle)

        st.markdown("---")
        col_active, col_dataset = st.columns([1, 1.2])

        with col_active:
            st.subheader("🔬 Active Molecule")
            has_match, matches, query, error_msg = substructure_module.find_substructure_matches(
                st.session_state.active_mol, q_str, q_type, use_chirality)
            if error_msg:
                st.error(error_msg)
            elif has_match:
                if constraint_toggle:
                    matches   = substructure_module.filter_matches_with_checker(st.session_state.active_mol, query, matches, constraint_type)
                    has_match = len(matches) > 0
                if has_match:
                    st.success(f"✅ {len(matches)} match(es) found")
                    hatoms, hbonds = substructure_module.get_highlight_atoms_and_bonds(st.session_state.active_mol, query, matches)
                    hl_color = st.color_picker("Highlight Color", "#ef4444")
                    hex_c    = hl_color.lstrip('#')
                    rgb_c    = tuple(int(hex_c[i:i+2], 16)/255.0 for i in (0,2,4))
                    svg_match = structure_module.draw_molecule_svg(
                        st.session_state.active_mol, 450, 340,
                        highlight_atoms=hatoms, highlight_atom_colors={i: rgb_c for i in hatoms},
                        highlight_bonds=hbonds, highlight_bond_colors={i: rgb_c for i in hbonds})
                    st.markdown(f'<div class="chemical-svg-container">{svg_match}</div>', unsafe_allow_html=True)
                else:
                    st.warning("Failed sidechain constraints.")
            else:
                st.warning("No match found.")

        with col_dataset:
            st.subheader("📦 Batch Search")
            if st.session_state.batch_mols and query is not None:
                matched_batch, matched_names = [], []
                for m, name in zip(st.session_state.batch_mols, st.session_state.batch_names):
                    b_match, b_idx, _, _ = substructure_module.find_substructure_matches(m, q_str, q_type, use_chirality)
                    if b_match:
                        if constraint_toggle:
                            b_idx = substructure_module.filter_matches_with_checker(m, query, b_idx, constraint_type)
                        if b_idx:
                            matched_batch.append(m); matched_names.append(name)
                st.write(f"**{len(matched_batch)}** matches in dataset")
                if matched_batch:
                    grid = st.columns(2)
                    for idx, (m, name) in enumerate(zip(matched_batch[:6], matched_names[:6])):
                        col = grid[idx % 2]
                        col.write(f"**{name}**")
                        bm, bi, _, _ = substructure_module.find_substructure_matches(m, q_str, q_type, use_chirality)
                        ha, hb = substructure_module.get_highlight_atoms_and_bonds(m, query, bi)
                        svg_m  = structure_module.draw_molecule_svg(m, 220, 170, highlight_atoms=ha, highlight_bonds=hb)
                        col.markdown(f'<div class="chemical-svg-container">{svg_m}</div>', unsafe_allow_html=True)
                    st.download_button("⬇️ Matched SDF", io_module.mols_to_sdf_bytes(matched_batch), "matched.sdf", "chemical/x-mdl-sdfile")
            else:
                st.info("Load a query above to search.")

    # ── TAB 4 ──
    with tabs[3]:
        card_header("Chemical Transformations & Scaffolds", "Modify structures or decompose into fragments", "Edit & Decompose")
        st.subheader("✏️ Substructure Edits")
        edit_mode = st.selectbox("Edit Action", ["Delete Substructure","Replace Substructure","Replace Core (Isolate Sidechains)"])
        col_e1, col_e2 = st.columns(2)

        with col_e1:
            st.write("**Original**")
            orig_svg = structure_module.draw_molecule_svg(st.session_state.active_mol, 400, 300)
            st.markdown(f'<div class="chemical-svg-container">{orig_svg}</div>', unsafe_allow_html=True)

        with col_e2:
            st.write("**Result**")
            prod_mol, error_msg = None, ""
            if edit_mode == "Delete Substructure":
                del_q = st.text_input("SMARTS to Delete", "C(=O)O")
                if del_q:
                    prod_mol, error_msg = transformation_module.delete_substructure(st.session_state.active_mol, del_q)
            elif edit_mode == "Replace Substructure":
                rep_q = st.text_input("SMARTS to Replace", "C(=O)O")
                rep_w = st.text_input("Replacement SMILES", "N")
                if rep_q and rep_w:
                    prod_mol, error_msg = transformation_module.replace_substructure(st.session_state.active_mol, rep_q, rep_w)
            else:
                core_q = st.text_input("Core SMARTS", "c1ccccc1")
                if core_q:
                    prod_mol, error_msg = transformation_module.replace_core(st.session_state.active_mol, core_q)

            if error_msg:
                st.error(error_msg)
            elif prod_mol:
                prod_svg = structure_module.draw_molecule_svg(prod_mol, 400, 300)
                st.markdown(f'<div class="chemical-svg-container">{prod_svg}</div>', unsafe_allow_html=True)
                if st.button("💾 Set as Active Molecule"):
                    st.session_state.active_mol  = prod_mol
                    st.session_state.active_name = f"{st.session_state.active_name}_edit"
                    st.rerun()
            else:
                st.warning("Awaiting inputs.")

        st.markdown("---")
        st.subheader("🧩 Fragmentation (Bemis-Murcko / BRICS / RECAP)")
        frag_type = st.radio("Type", ["Bemis-Murcko Scaffold","BRICS Decomposition","RECAP Deconstruction"], horizontal=True)
        if st.button("🚀 Run Decomposition"):
            if frag_type == "Bemis-Murcko Scaffold":
                scaff, err = transformation_module.get_murcko_scaffold(st.session_state.active_mol)
                if err:
                    st.error(err)
                elif scaff:
                    st.success(f"Scaffold SMILES: `{Chem.MolToSmiles(scaff)}`")
                    c1, c2 = st.columns(2)
                    svg_s = structure_module.draw_molecule_svg(scaff, 350, 270)
                    c2.markdown(f'<div class="chemical-svg-container">{svg_s}</div>', unsafe_allow_html=True)
                    st.download_button("⬇️ Scaffold MOL", io_module.mol_to_molblock(scaff), "scaffold.mol", "chemical/x-mdl-molfile")
            else:
                fn   = transformation_module.decompose_brics if "BRICS" in frag_type else transformation_module.decompose_recap
                label = "BRICS" if "BRICS" in frag_type else "RECAP"
                frags, err = fn(st.session_state.active_mol)
                if err:
                    st.error(err)
                elif frags:
                    st.success(f"{len(frags)} fragments via {label}")
                    fcols = st.columns(min(len(frags), 4))
                    for i, f in enumerate(frags):
                        fcols[i%4].write(f"`{Chem.MolToSmiles(f)}`")
                        svg_f = structure_module.draw_molecule_svg(f, 200, 170)
                        fcols[i%4].markdown(f'<div class="chemical-svg-container">{svg_f}</div>', unsafe_allow_html=True)
                    st.download_button(f"⬇️ {label} SDF", io_module.mols_to_sdf_bytes(frags), "fragments.sdf", "chemical/x-mdl-sdfile")
                else:
                    st.warning("Could not fragment molecule.")

        st.markdown("---")
        st.subheader("🔗 Maximum Common Substructure (MCS)")
        mc1, mc2 = st.columns(2)
        atom_compare = mc1.selectbox("Atom Rule", ["CompareElements","CompareAny","CompareAnyHeavyAtom"])
        bond_compare = mc2.selectbox("Bond Rule", ["CompareOrder","CompareAny","CompareOrderExact"])
        if st.button("🔍 Compute MCS"):
            if st.session_state.batch_mols and len(st.session_state.batch_mols) >= 2:
                mcs_res, err = transformation_module.find_maximum_common_substructure(
                    st.session_state.batch_mols, atom_compare, bond_compare)
                if err:
                    st.error(err)
                elif mcs_res:
                    st.success(f"MCS SMARTS: `{mcs_res['smarts']}`  ({mcs_res['num_atoms']} atoms, {mcs_res['num_bonds']} bonds)")
                    cm1, cm2 = st.columns([1,1.5])
                    svg_mcs  = structure_module.draw_molecule_svg(mcs_res["mol"], 300, 240)
                    cm1.markdown(f'<div class="chemical-svg-container">{svg_mcs}</div>', unsafe_allow_html=True)
                    mcs_cols = cm2.columns(3)
                    for i, (m, name) in enumerate(zip(st.session_state.batch_mols[:3], st.session_state.batch_names[:3])):
                        hm, bi, _, _ = substructure_module.find_substructure_matches(m, mcs_res["smarts"], "SMARTS")
                        ha, hb = substructure_module.get_highlight_atoms_and_bonds(m, mcs_res["mol"], bi)
                        mcs_cols[i].write(f"**{name}**")
                        svg_hm = structure_module.draw_molecule_svg(m, 190, 170, highlight_atoms=ha, highlight_bonds=hb)
                        mcs_cols[i].markdown(f'<div class="chemical-svg-container">{svg_hm}</div>', unsafe_allow_html=True)
            else:
                st.warning("Need ≥ 2 molecules in batch.")

    # ── TAB 5 ──
    with tabs[4]:
        card_header("Fingerprinting & Similarity Maps", "Binary descriptors, bit environments, similarity gradients", "Fingerprints")
        fp_select = st.selectbox("Fingerprint Type", ["Morgan (Circular)","RDKit (Topological)","Atom Pairs","Topological Torsions","MACCS Keys"])
        st.markdown("---")
        col_sim, col_bit = st.columns([1.2, 1])

        with col_sim:
            st.subheader("📏 Similarity Calculator")
            comp_smi   = st.text_input("Comparison SMILES", "CC(=O)Oc1ccccc1C(=O)O")
            sim_metric = st.selectbox("Metric", ["Tanimoto","Dice","Cosine","Sokal","Kulczynski","Tversky"])
            t_a, t_b   = 0.5, 0.5
            if sim_metric == "Tversky":
                t_a = st.slider("Alpha", 0.0, 1.0, 0.5)
                t_b = st.slider("Beta",  0.0, 1.0, 0.5)
            comp_mol = Chem.MolFromSmiles(comp_smi)
            if comp_mol:
                score = fingerprint_module.calculate_similarity(st.session_state.active_mol, comp_mol, fp_select, sim_metric, 2, 2048, t_a, t_b)
                metric_card(f"{sim_metric} Similarity", f"{score:.4f}")
                map_fp = "Morgan" if "Morgan" in fp_select else ("RDKit" if "RDKit" in fp_select else ("Atom Pairs" if "Atom" in fp_select else "Morgan"))
                svg_map = fingerprint_module.generate_similarity_map_svg(st.session_state.active_mol, comp_mol, fp_type=map_fp)
                st.markdown(f'<div class="chemical-svg-container">{svg_map}</div>', unsafe_allow_html=True)
                st.download_button("⬇️ Similarity Map SVG", svg_map, "sim_map.svg", "image/svg+xml")
            else:
                st.error("Invalid comparison SMILES.")

        with col_bit:
            st.subheader("🔬 Bit Environment Viewer")
            if "Morgan" in fp_select:
                radius_sel = st.slider("Radius", 1, 3, 2)
                bit_info, _ = fingerprint_module.get_morgan_bit_info(st.session_state.active_mol, radius_sel)
                active_bits = sorted(bit_info.keys())
                st.write(f"Active bits: **{len(active_bits)}**")
                bit_sel = st.selectbox("Select Bit", active_bits)
                if bit_sel:
                    svg_bit = fingerprint_module.draw_morgan_bit_env(st.session_state.active_mol, bit_sel, bit_info)
                    if svg_bit:
                        st.markdown(f'<div class="chemical-svg-container">{svg_bit}</div>', unsafe_allow_html=True)
                        st.download_button("⬇️ Bit SVG", svg_bit, f"bit_{bit_sel}.svg", "image/svg+xml")
            elif "RDKit" in fp_select:
                bit_info, _ = fingerprint_module.get_rdkit_bit_info(st.session_state.active_mol)
                active_bits = sorted(bit_info.keys())
                st.write(f"Active bits: **{len(active_bits)}**")
                bit_sel = st.selectbox("Select Bit", active_bits)
                if bit_sel:
                    svg_bit = fingerprint_module.draw_rdkit_bit_env(st.session_state.active_mol, bit_sel, bit_info)
                    if svg_bit:
                        st.markdown(f'<div class="chemical-svg-container">{svg_bit}</div>', unsafe_allow_html=True)
                        st.download_button("⬇️ Bit SVG", svg_bit, f"bit_{bit_sel}.svg", "image/svg+xml")
            else:
                st.info("Bit viewer available for Morgan and RDKit fingerprints.")

    # ── TAB 6 ──
    with tabs[5]:
        card_header("Descriptors & Partial Charges", "Physicochemical properties and Gasteiger charge maps", "Descriptors")
        col_desc, col_chg = st.columns([1, 1.2])
        with col_desc:
            st.subheader("📊 Physicochemical Descriptors")
            df_desc = descriptor_module.get_descriptors_dataframe(st.session_state.active_mol)
            if not df_desc.empty:
                st.dataframe(df_desc, use_container_width=True, height=360)
                st.download_button("⬇️ Descriptors CSV", df_desc.to_csv(index=False), f"{st.session_state.active_name}_desc.csv", "text/csv")
                st.markdown("---")
                st.write("**💊 Lipinski Radar Profile**")
                fig_radar = descriptor_module.get_radar_chart_plotly(st.session_state.active_mol)
                if fig_radar:
                    st.plotly_chart(fig_radar, use_container_width=True)
        with col_chg:
            st.subheader("⚡ Gasteiger Charge Map")
            st.write("Red = Negative, Blue = Positive")
            svg_chg = descriptor_module.draw_charge_distribution_svg(st.session_state.active_mol, 500, 420)
            st.markdown(f'<div class="chemical-svg-container">{svg_chg}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Charge Map SVG", svg_chg, "charge_map.svg", "image/svg+xml")

    # ── TAB 7 ──
    with tabs[6]:
        card_header("Reaction Simulator", "Run Reaction SMARTS, protect groups, generate products", "Synthesis")
        presets = {
            "Amide Bond Formation":    "[C:1](=[O:2])[O:3].[N:4]>>[C:1](=[O:2])[N:4]",
            "Click Triazole Coupling": "[C:1]#[C:2].[N:3]=[N+:4]=[N-:5]>>[c:1]1[c:2][n:3][n:4][n:5]1",
            "Esterification":          "[C:1](=[O:2])[O:3].[O:4]>>[C:1](=[O:2])[O:4]",
            "Suzuki Coupling":         "[c:1][B:2]([O:3])[O:4].[c:5][Cl,Br,I:6]>>[c:1][c:5]",
        }
        preset_choice = st.selectbox("Reaction Preset", list(presets.keys()) + ["Custom SMARTS"])
        rxn_smarts = st.text_input("Reaction SMARTS", presets.get(preset_choice, "[C:1](=[O:2])[O:3].[N:4]>>[C:1](=[O:2])[N:4]"))
        if preset_choice != "Custom SMARTS":
            rxn_smarts = presets[preset_choice]
            st.info(f"SMARTS: `{rxn_smarts}`")

        rxn, rxn_err = reaction_module.create_reaction(rxn_smarts)
        if rxn_err:
            st.error(rxn_err)
        elif rxn:
            st.markdown(reaction_module.draw_reaction_visualization(rxn), unsafe_allow_html=True)
            st.markdown("---")
            st.subheader("⚗️ Reactant Inputs")
            num_r    = rxn.GetNumReactantTemplates()
            defaults = ["CC(=O)O","CCN","C"]
            if "Click"  in preset_choice: defaults = ["C#CC","CCN=[N+]=[N-]","C"]
            if "Suzuki" in preset_choice: defaults = ["OB(O)c1ccccc1","Ic1ccccc1","C"]
            reactants_inputs = [
                st.text_input(f"Reactant {i+1} SMILES", defaults[i] if i < len(defaults) else "C", key=f"r_{i}")
                for i in range(num_r)
            ]
            reactants_mols, ready = [], True
            for i, ri in enumerate(reactants_inputs):
                m = Chem.MolFromSmiles(ri)
                if m is None:
                    st.error(f"Reactant {i+1} invalid."); ready = False
                else:
                    reactants_mols.append(m)
            protect_smarts = st.text_input("🛡️ Protect SMARTS (optional)", "")
            if ready and st.button("🚀 Run Reaction"):
                prod_sets, err = reaction_module.run_reaction(rxn, reactants_mols, protect_smarts)
                if err:
                    st.error(err)
                elif prod_sets:
                    st.success(f"Generated {len(prod_sets)} product set(s)")
                    all_prods = []
                    for s_idx, p_set in enumerate(prod_sets):
                        st.markdown(f"**Product Set {s_idx+1}:**")
                        pcols = st.columns(min(len(p_set), 4))
                        for p_idx, p in enumerate(p_set):
                            col = pcols[p_idx % 4]
                            col.write(f"`{Chem.MolToSmiles(p)}`")
                            svg_p = structure_module.draw_molecule_svg(p, 200, 170)
                            col.markdown(f'<div class="chemical-svg-container">{svg_p}</div>', unsafe_allow_html=True)
                            all_prods.append(p)
                    st.download_button("⬇️ All Products SDF", io_module.mols_to_sdf_bytes(all_prods), "products.sdf", "chemical/x-mdl-sdfile")
                else:
                    st.warning("No reaction products. Check reactant SMILES matches templates.")

    footer()

# ─────────────────────────────────────────────
# PAGE: ABOUT
# ─────────────────────────────────────────────
elif st.session_state.page == "About":

    st.markdown('<div style="padding: 10px 0 24px;"><h2 style="color:#38bdf8;font-weight:700;">👤 About</h2></div>', unsafe_allow_html=True)

    # Cleaned: Removed hidden web-formatting spaces and restructured onto a clear layout
    if AUTHOR_B64:
        author_img_html = f'<img class="author-photo" src="{AUTHOR_B64}" alt="Shekhar Gudda">'
    else:
        author_img_html = '<div class="author-photo-placeholder">👤</div>'

    st.markdown(f"""
    <div class="author-card">
        {author_img_html}
        <div style="flex:1">
            <div class="author-name">Shekhar Gudda</div>
            <div class="author-role">🔬 Bioinformatics Researcher · Computational Biologist</div>
            <div class="author-bio">
                I am deeply passionate about creating accessible, intelligent tools that bridge the gap between
                computational analysis and biological discovery. <strong>RDKit Studio</strong> is a web-based cheminformatics
                platform developed to make chemical structure analysis, molecular simulation, and drug-likeness
                profiling available to researchers, students, and educators through an intuitive interface
                powered by Streamlit and RDKit.
                <br><br>
                The motivation behind building RDKit Studio stems from the need for an all-in-one, browser-based
                platform for cheminformatics workflows — from 2D/3D visualization to reaction simulation, fingerprint
                analysis, and descriptor calculation — without requiring local installation of complex software.
            </div>
            <div class="author-links">
                <a class="author-link" href="https://github.com/Shekhar-08" target="_blank">🐙 GitHub</a>
                <a class="author-link" href="https://www.linkedin.com/in/shekhar-gudda-0299062ab/" target="_blank">💼 LinkedIn</a>
                <a class="author-link" href="mailto:shekhargudda844@gmail.com">📧 Email</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-row">
        <div class="info-item">
            <div class="info-label">🎓 Education</div>
            <div class="info-value">M.Sc. Bioinformatics </div>
        </div>
        <div class="info-item">
            <div class="info-label">🏛️ Institution</div>
            <div class="info-value">DES Pune University</div>
        </div>
        <div class="info-item">
            <div class="info-label">🔬 Research Focus</div>
            <div class="info-value">Cheminformatics · Computational Biology</div>
        </div>
        <div class="info-item">
            <div class="info-label">📧 Email</div>
            <div class="info-value">shekhargudda844@gmail.com</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<h3 style="color:#e2e8f0">🧪 About RDKit Studio</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div class="glass-card">
        <p style="color:#ffffff;line-height:1.8;font-size:0.95rem;">
        <strong style="color:#38bdf8;">RDKit Studio</strong> is a full-featured, browser-based cheminformatics research platform
        built on top of the industry-standard <strong>RDKit</strong> library. It provides an interactive graphical interface
        for a wide range of chemical analysis tasks:
        </p>
        <ul style="color:#ffffff;font-size:0.9rem;line-height:1.9;margin-top:10px;">
            <li>🔍 <strong style="color:#e2e8f0">2D/3D Structure Visualization</strong> — Draw molecules, generate conformers, and explore 3D geometry</li>
            <li>📦 <strong style="color:#e2e8f0">Batch Dataset Management</strong> — Load SDF/SMILES datasets and perform diversity analysis</li>
            <li>🎯 <strong style="color:#e2e8f0">Substructure Search</strong> — Query using SMILES or SMARTS with highlighting</li>
            <li>✂️ <strong style="color:#e2e8f0">Chemical Transformations</strong> — Edit structures, compute scaffolds, BRICS/RECAP fragmentation</li>
            <li>🧬 <strong style="color:#e2e8f0">Fingerprint Analysis</strong> — Morgan, RDKit, MACCS keys + similarity maps</li>
            <li>📊 <strong style="color:#e2e8f0">Descriptor Profiling</strong> — Lipinski properties, radar charts, Gasteiger charges</li>
            <li>⚗️ <strong style="color:#e2e8f0">Reaction Simulation</strong> — Run reactions using SMARTS with atom protection groups</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-row">
        <div class="info-item"><div class="info-label">⚙️ Backend</div><div class="info-value">RDKit ≥ 2023.03</div></div>
        <div class="info-item"><div class="info-label">🖥️ Frontend</div><div class="info-value">Streamlit ≥ 1.30</div></div>
        <div class="info-item"><div class="info-label">🔮 3D Viewer</div><div class="info-value">py3Dmol</div></div>
        <div class="info-item"><div class="info-label">📈 Plots</div><div class="info-value">Plotly</div></div>
        <div class="info-item"><div class="info-label">🌐 Deployment</div><div class="info-value">Streamlit Cloud</div></div>
        <div class="info-item"><div class="info-label">📦 Version</div><div class="info-value">v2.0</div></div>
    </div>
    """, unsafe_allow_html=True)

    footer()

# ─────────────────────────────────────────────
# PAGE: HELP
# ─────────────────────────────────────────────
elif st.session_state.page == "Help":

    st.markdown('<div style="padding: 10px 0 24px;"><h2 style="color:#38bdf8;font-weight:700;">❓ Help & Documentation</h2></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="help-card">
        <h4>🚀 Quick Start</h4>
        <ol>
            <li>Click <strong>"🧪 App"</strong> in the navigation bar to open the chemistry dashboard.</li>
            <li>Expand the <strong>"Molecule Input Panel"</strong> at the top of the page.</li>
            <li>Enter a SMILES string (e.g. <code>CC(C)Cc1ccc(cc1)C(C)C(=O)O</code> for Ibuprofen) or upload an SDF/SMILES file.</li>
            <li>Click <strong>"Load SMILES"</strong> to set the active molecule.</li>
            <li>Navigate between the 7 analysis tabs to explore different features.</li>
        </ol>
    </div>

    <div class="help-card">
        <h4>🔍 Tab 1 — Active Molecule Viewer</h4>
        <p>Displays your active molecule as a 2D SVG drawing. Toggle hydrogens, atom indices, and stereochemistry.
        Generate an interactive 3D conformer using ETKDGv3 + MMFF optimization. Download as SVG, MOL, or PDB.</p>
    </div>

    <div class="help-card">
        <h4>📦 Tab 2 — Batch Dataset Manager</h4>
        <p>After uploading an SDF or SMILES file, browse all molecules with their metadata.
        Use the <strong>MaxMin Diversity Picker</strong> to select the most chemically diverse subset using
        Morgan fingerprints.</p>
    </div>

    <div class="help-card">
        <h4>🎯 Tab 3 — Substructure Search</h4>
        <p>Enter a query in <strong>SMARTS</strong> (e.g. <code>[OH]</code> for hydroxyl) or <strong>SMILES</strong>.
        Matches are highlighted in your chosen color. Optionally enforce sidechain constraints (alkyl, all-carbon, no-nitrogen).
        Batch search across all loaded molecules.</p>
    </div>

    <div class="help-card">
        <h4>✂️ Tab 4 — Edits &amp; Scaffolds</h4>
        <ul>
            <li><strong>Delete Substructure</strong>: Remove atoms matching a SMARTS query.</li>
            <li><strong>Replace Substructure</strong>: Swap a fragment with a new SMILES group.</li>
            <li><strong>Replace Core</strong>: Cut out a ring core and isolate side chains.</li>
            <li><strong>Bemis-Murcko Scaffold</strong>: Extract the ring system + linkers.</li>
            <li><strong>BRICS / RECAP</strong>: Fragment using retrosynthetic rules.</li>
            <li><strong>MCS</strong>: Find the Maximum Common Substructure across a batch.</li>
        </ul>
    </div>

    <div class="help-card">
        <h4>🧬 Tab 5 — Fingerprints &amp; Similarity</h4>
        <p>Select a fingerprint type (Morgan, RDKit, Atom Pairs, Torsions, MACCS Keys) and compare your active
        molecule to any SMILES using Tanimoto, Dice, Cosine, Sokal, Kulczynski, or Tversky similarity.
        Visual similarity heatmaps show per-atom contributions.</p>
    </div>

    <div class="help-card">
        <h4>📈 Tab 6 — Descriptors &amp; Charges</h4>
        <p>Calculates 20+ physicochemical descriptors (MW, LogP, TPSA, HBD/A, RotBonds, QED…) and displays
        them with a Lipinski Rule-of-5 radar chart. The Gasteiger partial charge map color-codes atoms by
        electron density.</p>
    </div>

    <div class="help-card">
        <h4>⚗️ Tab 7 — Reaction Simulator</h4>
        <p>Choose a preset reaction (Amide Bond Formation, Click Chemistry, Esterification, Suzuki Coupling)
        or write your own Reaction SMARTS (<code>reactants>>products</code>). Enter reactant SMILES and
        optionally specify a SMARTS pattern to protect groups from reacting. Download all products as SDF.</p>
    </div>

    <div class="help-card">
        <h4>📁 Supported File Formats</h4>
        <ul>
            <li><code>.mol</code> — MDL MOL file (single molecule)</li>
            <li><code>.sdf</code> / <code>.sdf.gz</code> — Structure Data File (batch)</li>
            <li><code>.smi</code> / <code>.txt</code> — SMILES file (one SMILES per line)</li>
        </ul>
    </div>

    <div class="help-card">
        <h4>🐛 Common Issues</h4>
        <ul>
            <li><strong>3D conformer fails</strong>: Make sure the molecule has a valid valence. Try sanitizing the SMILES first.</li>
            <li><strong>Reaction produces no products</strong>: Verify that the reactant SMILES matches the reactant templates in the SMARTS.</li>
            <li><strong>MCS is empty</strong>: The batch molecules may be too structurally different. Try with a subset.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    footer()

# ─────────────────────────────────────────────
# PAGE: CONNECT
# ─────────────────────────────────────────────
elif st.session_state.page == "Connect":

    st.markdown('<div style="padding: 10px 0 24px;"><h2 style="color:#38bdf8;font-weight:700;">📬 Connect</h2></div>', unsafe_allow_html=True)

    col_c1, col_c2 = st.columns([1.1, 1])

    with col_c1:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color:#e2e8f0;margin-bottom:6px;">💬 Get in Touch</h3>
            <p style="color:#ffffff;font-size:0.9rem;margin-bottom:22px;">
                Have questions, suggestions, or want to collaborate? Reach out through any of these channels.
            </p>
            <div style="display:flex;flex-direction:column;gap:14px;">
                <a class="author-link" href="mailto:shekhargudda844@gmail.com" style="font-size:0.95rem;padding:12px 20px;">
                    📧 &nbsp; shekhargudda844@gmail.com
                </a>
                <a class="author-link" href="https://github.com/Shekhar-08" target="_blank" style="font-size:0.95rem;padding:12px 20px;">
                    🐙 &nbsp; github.com/Shekhar-08
                </a>
                <a class="author-link" href="https://www.linkedin.com/in/shekhar-gudda-0299062ab/" target="_blank" style="font-size:0.95rem;padding:12px 20px;">
                    💼 &nbsp; linkedin.com/in/shekhar-gudda-0299062ab
                </a>
            </div>
            <div style="margin-top:28px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.07);">
                <div class="info-label" style="margin-bottom:10px;">🏛️ Institution</div>
                <div style="color:#e2e8f0;font-size:0.95rem;font-weight:500;">DES Pune University</div>
                <div style="color:#ffffff;font-size:0.85rem;margin-top:4px;">Department of Bioinformatics</div>
                <div style="color:#ffffff;font-size:0.85rem;">Pune, Maharashtra, India</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color:#e2e8f0;margin-bottom:6px;">🐛 Report an Issue</h3>
            <p style="color:#ffffff;font-size:0.88rem;margin-bottom:16px;">
                Found a bug or have a feature request? Open an issue on GitHub.
            </p>
            <a class="author-link" href="https://github.com/Shekhar-08" target="_blank" style="font-size:0.92rem;padding:10px 18px;display:inline-flex;">
                🐙 Open GitHub Issue
            </a>

            <div style="margin-top:28px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.07);">
                <h3 style="color:#e2e8f0;margin-bottom:12px;">🤝 Collaborate</h3>
                <p style="color:#ffffff;font-size:0.88rem;line-height:1.7;">
                    I am open to collaborations in:<br>
                    • Cheminformatics &amp; Drug Discovery<br>
                    • Bioinformatics Tool Development<br>
                    • Computational Biology Research<br>
                    • Open-source Software Projects
                </p>
            </div>

            <div style="margin-top:24px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.07);">
                <h3 style="color:#e2e8f0;margin-bottom:12px;">⭐ Support the Project</h3>
                <p style="color:#ffffff;font-size:0.88rem;line-height:1.7;">
                    If RDKit Studio has been useful to you, consider starring the repository on GitHub
                    or sharing it with your colleagues and research community.
                </p>
                <a class="author-link" href="https://github.com/Shekhar-08" target="_blank" style="margin-top:10px;display:inline-flex;font-size:0.9rem;padding:9px 16px;">
                    ⭐ Star on GitHub
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    footer()