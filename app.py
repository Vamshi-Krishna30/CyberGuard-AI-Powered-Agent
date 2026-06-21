import streamlit as st
import subprocess
import os
import sys
import requests
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load .env file
load_dotenv()
# Detect if running on Hugging Face
IS_HF = os.getenv("SPACE_ID") is not None
# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght=300;400;500;600&display=swap');
:root {
  --bg:#0a0e1a; --panel:#0f1628; --border:#1e2d4a;
  --accent:#00d4ff; --accent2:#00ff88; --danger:#ff4444;
  --warn:#ffaa00; --muted:#4a6080; --text:#c8d8e8;
  --mono:'Share Tech Mono',monospace; --sans:'Inter',sans-serif;
}
html,body,[data-testid="stApp"]{background:var(--bg)!important;color:var(--text)!important;font-family:var(--sans)}
[data-testid="stSidebar"]{background:var(--panel)!important;border-right:1px solid var(--border)!important}
[data-testid="stSidebarUserContent"]{padding-top:1rem!important;width:280px!important}
[data-testid="stSidebar"] *{color:var(--text)}
[data-testid="stSidebar"] strong{color:var(--accent)!important;font-family:var(--mono)!important;letter-spacing:.5px}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="collapsedControl"]{background:#0f1628!important;border:1px solid #1e2d4a!important;border-radius:0 8px 8px 0!important;color:#00d4ff!important;top:10px!important}
[data-testid="collapsedControl"]:hover{background:#1a2a4a!important;box-shadow:0 0 10px #00d4ff44!important}
[data-testid="stActionButton"]{visibility:hidden!important}
#MainMenu,footer{visibility:hidden!important}
.stButton>button{background:linear-gradient(135deg,#003d66,#006699)!important;color:#00d4ff!important;border:1px solid #00d4ff!important;border-radius:6px!important;font-family:var(--mono)!important;font-size:13px!important;letter-spacing:1px!important;padding:10px 28px!important;transition:all .2s!important;width:100%}
.stButton>button:hover{background:linear-gradient(135deg,#005588,#0088cc)!important;box-shadow:0 0 16px #00d4ff55!important;color:#00ff88!important;border-color:#00ff88!important}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:#060d1a!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:6px!important;font-family:var(--mono);font-size:13px}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--accent)!important;box-shadow:0 0 8px #00d4ff33!important}
.stSelectbox div[data-baseweb="select"]>div{background:#060d1a!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:6px!important;font-family:var(--mono)!important;font-size:13px!important}
[data-testid="stRadio"] label{font-family:var(--mono)!important;color:var(--text)!important;font-size:13px!important}
.cyber-card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:1.2rem 1.4rem;margin-bottom:1rem}
.cyber-card.accent{border-left:3px solid var(--accent)}
.cyber-card.warn{border-left:3px solid var(--warn)}
.cyber-card.danger{border-left:3px solid var(--danger)}
.cyber-card.success{border-left:3px solid var(--accent2)}
.terminal{background:#020810;border:1px solid #1a2a3a;border-radius:8px;padding:1rem 1.2rem;font-family:var(--mono);font-size:12px;color:#00d4ff;min-height:200px;max-height:440px;overflow-y:auto;line-height:1.8;white-space:pre-wrap;word-break:break-word;box-shadow:inset 0 0 10px #000}
.t-prompt{color:#00ff88} .t-error{color:#ff4444} .t-warn{color:#ffaa00} .t-info{color:#88aaff}
.stat-row{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:1rem}
.stat-box{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:.7rem .9rem;text-align:center}
.stat-n{font-size:22px;font-weight:600;font-family:var(--mono)}
.stat-l{font-size:10px;color:var(--muted);margin-top:2px;letter-spacing:.05em;text-transform:uppercase}
.badge{display:inline-block;font-size:10px;font-family:var(--mono);padding:2px 8px;border-radius:3px;letter-spacing:.05em;margin-right:5px}
.badge-ok{background:#0a2a1a;color:#00ff88;border:1px solid #00ff8844}
.badge-live{background:#1a0a0a;color:#ff4444;border:1px solid #ff444444}
.badge-info{background:#0a1a2a;color:#00d4ff;border:1px solid #00d4ff44}
.badge-warn{background:#1a1000;color:#ffaa00;border:1px solid #ffaa0044}
.log-line{padding:4px 0;border-bottom:1px solid #0f1e30;font-family:var(--mono);font-size:12px}
.log-ts{color:var(--muted);margin-right:10px}
.log-ok{color:#00ff88} .log-err{color:#ff4444} .log-warn{color:#ffaa00} .log-info{color:#00d4ff}
.cyber-title{font-family:var(--mono);font-size:22px;color:var(--accent);letter-spacing:2px;text-shadow:0 0 20px #00d4ff55}
.cyber-sub{font-size:11px;color:var(--muted);letter-spacing:1px;font-family:var(--mono)}
.cyber-divider{border:none;border-top:1px solid var(--border);margin:1rem 0}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.pulse{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--accent2);animation:pulse 1.5s infinite;margin-right:6px}
.nim-banner{background:linear-gradient(135deg,#0a1f0a,#0a0f2a);border:1px solid #00ff8844;border-radius:10px;padding:.9rem 1.1rem;margin-bottom:1rem}
.vt-banner{background:linear-gradient(135deg,#1a0a0a,#0a0f2a);border:1px solid #ff444444;border-radius:10px;padding:.9rem 1.1rem;margin-bottom:1rem}
.vt-result-card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:1rem 1.2rem;margin-bottom:.8rem}
.vt-stat{display:inline-block;padding:4px 12px;border-radius:6px;font-family:var(--mono);font-size:13px;font-weight:600;margin-right:8px;margin-bottom:6px}
.vt-malicious{background:#2a0a0a;color:#ff4444;border:1px solid #ff444466}
.vt-clean{background:#0a2a1a;color:#00ff88;border:1px solid #00ff8866}
.vt-suspicious{background:#1a1000;color:#ffaa00;border:1px solid #ffaa0066}
.vt-undetected{background:#0a1a2a;color:#88aaff;border:1px solid #88aaff44}
.engine-row{display:flex;justify-content:space-between;padding:4px 8px;border-radius:4px;font-family:var(--mono);font-size:11px;margin-bottom:2px}
.engine-bad{background:#1a0505;color:#ff6666}
.engine-ok{background:#051a0a;color:#66ff99}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {
    "logs": [], "scan_count": 0, "threat_count": 0,
    "last_output": "", "chat_history": [],
    "llm_provider": "nim", "vt_result": None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def ts():
    return datetime.now().strftime("%H:%M:%S")

def add_log(msg, kind="info"):
    st.session_state.logs.append({"ts": ts(), "msg": msg, "kind": kind})

# ── NIM Chat ──────────────────────────────────────────────────────────────────
def nim_chat(user_message: str, system_prompt: str = None) -> str:
    nim_key = os.getenv("NIM_API_KEY")
    if not nim_key:
        return "❌ NIM_API_KEY not found!"
    try:
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=nim_key)
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

# ── VirusTotal Functions ───────────────────────────────────────────────────────
def vt_scan_ip(ip: str, api_key: str) -> dict:
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            return {"error": "IP not found in VirusTotal database"}
        elif r.status_code == 429:
            return {"error": "Rate limit exceeded — wait 1 minute (Free: 4 req/min)"}
        else:
            return {"error": f"API Error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def vt_scan_url(url_target: str, api_key: str) -> dict:
    import base64
    url_id = base64.urlsafe_b64encode(url_target.encode()).decode().strip("=")
    url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    headers = {"x-apikey": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            submit_url = "https://www.virustotal.com/api/v3/urls"
            payload = {"url": url_target}
            r2 = requests.post(submit_url, headers=headers, data=payload, timeout=15)
            if r2.status_code == 200:
                return {"info": "URL submitted for scanning. Try again in 30 seconds."}
            return {"error": "URL not found"}
        elif r.status_code == 429:
            return {"error": "Rate limit exceeded — wait 1 minute (Free: 4 req/min)"}
        else:
            return {"error": f"API Error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def vt_scan_hash(file_hash: str, api_key: str) -> dict:
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {"x-apikey": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            return {"error": "Hash not found in VirusTotal database"}
        elif r.status_code == 429:
            return {"error": "Rate limit exceeded — wait 1 minute (Free: 4 req/min)"}
        else:
            return {"error": f"API Error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def vt_scan_domain(domain: str, api_key: str) -> dict:
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": api_key}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            return {"error": "Domain not found in VirusTotal database"}
        elif r.status_code == 429:
            return {"error": "Rate limit exceeded — wait 1 minute (Free: 4 req/min)"}
        else:
            return {"error": f"API Error: {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def parse_vt_result(data: dict, scan_type: str) -> dict:
    if "error" in data: return {"error": data["error"]}
    if "info" in data: return {"info": data["info"]}

    attrs = data.get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {})

    malicious   = stats.get("malicious", 0)
    suspicious  = stats.get("suspicious", 0)
    undetected  = stats.get("undetected", 0)
    harmless    = stats.get("harmless", 0)
    total       = malicious + suspicious + undetected + harmless

    if malicious >= 10:
        risk, risk_color = "🔴 CRITICAL", "#ff4444"
    elif malicious >= 5:
        risk, risk_color = "🟠 HIGH", "#ff8844"
    elif malicious >= 2:
        risk, risk_color = "🟡 MEDIUM", "#ffaa00"
    elif malicious == 1 or suspicious >= 2:
        risk, risk_color = "🟡 LOW", "#ffdd00"
    else:
        risk, risk_color = "🟢 CLEAN", "#00ff88"

    engines = attrs.get("last_analysis_results", {})
    bad_engines = [
        {"engine": k, "result": v.get("result", "malicious")}
        for k, v in engines.items()
        if v.get("category") in ["malicious", "suspicious"]
    ][:10]

    result = {
        "risk": risk, "risk_color": risk_color,
        "malicious": malicious, "suspicious": suspicious,
        "undetected": undetected, "harmless": harmless,
        "total": total, "bad_engines": bad_engines, "scan_type": scan_type,
    }

    if scan_type == "IP":
        result["country"] = attrs.get("country", "Unknown")
        result["owner"]   = attrs.get("as_owner", "Unknown")
        result["asn"]     = attrs.get("asn", "Unknown")
        result["rep"]     = attrs.get("reputation", 0)
    elif scan_type == "Domain":
        result["rep"]       = attrs.get("reputation", 0)
        result["categories"] = list(attrs.get("categories", {}).values())[:3]
        result["registrar"] = attrs.get("registrar", "Unknown")
    elif scan_type == "Hash":
        result["name"]       = attrs.get("meaningful_name", "Unknown")
        result["file_type"]  = attrs.get("type_description", "Unknown")
        result["file_size"]  = attrs.get("size", 0)
        result["tags"]       = attrs.get("tags", [])[:5]

    return result

def display_vt_result(parsed: dict, target: str):
    if "error" in parsed:
        st.markdown(f'<div class="vt-result-card danger"><span style="color:#ff4444;font-family:var(--mono)">❌ {parsed["error"]}</span></div>', unsafe_allow_html=True)
        return
    if "info" in parsed:
        st.markdown(f'<div class="vt-result-card warn"><span style="color:#ffaa00;font-family:var(--mono)">ℹ️ {parsed["info"]}</span></div>', unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="vt-result-card">
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:12px">
        <div>
          <div style="font-family:var(--mono);font-size:14px;color:#c8d8e8;margin-bottom:4px">
            🔍 VirusTotal Scan — <span style="color:#00d4ff">{target}</span>
          </div>
          <div style="font-size:18px;font-weight:600;color:{parsed['risk_color']};font-family:var(--mono)">
            {parsed['risk']}
          </div>
        </div>
        <div style="text-align:right">
          <div style="font-size:11px;color:#4a6080;font-family:var(--mono)">Detection Rate</div>
          <div style="font-size:22px;font-weight:600;font-family:var(--mono);color:{parsed['risk_color']}">
            {parsed['malicious']}/{parsed['total']}
          </div>
        </div>
      </div>
      <div style="margin-bottom:12px">
        <span class="vt-stat vt-malicious">🔴 Malicious: {parsed['malicious']}</span>
        <span class="vt-stat vt-suspicious">🟡 Suspicious: {parsed['suspicious']}</span>
        <span class="vt-stat vt-clean">🟢 Clean: {parsed['harmless']}</span>
        <span class="vt-stat vt-undetected">⚪ Undetected: {parsed['undetected']}</span>
      </div>
    """, unsafe_allow_html=True)

    if parsed["scan_type"] == "IP":
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px">
          <div style="background:#060d1a;padding:8px;border-radius:6px;font-family:var(--mono);font-size:11px">
            <div style="color:#4a6080">Country</div>
            <div style="color:#c8d8e8">{parsed.get('country','Unknown')}</div>
          </div>
          <div style="background:#060d1a;padding:8px;border-radius:6px;font-family:var(--mono);font-size:11px">
            <div style="color:#4a6080">ASN Owner</div>
            <div style="color:#c8d8e8">{parsed.get('owner','Unknown')[:20]}</div>
          </div>
          <div style="background:#060d1a;padding:8px;border-radius:6px;font-family:var(--mono);font-size:11px">
            <div style="color:#4a6080">Reputation</div>
            <div style="color:{'#ff4444' if parsed.get('rep',0) < 0 else '#00ff88'}">{parsed.get('rep',0)}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    elif parsed["scan_type"] == "Hash":
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px">
          <div style="background:#060d1a;padding:8px;border-radius:6px;font-family:var(--mono);font-size:11px">
            <div style="color:#4a6080">File Name</div>
            <div style="color:#c8d8e8">{str(parsed.get('name','Unknown'))[:20]}</div>
          </div>
          <div style="background:#060d1a;padding:8px;border-radius:6px;font-family:var(--mono);font-size:11px">
            <div style="color:#4a6080">File Type</div>
            <div style="color:#c8d8e8">{parsed.get('file_type','Unknown')}</div>
          </div>
          <div style="background:#060d1a;padding:8px;border-radius:6px;font-family:var(--mono);font-size:11px">
            <div style="color:#4a6080">File Size</div>
            <div style="color:#c8d8e8">{parsed.get('file_size',0):,} bytes</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    if parsed["bad_engines"]:
        st.markdown('<div style="font-size:11px;color:#4a6080;font-family:var(--mono);margin-bottom:6px">🔴 Detected by engines:</div>', unsafe_allow_html=True)
        engines_html = "".join([f'<div class="engine-row engine-bad"><span>{eng["engine"]}</span><span>{eng["result"]}</span></div>' for eng in parsed["bad_engines"]])
        st.markdown(f'<div style="max-height:160px;overflow-y:auto">{engines_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#00ff88;font-family:var(--mono);font-size:12px">✅ No engines flagged this as malicious</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Run NVISO agent (AUTOMATIC CLOUD DETECTION UPDATE) ────────────────────────
def run_agent_scenario(scenario: str, project_path: str = None) -> tuple:
    # హగ్గింగ్ ఫేస్ క్లౌడ్ ఎన్విరాన్మెంట్‌లో కరెంట్ ఫోల్డర్ లొకేషన్‌ను ఆటోమేటిక్‌గా తీసుకుంటుంది
    current_dir = os.path.dirname(os.path.abspath(__file__)).strip()
    
    venv_python = os.path.join(current_dir, "venv", "bin", "python")
    if not os.path.exists(venv_python):
        venv_python = os.path.join(current_dir, "venv", "Scripts", "python.exe")
    
    # ఒకవేళ డోకర్ స్పేస్‌లో వర్చువల్ ఎన్విరాన్మెంట్ లేకపోతే బేస్ పైథాన్‌ను వాడుకుంటుంది
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    run_script = os.path.join(current_dir, "run_agents.py")
    
    # హగ్గింగ్ ఫేస్ సీక్రెట్ కీస్ (NIM_API_KEY) సబ్‌ప్రాసెస్‌కి అందేలా సిస్టమ్ ఎన్విరాన్మెంట్‌ను పంపుతున్నాం
    current_env = os.environ.copy()
    
    try:
        result = subprocess.run(
            [venv_python, run_script, scenario],
            capture_output=True, text=True, cwd=os.getcwd().strip(), timeout=120,
            env=current_env
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

    st.markdown("**🤖 LLM Provider**")
    provider = st.radio("provider", ["NVIDIA NIM (Cloud ☁️)", "Ollama (Local 🦙)"], index=0, label_visibility="collapsed")
    st.session_state.llm_provider = "nim" if "NIM" in provider else "ollama"

    if st.session_state.llm_provider == "nim":
        nim_ok = bool(os.getenv("NIM_API_KEY"))
        st.markdown(
            f'<div style="font-size:11px;color:{"#00ff88" if nim_ok else "#ffaa00"};font-family:var(--mono);margin:4px 0">'
            f'{"✅ NIM API Ready" if nim_ok else "⚠️ NIM_API_KEY not set"}</div>',
            unsafe_allow_html=True
        )
        st.markdown('<span class="badge badge-ok">llama-3.3-70b</span><span class="badge badge-info">NIM</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-ok">● OLLAMA</span><span class="badge badge-info">llama3.2</span>', unsafe_allow_html=True)

    vt_ok = bool(os.getenv("VT_API_KEY"))
    st.markdown(
        f'<div style="font-size:11px;color:{"#00ff88" if vt_ok else "#ffaa00"};font-family:var(--mono);margin:4px 0">'
        f'{"✅ VirusTotal Ready" if vt_ok else "⚠️ VT_API_KEY not set"}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)

    # లోకల్ పాత్‌లతో పనిలేకుండా క్లౌడ్ ఆటో-డిటెక్షన్ కోసం అప్‌డేట్
    if st.session_state.llm_provider == "ollama":
        st.markdown("**⚙️ Project Path**")
        project_path = st.text_input("Path", value=os.getcwd(), label_visibility="collapsed").strip()
    else:
        project_path = os.getcwd().strip()

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
    st.markdown("**📋 Select Scenario**")
    scenarios = {
        "HELLO_AGENTS":     ("👋", "Hello Agents",      "Basic connectivity test"),
        "THREAT_ANALYSIS":  ("🔍", "Threat Analysis",   "Analyze threat with NIM AI"),
        "LOG_INVESTIGATION": ("📄", "Log Investigation", "AI-powered log analysis"),
        "DETECT_EDR":        ("🛡️", "Detect EDR",        "Enumerate endpoint defenses"),
        "THREAT_HUNT":       ("🎯", "Threat Hunt",       "Active threat hunting"),
    }
    selected_scenario = st.selectbox("Scenario", list(scenarios.keys()),
        format_func=lambda x: f"{scenarios[x][0]}  {scenarios[x][1]}", label_visibility="collapsed")
    scn = scenarios[selected_scenario]
    st.markdown(f'<div style="font-size:11px;color:#4a6080;margin:4px 0 10px;font-family:var(--mono)">ℹ️ {scn[2]}</div>', unsafe_allow_html=True)
    sidebar_run = st.button(f"▶ RUN  {selected_scenario}", key="sidebar_run")

    st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-box"><div class="stat-n" style="color:#00d4ff">{st.session_state.scan_count}</div><div class="stat-l">Scans</div></div>'
        f'<div class="stat-box"><div class="stat-n" style="color:#ff4444">{st.session_state.threat_count}</div><div class="stat-l">Threats</div></div>'
        f'</div>', unsafe_allow_html=True
    )
    if st.button("🗑️ Clear All", key="clear"):
        st.session_state.logs = []
        st.session_state.last_output = ""
        st.session_state.vt_result = None
        st.rerun()

# ── MAIN ─────────────────────────────────────────────────────────────────────
nim_badge = '<span class="badge badge-ok">⚡ NIM 70B</span>' if st.session_state.llm_provider == "nim" else '<span class="badge badge-warn">🦙 Ollama</span>'
vt_badge  = '<span class="badge badge-ok">🦠 VT</span>' if vt_ok else '<span class="badge badge-warn">🦠 VT</span>'

st.markdown(f"""
<div class="cyber-card accent" style="margin-bottom:1rem">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
    <div>
      <span class="cyber-title" style="font-size:18px">🛡️ CYBERGUARD AI</span>
      <span style="font-size:11px;color:#4a6080;margin-left:12px;font-family:var(--mono)">NVISO Threat Detection — NVIDIA NIM + VirusTotal</span>
    </div>
    <div>
      <span class="badge badge-live"><span class="pulse"></span>LIVE</span>
      {nim_badge}{vt_badge}
      <span class="badge badge-ok">FREE</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Run Scenario", "🔍 AI Threat Analyzer", "🦠 VirusTotal Scanner", "📋 Activity Log"])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([1, 1], gap="medium")
    with col_left:
        st.markdown("### 🎯 Scenario Control")
        st.markdown(f"""
        <div class="cyber-card warn">
          <div style="font-size:14px;font-weight:600;color:#ffaa00;margin-bottom:4px">{scn[0]} {scn[1]}</div>
          <div style="font-size:12px;color:#4a6080">{scn[2]}</div>
          <div style="font-size:11px;color:#2a4060;margin-top:6px;font-family:var(--mono)">CMD: python run_agents.py {selected_scenario}</div>
        </div>""", unsafe_allow_html=True)
        main_run = st.button(f"▶ EXECUTE  {selected_scenario}", key="main_run")
        if main_run or sidebar_run:
    st.session_state.scan_count += 1
    add_log(f"Starting: {selected_scenario}", "info")

    if IS_HF:
        # HF Cloud — NIM only
        with st.spinner("⚡ NVIDIA NIM AI analyzing..."):
            result = nim_chat(
                f"You are a cybersecurity agent. Perform this security task: {selected_scenario.replace('_',' ')}. Provide detailed analysis.",
                "You are an expert cybersecurity analyst and SOC agent. Perform the requested security task thoroughly."
            )
            st.session_state.last_output = result
            add_log(f"{selected_scenario} completed via NIM ✅", "ok")
    elif st.session_state.llm_provider == "nim" and selected_scenario in ["THREAT_ANALYSIS", "LOG_INVESTIGATION"]:
        # Local NIM scenarios
        with st.spinner("⚡ NVIDIA NIM AI analyzing..."):
            result = nim_chat(
                f"Perform a {selected_scenario.replace('_',' ')} and explain what you find.",
                "You are an expert cybersecurity analyst. Format: THREAT ASSESSMENT, INDICATORS, RECOMMENDATIONS."
            )
            st.session_state.last_output = result
            add_log(f"{selected_scenario} completed via NIM ✅", "ok")
    else:
        # Local Ollama
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
            if any(w in raw for w in ["THREAT ASSESSMENT", "INDICATORS", "RECOMMENDATIONS"]):
                st.markdown(f'<div class="terminal"><span class="t-prompt">{raw.replace(chr(10), "<br>")}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="terminal">{colorize_output(raw)}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""<div class="terminal">
<span class="t-prompt">CyberGuard AI v2.0 — NVIDIA NIM Edition</span>
<span class="t-info">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
<span class="t-warn">Powered by : NVIDIA NIM llama-3.3-70b-instruct</span>
<span class="t-info">Framework  : Microsoft AutoGen multi-agent</span>
<span class="t-prompt">Status     : READY ✅</span>
<span class="t-info">Select a scenario → click EXECUTE</span>
<span class="t-warn">▌</span></div>""", unsafe_allow_html=True)

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔍 AI-Powered Threat Analyzer")
    st.markdown('<div class="nim-banner"><span style="font-size:12px;color:#00ff88;font-family:var(--mono)">⚡ Powered by NVIDIA NIM — llama-3.3-70b-instruct</span><br><span style="font-size:11px;color:#4a6080">Paste any IP, domain, hash, log line or alert — AI will analyze it</span></div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1], gap="medium")
    with col_a:
        analysis_type = st.selectbox("Analysis Type", [
            "🔍 General Threat Analysis", "📋 Log Line Analysis",
            "🌐 IP / Domain Investigation", "🦠 Malware Hash Analysis",
            "⚠️ Alert Triage", "📊 MITRE ATT&CK Mapping"])
        target_input = st.text_area("Input", placeholder="Paste suspicious content here...", height=180)
        analyze_btn = st.button("⚡ ANALYZE WITH NIM AI", key="nim_analyze")
    with col_b:
        st.markdown("**💬 AI Analysis Result**")
        if analyze_btn and target_input:
            st.session_state.scan_count += 1
            add_log(f"NIM Analysis: {analysis_type[:30]}...", "info")
            type_map = {
                "🔍 General Threat Analysis":  "Perform a comprehensive threat analysis. Identify threat type, severity, IOCs, and recommended actions.",
                "📋 Log Line Analysis":         "Analyze this log entry for security threats. Identify anomalies and MITRE ATT&CK techniques.",
                "🌐 IP / Domain Investigation": "Investigate this IP/domain for malicious activity. Check for known threats and risk level.",
                "🦠 Malware Hash Analysis":     "Analyze this file hash for malware indicators. Identify malware family and remediation steps.",
                "⚠️ Alert Triage":              "Triage this security alert. Determine true/false positive, severity, and immediate actions.",
                "📊 MITRE ATT&CK Mapping":     "Map this activity to MITRE ATT&CK framework. Identify tactics, techniques, sub-techniques.",
            }
            sys_prompt = "You are a senior SOC analyst with 15+ years experience. Provide detailed, actionable security analysis with clear sections. Always include: severity (CRITICAL/HIGH/MEDIUM/LOW/INFO), confidence score, and recommendations."
            with st.spinner("⚡ NVIDIA NIM AI analyzing threat..."):
                result = nim_chat(f"{type_map.get(analysis_type,'Analyze this:')}\n\nInput:\n{target_input}", sys_prompt)
                st.session_state.last_output = result
            if "❌" in result:
                add_log("NIM API error", "err")
            else:
                add_log("Analysis complete ✅", "ok")
            st.markdown(f'<div class="terminal" style="max-height:360px"><span class="t-prompt">{result.replace(chr(10),"<br>")}</span></div>', unsafe_allow_html=True)
        elif analyze_btn:
            st.warning("Please enter something to analyze!")
        else:
            st.markdown("""<div class="terminal" style="min-height:300px">
<span class="t-info">⚡ NVIDIA NIM AI Threat Analyzer</span>
<span class="t-info">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
<span class="t-warn">Paste suspicious content on the left</span>
<span class="t-warn">and click ANALYZE for AI-powered analysis</span>
<span class="t-prompt">Model: meta/llama-3.3-70b-instruct</span>
<span class="t-info">Ready ▌</span></div>""", unsafe_allow_html=True)

# ── TAB 3 — VirusTotal Scanner ────────────────────────────────────────────────
with tab3:
    st.markdown("### 🦠 VirusTotal Scanner")
    st.markdown("""
    <div class="vt-banner">
      <span style="font-size:12px;color:#ff6666;font-family:var(--mono)">🦠 Powered by VirusTotal — 70+ AV Engines</span><br>
      <span style="font-size:11px;color:#4a6080">Real-time threat intelligence — IP, URL, Domain, File Hash scanning</span>
    </div>
    """, unsafe_allow_html=True)

    vt_key = os.getenv("VT_API_KEY")

    if not vt_key:
        st.warning("⚠️ VT_API_KEY not set! Add it to your .env file or HF Secrets.")
    else:
        col_vt1, col_vt2 = st.columns([1, 1], gap="medium")

        with col_vt1:
            st.markdown("**🎯 Scan Target**")
            scan_type = st.selectbox("Scan Type", [
                "🌐 IP Address", "🔗 URL", "🏠 Domain", "🦠 File Hash (MD5/SHA1/SHA256)",
            ], key="vt_scan_type")

            type_map_vt = {"🌐 IP Address": "IP", "🔗 URL": "URL", "🏠 Domain": "Domain", "🦠 File Hash (MD5/SHA1/SHA256)": "Hash"}
            placeholders = {
                "🌐 IP Address": "e.g. 8.8.8.8 or 1.2.3.4",
                "🔗 URL": "e.g. https://suspicious-site.com/malware",
                "🏠 Domain": "e.g. suspicious-domain.xyz",
                "🦠 File Hash (MD5/SHA1/SHA256)": "e.g. d41d8cd98f00b204e9800998ecf8427e",
            }

            vt_target = st.text_input("Enter target to scan", placeholder=placeholders.get(scan_type, "Enter value"), key="vt_target_input")
            vt_scan_btn = st.button("🔍 SCAN ON VIRUSTOTAL", key="vt_scan")
            vt_nim_btn = st.button("⚡ VT + NIM COMBINED ANALYSIS", key="vt_nim_btn")

            st.markdown("""
            <div style="margin-top:1rem;background:#060d1a;border-radius:8px;padding:10px 12px">
              <div style="font-size:11px;color:#4a6080;font-family:var(--mono);margin-bottom:6px">ℹ️ Free tier limits:</div>
              <div style="font-size:11px;color:#88aaff;font-family:var(--mono)">• 4 requests/minute</div>
              <div style="font-size:11px;color:#88aaff;font-family:var(--mono)">• 500 requests/day</div>
              <div style="font-size:11px;color:#88aaff;font-family:var(--mono)">• IP, URL, Domain, Hash ✅</div>
            </div>
            """, unsafe_allow_html=True)

        with col_vt2:
            st.markdown("**📊 Scan Results**")
            current_type = type_map_vt.get(scan_type, "IP")

            if vt_scan_btn and vt_target:
                st.session_state.scan_count += 1
                add_log(f"VT Scan: {current_type} — {vt_target}", "info")

                with st.spinner(f"🦠 Scanning {vt_target} on VirusTotal..."):
                    if current_type == "IP": raw = vt_scan_ip(vt_target.strip(), vt_key)
                    elif current_type == "URL": raw = vt_scan_url(vt_target.strip(), vt_key)
                    elif current_type == "Domain": raw = vt_scan_domain(vt_target.strip(), vt_key)
                    else: raw = vt_scan_hash(vt_target.strip(), vt_key)

                    parsed = parse_vt_result(raw, current_type)
                    st.session_state.vt_result = {"parsed": parsed, "target": vt_target, "type": current_type}

                    if "error" not in parsed and parsed.get("malicious", 0) > 0:
                        st.session_state.threat_count += 1
                        add_log(f"THREAT DETECTED: {vt_target} — {parsed['malicious']} engines flagged! 🔴", "err")
                    elif "error" not in parsed:
                        add_log(f"VT Scan complete: {vt_target} — {parsed.get('risk','Unknown')} ✅", "ok")
                    else:
                        add_log(f"VT Scan error: {parsed.get('error','Unknown')}", "warn")
                st.rerun()

            elif vt_nim_btn and vt_target:
                st.session_state.scan_count += 1
                add_log(f"VT+NIM Combined: {current_type} — {vt_target}", "info")

                with st.spinner(f"🦠 Scanning + 🤖 AI Analyzing..."):
                    if current_type == "IP": raw = vt_scan_ip(vt_target.strip(), vt_key)
                    elif current_type == "URL": raw = vt_scan_url(vt_target.strip(), vt_key)
                    elif current_type == "Domain": raw = vt_scan_domain(vt_target.strip(), vt_key)
                    else: raw = vt_scan_hash(vt_target.strip(), vt_key)

                    parsed = parse_vt_result(raw, current_type)
                    st.session_state.vt_result = {"parsed": parsed, "target": vt_target, "type": current_type}

                    vt_context = f"VirusTotal scan results for {current_type}: {vt_target}\n- Risk Level: {parsed.get('risk','Unknown')}\n- Malicious detections: {parsed.get('malicious',0)}/{parsed.get('total',0)} engines\n- Suspicious: {parsed.get('suspicious',0)}"
                    nim_result = nim_chat(f"Based on these VirusTotal results, provide a detailed threat analysis:\n{vt_context}\nProvide: threat assessment, attack patterns, risk to organization, and remediation steps.", "You are a senior SOC analyst.")
                    st.session_state.last_output = nim_result

                    if parsed.get("malicious", 0) > 0:
                        st.session_state.threat_count += 1
                        add_log(f"THREAT: {vt_target} flagged by {parsed['malicious']} engines 🔴", "err")
                    add_log("VT+NIM Combined analysis complete ✅", "ok")
                st.rerun()

            elif (vt_scan_btn or vt_nim_btn) and not vt_target:
                st.warning("Please enter a target to scan!")

            if st.session_state.vt_result:
                r = st.session_state.vt_result
                display_vt_result(r["parsed"], r["target"])
                if st.session_state.last_output and vt_nim_btn:
                    st.markdown("**🤖 NIM AI Analysis:**")
                    st.markdown(f'<div class="terminal" style="min-height:150px;max-height:250px"><span class="t-prompt">{st.session_state.last_output.replace(chr(10),"<br>")}</span></div>', unsafe_allow_html=True)
            else:
                st.markdown("""<div class="terminal" style="min-height:300px">
<span class="t-info">🦠 VirusTotal Scanner Ready</span>
<span class="t-info">━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</span>
<span class="t-warn">Enter an IP, URL, Domain or Hash on the left and click SCAN</span>
<span class="t-info">70+ AV engines will check your target in real-time for threats...</span>
<span class="t-prompt">Ready ▌</span></div>""", unsafe_allow_html=True)

# ── TAB 4 — Activity Log ──────────────────────────────────────────────────────
with tab4:
    st.markdown("### 📋 Activity Log")
    if st.session_state.logs:
        log_html = ""
        for e in reversed(st.session_state.logs):
            kc   = {"ok":"log-ok","err":"log-err","warn":"log-warn","info":"log-info"}.get(e["kind"],"log-info")
            icon = {"ok":"✅","err":"❌","warn":"⚠️","info":"ℹ️"}.get(e["kind"],"ℹ️")
            log_html += f'<div class="log-line"><span class="log-ts">[{e["ts"]}]</span><span class="{kc}">{icon} {e["msg"]}</span></div>'
        st.markdown(f'<div class="cyber-card" style="padding:.6rem .8rem">{log_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="cyber-card"><span style="color:#2a4060;font-size:12px;font-family:var(--mono)">No activity yet</span></div>', unsafe_allow_html=True)

# ── Status bar ────────────────────────────────────────────────────────────────
st.markdown('<hr class="cyber-divider">', unsafe_allow_html=True)
provider_label = "NIM/llama-3.3-70b" if st.session_state.llm_provider == "nim" else "ollama/llama3.2"
st.markdown(f"""
<div style="display:flex;justify-content:space-between;font-size:11px;color:#2a4060;font-family:var(--mono);padding:4px 0">
  <span><span class="pulse"></span>CYBERGUARD AI v2.0</span>
  <span>LLM: {provider_label} | VT: {"✅" if vt_ok else "❌"} | Cost: $0.00 | Scans: {st.session_state.scan_count}</span>
  <span>BUILD: v2.0-vt | {datetime.now().strftime("%Y-%m-%d")}</span>
</div>
""", unsafe_allow_html=True)
