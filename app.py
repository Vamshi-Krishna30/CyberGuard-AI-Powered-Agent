import streamlit as st
import subprocess
import os
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS (Cyberpunk Hacker Aesthetic Theme) ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght=300;400;500;600&display=swap');

:root {
  --bg:     #0a0e1a;
  --panel:  #0f1628;
  --border: #1e2d4a;
  --accent: #00d4ff;
  --accent2:#00ff88;
  --danger: #ff4444;
  --warn:   #ffaa00;
  --muted:  #4a6080;
  --text:   #c8d8e8;
  --mono:   'Share Tech Mono', monospace;
  --sans:   'Inter', sans-serif;
}

/* ── GLOBAL BODY STYLING ── */
html, body, [data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--sans);
}

/* ── SIDEBAR FIXES & STYLE PRESERVATION ── */
[data-testid="stSidebar"] {
  background: var(--panel) !important;
  border-right: 1px solid var(--border) !important;
}

/* Fix width without crushing internal components */
[data-testid="stSidebarUserContent"] {
  padding-top: 1rem !important;
  width: 280px !important;
}

/* Ensure typography inside sidebar inherits theme styles */
[data-testid="stSidebar"] * {
  color: var(--text);
}

[data-testid="stSidebar"] strong {
  color: var(--accent) !important;
  font-family: var(--mono) !important;
  letter-spacing: 0.5px;
}

/* Clean up header and display toggle arrow */
[data-testid="stHeader"] {
  background: transparent !important;
}
[data-testid="stHeader"] > div:first-child {
  visibility: visible !important;
}

/* Style the default collapse arrow button nicely */
[data-testid="collapsedControl"] {
  background: #0f1628 !important;
  border: 1px solid #1e2d4a !important;
  border-radius: 0 8px 8px 0 !important;
  color: #00d4ff !important;
  top: 10px !important;
}
[data-testid="collapsedControl"]:hover {
  background: #1a2a4a !important;
  box-shadow: 0 0 10px #00d4ff44 !important;
}

/* Hide deploy button and extra clutter */
[data-testid="stActionButton"] { visibility: hidden !important; }
#MainMenu, footer { visibility: hidden !important; }

/* ── CYBERPUNK BUTTONS ── */
.stButton > button {
  background: linear-gradient(135deg, #003d66, #006699) !important;
  color: #00d4ff !important;
  border: 1px solid #00d4ff !important;
  border-radius: 6px !important;
  font-family: var(--mono) !important;
  font-size: 13px !important;
  letter-spacing: 1px !important;
  padding: 10px 28px !important;
  transition: all .2s !important;
  width: 100%;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #005588, #0088cc) !important;
  box-shadow: 0 0 16px #00d4ff55 !important;
  color: #00ff88 !important;
  border-color: #00ff88 !important;
}

/* ── CYBERPUNK FORM INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  background: #060d1a !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 6px !important;
  font-family: var(--mono) !important;
  font-size: 13px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 8px #00d4ff33 !important;
}

/* Styled Selectbox for modern Streamlit structure */
.stSelectbox div[data-baseweb="select"] > div {
  background: #060d1a !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 6px !important;
  font-family: var(--mono) !important;
  font-size: 13px !important;
}

/* Styled Radio Buttons for Sidebar */
[data-testid="stRadio"] label {
  font-family: var(--mono) !important;
  color: var(--text) !important;
  font-size: 13px !important;
}

/* ── DASHBOARD ELEMENTS ── */
.cyber-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.2rem 1.4rem;
  margin-bottom: 1rem;
}
.cyber-card.accent  { border-left: 3px solid var(--accent); }
.cyber-card.success { border-left: 3px solid var(--accent2); }
.cyber-card.danger  { border-left: 3px solid var(--danger); }
.cyber-card.warn    { border-left: 3px solid var(--warn); }

/* Terminal panel styling */
.terminal {
  background: #020810;
  border: 1px solid #1a2a3a;
  border-radius: 8px;
  padding: 1rem 1.2rem;
  font-family: var(--mono);
  font-size: 12px;
  color: #00d4ff;
  min-height: 200px;
  max-height: 440px;
  overflow-y: auto;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: inset 0 0 10px #000000;
}
.t-prompt { color: #00ff88; }
.t-error  { color: #ff4444; }
.t-warn   { color: #ffaa00; }
.t-info   { color: #88aaff; }

/* Stat blocks */
.stat-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 1rem;
}
.stat-box {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: .7rem .9rem;
  text-align: center;
}
.stat-n { font-size: 22px; font-weight: 600; font-family: var(--mono); }
.stat-l { font-size: 10px; color: var(--muted); margin-top: 2px; letter-spacing:.05em; text-transform:uppercase; }

/* Badges */
.badge {
  display: inline-block;
  font-size: 10px;
  font-family: var(--mono);
  padding: 2px 8px;
  border-radius: 3px;
  letter-spacing: .05em;
  margin-right: 5px;
}
.badge-ok   { background:#0a2a1a; color:#00ff88; border:1px solid #00ff8844; }
.badge-live { background:#1a0a0a; color:#ff4444; border:1px solid #ff444444; }
.badge-info { background:#0a1a2a; color:#00d4ff; border:1px solid #00d4ff44; }
.badge-warn { background:#1a1000; color:#ffaa00; border:1px solid #ffaa0044; }

/* Log lines */
.log-line { padding:4px 0; border-bottom:1px solid #0f1e30; font-family:var(--mono); font-size:12px; }
.log-ts   { color:var(--muted); margin-right:10px; }
.log-ok   { color:#00ff88; } 
.log-err  { color:#ff4444; } 
.log-warn { color:#ffaa00; } 
.log-info { color:#00d4ff; }

/* Titles */
.cyber-title {
  font-family: var(--mono);
  font-size: 22px;
  color: var(--accent);
  letter-spacing: 2px;
  text-shadow: 0 0 20px #00d4ff55;
}
.cyber-sub {
  font-size: 11px;
  color: var(--muted);
  letter-spacing: 1px;
  font-family: var(--mono);
}
.cyber-divider { border:none; border-top:1px solid var(--border); margin:1rem 0; }

/* Pulse animation dot */
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
.pulse {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--accent2);
  animation: pulse 1.5s infinite;
  margin-right: 6px;
}

.nim-banner {
  background: linear-gradient(135deg, #0a1f0a, #0a0f2a);
  border: 1px solid #00ff8844;
  border-radius: 10px;
  padding: .9rem 1.1rem;
  margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "logs": [], "scan_count": 0, "threat_count": 0,
    "last_output": "", "chat_history": [],
    "llm_provider": "nim"
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%H:%M:%S")

def add_log(msg, kind="info"):
    st.session_state.logs.append({"ts": ts(), "msg": msg, "kind": kind})

# ── NIM Chat function ─────────────────────────────────────────────────────────
def nim_chat(user_message: str, system_prompt: str = None) -> str:
    """Call NVIDIA NIM API directly for threat analysis."""
    nim_key = os.getenv("NIM_API_KEY")
    if not nim_key:
        return "❌ NIM_API_KEY not found! Please set it in environment variables."

    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=nim_key,
        )
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=messages,
            temperature=0.2,
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ NIM API Error: {str(e)}"

# ── Run NVISO agent scenario ──────────────────────────────────────────────────
def run_agent_scenario(scenario: str, project_path: str) -> tuple:
    venv_python = os.path.join(project_path, "venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = os.path.join(project_path, "venv", "bin", "python")
    run_script = os.path.join(project_path, "run_agents.py")
    try:
        result = subprocess.run(
            [venv_python, run_script, scenario],
            capture_output=True, text=True,
            cwd=project_path, timeout=120,
        )
        return result.stdout + result.stderr, result.returncode == 0
    except subprocess.TimeoutExpired:
        return "⏱️ Timeout — Agent took too long (>120s)", False
    except Exception as e:
        return f"Error: {str(e)}", False

def colorize_output(raw: str) -> str:
    lines, colored = raw.split("\n"), []
    for line in lines:
        l = line.replace("<", "&lt;").replace(">", "&gt;")
        if any(w in line for w in ["WARNING", "warn"]):
            colored.append(f'<span class="t-warn">{l}</span>')
        elif any(w in line for w in ["Error", "error", "Traceback"]):
            colored.append(f'<span class="t-error">{l}</span>')
        elif any(w in line for w in ["TERMINATED", "joke", "Why", "Because", "✅"]):
            colored.append(f'<span class="t-prompt">{l}</span>')
        elif any(w in line for w in ["[", "----", "****", "Starting"]):
            colored.append(f'<span class="t-info">{l}</span>')
        else:
            colored.append(l)
    return "<br>".join(colored)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="cyber-title">🛡️ CyberGuard</div>', unsafe_allow_html=True)
    st.markdown('<div class="cyber-sub">AI THREAT DETECTION AGENT</div>', unsafe_allow_html=True)
    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)

    # LLM Provider selector
    st.markdown("**🤖 LLM Provider**")
    provider = st.radio(
        "provider",
        ["NVIDIA NIM (Cloud ☁️)", "Ollama (Local 🦙)"],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state.llm_provider = "nim" if "NIM" in provider else "ollama"

    if st.session_state.llm_provider == "nim":
        nim_status = "✅ NIM API Ready" if os.getenv("NIM_API_KEY") else "⚠️ NIM_API_KEY not set"
        color = "#00ff88" if os.getenv("NIM_API_KEY") else "#ffaa00"
        st.markdown(
            f'<div style="font-size:11px;color:{color};font-family:var(--mono);margin:4px 0">'
            f'{nim_status}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<span class="badge badge-ok">llama-3.3-70b</span>'
            '<span class="badge badge-info">NIM</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="badge badge-ok">● OLLAMA</span>'
            '<span class="badge badge-info">llama3.2</span>',
            unsafe_allow_html=True
        )

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)

    # Project path (only needed for Ollama agent scenarios)
    if st.session_state.llm_provider == "ollama":
        st.markdown("**⚙️ Project Path**")
        project_path = st.text_input(
            "Path",
            value=r"C:\Users\Vamshi Krishna\Desktop\my-security-agent\cyber-security-llm-agents",
            label_visibility="collapsed",
        )
    else:
        project_path = r"C:\Users\Vamshi Krishna\Desktop\my-security-agent\cyber-security-llm-agents"

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)

    # Scenarios
    st.markdown("**📋 Select Scenario**")
    scenarios = {
        "HELLO_AGENTS":      ("👋", "Hello Agents",      "Basic connectivity test"),
        "THREAT_ANALYSIS":   ("🔍", "Threat Analysis",   "Analyze threat with NIM AI"),
        "LOG_INVESTIGATION": ("📄", "Log Investigation", "AI-powered log analysis"),
        "DETECT_EDR":        ("🛡️", "Detect EDR",        "Enumerate endpoint defenses"),
        "THREAT_HUNT":       ("🎯", "Threat Hunt",       "Active threat hunting"),
    }
    selected_scenario = st.selectbox(
        "Scenario",
        list(scenarios.keys()),
        format_func=lambda x: f"{scenarios[x][0]}  {scenarios[x][1]}",
        label_visibility="collapsed",
    )
    scn = scenarios[selected_scenario]
    st.markdown(
        f'<div style="font-size:11px;color:#4a6080;margin:4px 0 10px;font-family:var(--mono)">ℹ️ {scn[2]}</div>',
        unsafe_allow_html=True
    )

    sidebar_run = st.button(f"▶ RUN  {selected_scenario}", key="sidebar_run")

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)

    # Stats
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-box"><div class="stat-n" style="color:#00d4ff">{st.session_state.scan_count}</div><div class="stat-l">Scans</div></div>'
        f'<div class="stat-box"><div class="stat-n" style="color:#ff4444">{st.session_state.threat_count}</div><div class="stat-l">Threats</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if st.button("🗑️ Clear All", key="clear"):
        st.session_state.logs = []
        st.session_state.last_output = ""
        st.session_state.chat_history = []
        st.rerun()

# ── MAIN ─────────────────────────────────────────────────────────────────────
# Header
nim_badge = '<span class="badge badge-ok">⚡ NIM 70B</span>' if st.session_state.llm_provider == "nim" else '<span class="badge badge-warn">🦙 Ollama</span>'
st.markdown(f"""
<div class="cyber-card accent" style="margin-bottom:1rem">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
    <div>
      <span class="cyber-title" style="font-size:18px">🛡️ CYBERGUARD AI</span>
      <span style="font-size:11px;color:#4a6080;margin-left:12px;font-family:var(--mono)">
        NVISO Threat Detection — NVIDIA NIM + AutoGen
      </span>
    </div>
    <div>
      <span class="badge badge-live"><span class="pulse"></span>LIVE</span>
      {nim_badge}
      <span class="badge badge-ok">FREE</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["🎯 Run Scenario", "🔍 AI Threat Analyzer", "📋 Activity Log"])

# ── TAB 1 — Run Scenario ──────────────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.markdown("### 🎯 Scenario Control")
        st.markdown(f"""
        <div class="cyber-card warn">
          <div style="font-size:14px;font-weight:600;color:#ffaa00;margin-bottom:4px">{scn[0]} {scn[1]}</div>
          <div style="font-size:12px;color:#4a6080">{scn[2]}</div>
          <div style="font-size:11px;color:#2a4060;margin-top:6px;font-family:var(--mono)">
            CMD: python run_agents.py {selected_scenario}
          </div>
        </div>
        """, unsafe_allow_html=True)

        main_run = st.button(f"▶ EXECUTE  {selected_scenario}", key="main_run")

        if main_run or sidebar_run:
            st.session_state.scan_count += 1
            add_log(f"Starting: {selected_scenario}", "info")

            # NIM direct scenarios
            if st.session_state.llm_provider == "nim" and selected_scenario in ["THREAT_ANALYSIS", "LOG_INVESTIGATION"]:
                with st.spinner("⚡ NVIDIA NIM AI analyzing..."):
                    sys_prompt = (
                        "You are an expert cybersecurity analyst. "
                        "Analyze threats, explain findings clearly, and provide actionable recommendations. "
                        "Format your response with sections: THREAT ASSESSMENT, INDICATORS, RECOMMENDATIONS."
                    )
                    result = nim_chat(
                        f"Perform a {selected_scenario.replace('_',' ')} and explain what you find.",
                        sys_prompt
                    )
                    st.session_state.last_output = result
                    add_log(f"{selected_scenario} completed via NIM ✅", "ok")
            else:
                # Run NVISO autogen scenario
                with st.spinner(f"🤖 Agent running {selected_scenario}..."):
                    output, success = run_agent_scenario(selected_scenario, project_path)
                    st.session_state.last_output = output
                    if success or "TERMINATED" in output:
                        add_log(f"{selected_scenario} completed ✅", "ok")
                    else:
                        add_log(f"{selected_scenario} had issues", "warn")
                        st.session_state.threat_count += 1
            st.rerun()

    with col_right:
        st.markdown("### 📟 Agent Output")
        if st.session_state.last_output:
            raw = st.session_state.last_output
            # Check if NIM plain text or agent output
            if "THREAT ASSESSMENT" in raw or "INDICATORS" in raw or "RECOMMENDATIONS" in raw:
                # NIM formatted output styled inside terminal layout
                st.markdown(
                    f'<div class="terminal"><span class="t-prompt">{raw.replace(chr(10), "<br>")}</span></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="terminal">{colorize_output(raw)}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown("""
            <div class="terminal">
<span class="t-prompt">CyberGuard AI v2.0 — NVIDIA NIM Edition</span>
<span class="t-info">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
<span class="t-warn">Powered by : NVIDIA NIM llama-3.3-70b-instruct</span>
<span class="t-info">Framework  : Microsoft AutoGen multi-agent</span>
<span class="t-prompt">Status     : READY ✅</span>

<span class="t-info">Select a scenario → click EXECUTE</span>
<span class="t-warn">▌</span>
            </div>
            """, unsafe_allow_html=True)

# ── TAB 2 — AI Threat Analyzer ────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔍 AI-Powered Threat Analyzer")
    st.markdown(
        '<div class="nim-banner">'
        '<span style="font-size:12px;color:#00ff88;font-family:var(--mono)">⚡ Powered by NVIDIA NIM — llama-3.3-70b-instruct</span><br>'
        '<span style="font-size:11px;color:#4a6080">Paste any IP, domain, hash, log line or alert — AI will analyze it</span>'
        '</div>',
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([1, 1], gap="medium")

    with col_a:
        analysis_type = st.selectbox(
            "Analysis Type",
            ["🔍 General Threat Analysis",
             "📋 Log Line Analysis",
             "🌐 IP / Domain Investigation",
             "🦠 Malware Hash Analysis",
             "⚠️ Alert Triage",
             "📊 MITRE ATT&CK Mapping"],
        )
        target_input = st.text_area(
            "Input (IP / Domain / Hash / Log / Alert)",
            placeholder="Paste suspicious content here...\n\nExamples:\n• 192.168.1.100\n• suspicious-domain.xyz\n• Failed login attempts from multiple IPs\n• d41d8cd98f00b204e9800998ecf8427e",
            height=180,
        )
        analyze_btn = st.button("⚡ ANALYZE WITH NIM AI", key="nim_analyze")

    with col_b:
        st.markdown("**💬 AI Analysis Result**")
        if analyze_btn and target_input:
            st.session_state.scan_count += 1
            add_log(f"NIM Analysis: {analysis_type[:30]}...", "info")

            type_map = {
                "🔍 General Threat Analysis":   "Perform a comprehensive threat analysis on this input. Identify threat type, severity, IOCs, and recommended actions.",
                "📋 Log Line Analysis":          "Analyze this log entry for security threats. Identify anomalies, potential attacks, and MITRE ATT&CK techniques.",
                "🌐 IP / Domain Investigation":  "Investigate this IP/domain for malicious activity. Check for known threats, suspicious patterns, and risk level.",
                "🦠 Malware Hash Analysis":      "Analyze this file hash for malware indicators. Identify malware family, behavior, and remediation steps.",
                "⚠️ Alert Triage":               "Triage this security alert. Determine if it's a true positive or false positive, severity, and immediate actions.",
                "📊 MITRE ATT&CK Mapping":      "Map this activity to MITRE ATT&CK framework. Identify tactics, techniques, and sub-techniques.",
            }

            system_prompt = (
                "You are a senior SOC analyst and cybersecurity expert with 15+ years experience. "
                "Provide detailed, actionable security analysis. Use clear sections with headers. "
                "Always include: severity level (CRITICAL/HIGH/MEDIUM/LOW/INFO), confidence score, and specific recommendations."
            )
            user_msg = f"{type_map.get(analysis_type, 'Analyze this:')}\n\nInput:\n{target_input}"

            with st.spinner("⚡ NVIDIA NIM AI analyzing threat..."):
                result = nim_chat(user_msg, system_prompt)
                st.session_state.last_output = result

            if "❌" in result:
                add_log("NIM API error — check API key", "err")
                st.session_state.threat_count += 1
            else:
                add_log(f"Analysis complete ✅", "ok")

            st.markdown(
                f'<div class="terminal" style="max-height:360px">'
                f'<span class="t-prompt">{result.replace(chr(10), "<br>")}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        elif analyze_btn:
            st.warning("Please enter something to analyze!")
        else:
            st.markdown("""
            <div class="terminal" style="min-height:300px">
<span class="t-info">⚡ NVIDIA NIM AI Threat Analyzer</span>
<span class="t-info">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
<span class="t-warn">Paste any suspicious content on the left</span>
<span class="t-warn">and click ANALYZE to get AI-powered</span>
<span class="t-warn">security analysis...</span>

<span class="t-prompt">Model: meta/llama-3.3-70b-instruct</span>
<span class="t-info">Ready ▌</span>
            </div>
            """, unsafe_allow_html=True)

# ── TAB 3 — Activity Log ──────────────────────────────────────────────────────
with tab3:
    st.markdown("### 📋 Activity Log")
    if st.session_state.logs:
        log_html = ""
        for e in reversed(st.session_state.logs):
            kc   = {"ok":"log-ok","err":"log-err","warn":"log-warn","info":"log-info"}.get(e["kind"],"log-info")
            icon = {"ok":"✅","err":"❌","warn":"⚠️","info":"ℹ️"}.get(e["kind"],"ℹ️")
            log_html += (
                f'<div class="log-line">'
                f'<span class="log-ts">[{e["ts"]}]</span>'
                f'<span class="{kc}">{icon} {e["msg"]}</span>'
                f'</div>'
            )
        st.markdown(f'<div class="cyber-card" style="padding:.6rem .8rem">{log_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="cyber-card"><span style="color:#2a4060;font-size:12px;font-family:var(--mono)">No activity yet</span></div>',
            unsafe_allow_html=True
        )

# ── Status bar ────────────────────────────────────────────────────────────────
st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
provider_label = "NIM/llama-3.3-70b" if st.session_state.llm_provider == "nim" else "ollama/llama3.2"
st.markdown(f"""
<div style="display:flex;justify-content:space-between;font-size:11px;color:#2a4060;font-family:var(--mono);padding:4px 0">
  <span><span class="pulse"></span>CYBERGUARD AI v2.0</span>
  <span>LLM: {provider_label} | Cost: $0.00 | Scans: {st.session_state.scan_count}</span>
  <span>BUILD: v2.0-nim | {datetime.now().strftime("%Y-%m-%d")}</span>
</div>
""", unsafe_allow_html=True)