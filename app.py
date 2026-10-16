
"""
ACCESSGUARD NEXUS — Hackathon Edition
Python + Streamlit + JSON + optional Gemini AI
"""

import json
import os
import re
import hashlib
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st

try:
    from google import genai
except Exception:
    genai = None

APP_NAME = "ACCESSGUARD NEXUS"
ORG_NAME = "PYTHONGURUKOOL"
DATA_FILE = Path("accessguard_nexus_data.json")
TOOLS = [
    "GITHUB", "AWS", "SLACK", "JIRA", "HR PORTAL", "FIGMA",
    "PRODUCTION SERVER", "DOCKER"
]
ROLES = ["Intern", "Developer", "Tester", "Manager", "Admin"]
ROLE_PERMISSIONS = {
    "Intern": ["SLACK", "JIRA"],
    "Developer": ["GITHUB", "SLACK", "JIRA", "AWS"],
    "Tester": ["SLACK", "JIRA", "GITHUB", "DOCKER"],
    "Manager": ["GITHUB", "AWS", "SLACK", "JIRA", "HR PORTAL"],
    "Admin": TOOLS.copy(),
}
SENSITIVE_TOOLS = {"AWS", "PRODUCTION SERVER", "HR PORTAL"}
PRIVILEGED_ROLES = {"Admin", "Manager"}


def now_stamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def seed_data():
    return {
        "employees": {
            "E101": {"name": "Aarav Sharma", "role": "Manager",
                     "access": ["GITHUB", "AWS", "SLACK", "JIRA"],
                     "email": "aaravsharma@pythongurukool.com",
                     "experience": 6, "phone": "", "created_at": "2026-08-15"},
            "E102": {"name": "Sneha Patil", "role": "Intern",
                     "access": ["SLACK", "JIRA"],
                     "email": "snehapatil@pythongurukool.com",
                     "experience": 0, "phone": "", "created_at": "2026-08-15"},
            "E103": {"name": "Kabir Desai", "role": "Developer",
                     "access": ["GITHUB", "SLACK", "JIRA", "AWS"],
                     "email": "kabirdesai@pythongurukool.com",
                     "experience": 2, "phone": "", "created_at": "2026-09-02"},
        },
        "logs": [
            {"id": "E101", "tool": "GITHUB", "status": "Granted",
             "date": "2026-08-15", "detail": "Initial access assigned", "risk": 5},
            {"id": "E102", "tool": "AWS", "status": "Denied",
             "date": "2026-08-15", "detail": "Intern role lacks AWS permission", "risk": 45},
            {"id": "E103", "tool": "AWS", "status": "Granted",
             "date": "2026-09-02", "detail": "Developer role permission", "risk": 10},
        ],
        "requests": [],
        "settings": {"company": ORG_NAME},
    }


def save_data(data):
    temp = DATA_FILE.with_suffix(".tmp")
    temp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    temp.replace(DATA_FILE)


def load_data():
    if DATA_FILE.exists():
        try:
            d = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            for key, default in seed_data().items():
                d.setdefault(key, default)
            return d
        except (OSError, json.JSONDecodeError):
            pass
    d = seed_data()
    save_data(d)
    return d


if "nexus_data" not in st.session_state:
    st.session_state.nexus_data = load_data()
if "nexus_notice" not in st.session_state:
    st.session_state.nexus_notice = None

data = st.session_state.nexus_data
employees, logs, requests = data["employees"], data["logs"], data["requests"]


def audit(emp_id, tool, status, detail="", risk=0):
    logs.append({
        "id": emp_id, "tool": tool, "status": status, "date": now_stamp(),
        "detail": detail, "risk": int(risk)
    })
    # Bound demo file growth while keeping a useful recent history.
    data["logs"] = logs[-3000:]
    save_data(data)


def risk_score(emp_id, tool, action="request"):
    """Transparent demo heuristic; not a validated security risk model."""
    score, reasons = 5, []
    employee = employees.get(emp_id)
    if not employee:
        return 100, ["Unknown employee identity"]
    role = employee.get("role", "Intern")
    if tool in SENSITIVE_TOOLS:
        score += 25
        reasons.append("Sensitive system requested")
    if role == "Intern" and tool in {"AWS", "PRODUCTION SERVER", "HR PORTAL"}:
        score += 35
        reasons.append("High privilege mismatch for Intern role")
    if tool not in ROLE_PERMISSIONS.get(role, []):
        score += 30
        reasons.append("Tool is outside role policy")
    recent_denials = sum(
        1 for item in logs[-30:]
        if item.get("id") == emp_id and item.get("status") == "Denied"
    )
    if recent_denials:
        score += min(20, recent_denials * 5)
        reasons.append(f"{recent_denials} recent denial event(s)")
    if action == "revoke":
        score = max(0, score - 10)
        reasons.append("Revocation is a risk-reducing action")
    return min(score, 100), reasons or ["Standard role-based request"]


def create_request(emp_id, tool, justification):
    score, reasons = risk_score(emp_id, tool)
    allowed_by_role = tool in ROLE_PERMISSIONS[employees[emp_id]["role"]]
    already = tool in employees[emp_id]["access"]
    if already:
        status = "Already Assigned"
    elif not allowed_by_role or score >= 60:
        status = "Denied"
    elif score >= 30 or tool in SENSITIVE_TOOLS:
        status = "Pending Approval"
    else:
        status = "Approved"
    req = {
        "request_id": f"REQ-{datetime.now().strftime('%y%m%d%H%M%S')}-{len(requests)+1:03d}",
        "employee_id": emp_id, "tool": tool, "justification": justification.strip(),
        "status": status, "risk": score, "risk_reasons": reasons,
        "created_at": now_stamp(), "reviewed_by": "", "reviewed_at": ""
    }
    requests.append(req)
    if status == "Approved":
        employees[emp_id]["access"].append(tool)
        audit(emp_id, tool, "Granted", f"Auto-approved request {req['request_id']}", score)
    elif status == "Denied":
        audit(emp_id, tool, "Denied", f"Request {req['request_id']}: role/risk policy", score)
    else:
        audit(emp_id, tool, "Pending", f"Approval required for {req['request_id']}", score)
    save_data(data)
    return req


def get_secret_key():
    key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        try:
            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            key = ""
    return key


def ai_copilot(question, context):
    key = get_secret_key()
    if not key or genai is None:
        return None
    try:
        client = genai.Client(api_key=key)
        prompt = f"""You are AccessGuard Nexus, a cautious IAM security copilot for a hackathon demo.
Use only the supplied application context. Do not claim to have performed actions.
Identify risks, explain role-based access, and give practical recommendations.
Never reveal secrets or invent audit events.
Context: {json.dumps(context, ensure_ascii=False)}
Question: {question}
Respond with concise headings: Assessment, Evidence, Recommended next step."""
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            contents=prompt,
        )
        return getattr(response, "text", None) or "The AI service returned an empty response."
    except Exception as exc:
        return f"AI connection error: {type(exc).__name__}. Check your API key, SDK, and model name."


st.set_page_config(
    page_title="AccessGuard Nexus | IAM Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--bg:#070c16;--cyan:#5be7ff;--violet:#9a86ff;--green:#65f4b6;--red:#ff718d;--muted:#91a7c7;--line:rgba(144,180,225,.18)}
html,body,[class*="css"]{font-family:'Manrope',sans-serif}
.stApp{background:radial-gradient(ellipse at 10% 0%,rgba(34,103,181,.22),transparent 35%),radial-gradient(ellipse at 95% 12%,rgba(119,68,215,.18),transparent 30%),var(--bg);color:#eef4ff}
.block-container{max-width:1550px;padding-top:1.1rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0d1729,#080d17);border-right:1px solid var(--line)}
[data-testid="stSidebar"] *{color:#eaf2ff}
.hero{position:relative;overflow:hidden;padding:30px 32px;border-radius:24px;background:linear-gradient(125deg,rgba(23,47,79,.97),rgba(27,21,61,.97));border:1px solid rgba(91,231,255,.32);box-shadow:0 25px 65px rgba(0,0,0,.4),inset 0 1px rgba(255,255,255,.12);transform:perspective(1100px) rotateX(1deg)}
.hero:after{content:"";position:absolute;width:270px;height:270px;right:5%;top:-125px;border-radius:50%;border:1px solid rgba(91,231,255,.4);box-shadow:0 0 0 24px rgba(91,231,255,.035),0 0 0 55px rgba(154,134,255,.04),0 0 75px rgba(91,231,255,.15)}
.eyebrow{font:500 11px 'DM Mono',monospace;color:var(--cyan);letter-spacing:2.4px}
.hero h1{font-size:clamp(28px,4vw,49px);line-height:1.05;margin:10px 0;color:white;font-weight:800}
.hero p{color:#b7c8e3;max-width:760px;font-size:14px}
.chip{display:inline-block;padding:6px 10px;margin:8px 6px 0 0;border:1px solid rgba(91,231,255,.24);border-radius:100px;background:rgba(91,231,255,.07);color:#b5f3ff;font:10px 'DM Mono',monospace}
.metric{padding:17px 18px;border-radius:18px;background:linear-gradient(145deg,rgba(26,42,67,.96),rgba(12,20,36,.98));border:1px solid var(--line);box-shadow:8px 10px 22px rgba(0,0,0,.24),inset 0 1px rgba(255,255,255,.06);min-height:118px;transition:transform .2s,border-color .2s}
.metric:hover{transform:translateY(-5px) perspective(700px) rotateX(2deg);border-color:rgba(91,231,255,.55)}
.metric-label{color:#9db2d0;font-size:10px;letter-spacing:1.5px;text-transform:uppercase}
.metric-value{font-size:30px;font-weight:800;color:#f5f8ff;margin-top:8px}
.metric-foot{font-size:11px;color:#7790b1;margin-top:2px}
.panel{border:1px solid var(--line);border-radius:18px;padding:18px;background:linear-gradient(145deg,rgba(19,31,51,.94),rgba(11,18,32,.96));box-shadow:0 15px 35px rgba(0,0,0,.18)}
.section-title{font-size:20px;font-weight:800;margin:22px 0 12px}
.small-muted{font-size:12px;color:#8da3c2}
.status{display:inline-block;padding:4px 9px;border-radius:99px;font-size:10px;font-weight:800}
.ok{color:#74ffc0;background:rgba(66,238,158,.1);border:1px solid rgba(66,238,158,.2)}
.warn{color:#ffd37a;background:rgba(255,196,78,.1);border:1px solid rgba(255,196,78,.2)}
.bad{color:#ff91a5;background:rgba(255,91,124,.1);border:1px solid rgba(255,91,124,.2)}
.stButton>button{border-radius:11px;border:1px solid rgba(91,231,255,.3);background:linear-gradient(135deg,#205d79,#5142a1);color:white;font-weight:700;box-shadow:0 7px 18px rgba(26,100,145,.2);transition:all .18s}
.stButton>button:hover{transform:translateY(-2px);border-color:#7cecff;color:white}
.stTextInput input,.stNumberInput input,.stTextArea textarea{background:#0b1423!important;color:#eef5ff!important;border-color:#293c59!important}
.stSelectbox div[data-baseweb="select"]{background:#0b1423!important}
div[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:14px;overflow:hidden}
hr{border-color:var(--line)}

/* NEXUS 3D UPGRADE: layered depth, animated holographic grid and glass surfaces */
.stApp{background-image:radial-gradient(ellipse at 10% 0%,rgba(34,103,181,.22),transparent 35%),radial-gradient(ellipse at 95% 12%,rgba(119,68,215,.18),transparent 30%),linear-gradient(rgba(91,231,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(91,231,255,.035) 1px,transparent 1px);background-size:auto,auto,42px 42px,42px 42px;background-position:center,center,center,center;background-color:var(--bg);background-attachment:fixed}
.block-container{perspective:1600px}
.hero{isolation:isolate;transform-style:preserve-3d;animation:heroRise .9s cubic-bezier(.2,.8,.2,1) both}
.hero:before{content:"";position:absolute;z-index:-1;right:7%;top:8%;width:190px;height:190px;border-radius:50%;border:1px solid rgba(91,231,255,.5);box-shadow:inset 0 0 30px rgba(91,231,255,.12),0 0 35px rgba(91,231,255,.15);background:radial-gradient(circle at 35% 30%,rgba(91,231,255,.22),rgba(154,134,255,.07) 42%,transparent 68%);animation:orbFloat 7s ease-in-out infinite;transform:translateZ(35px)}
.hero:after{z-index:-1;animation:ringPulse 5s ease-in-out infinite}
.hero h1,.hero p,.hero .chip,.hero .eyebrow{position:relative;z-index:1;transform:translateZ(18px)}
.metric{transform-style:preserve-3d;position:relative;overflow:hidden;backdrop-filter:blur(12px);transition:transform .28s ease,box-shadow .28s ease,border-color .28s ease}
.metric:before{content:"";position:absolute;left:-35%;top:-80%;width:65%;height:260%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.08),transparent);transform:rotate(28deg);transition:left .65s ease;pointer-events:none}
.metric:hover{transform:translateY(-7px) perspective(800px) rotateX(5deg) rotateY(-3deg) scale(1.015);box-shadow:0 22px 38px rgba(0,0,0,.36),0 0 22px rgba(91,231,255,.08);border-color:rgba(91,231,255,.65)}
.metric:hover:before{left:120%}
.panel{backdrop-filter:blur(14px);transform-style:preserve-3d;transition:transform .25s ease,border-color .25s ease,box-shadow .25s ease}
.panel:hover{transform:translateY(-3px) perspective(900px) rotateX(1.2deg);border-color:rgba(91,231,255,.28);box-shadow:0 22px 40px rgba(0,0,0,.25),inset 0 1px rgba(255,255,255,.07)}
[data-testid="stSidebar"]{box-shadow:12px 0 35px rgba(0,0,0,.22)}
[data-testid="stSidebar"] [role="radiogroup"] label{border:1px solid transparent;border-radius:10px;padding:7px 10px;transition:all .2s ease}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(91,231,255,.08);border-color:rgba(91,231,255,.25);transform:translateX(3px)}
.stButton>button{position:relative;overflow:hidden;transform:translateZ(0);box-shadow:0 8px 0 rgba(7,12,22,.45),0 13px 24px rgba(26,100,145,.22),inset 0 1px rgba(255,255,255,.15)}
.stButton>button:active{transform:translateY(3px);box-shadow:0 3px 0 rgba(7,12,22,.45)}
.stButton>button:focus{box-shadow:0 0 0 2px rgba(91,231,255,.25),0 8px 0 rgba(7,12,22,.45)}
.stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{box-shadow:0 0 0 2px rgba(91,231,255,.16)!important;border-color:var(--cyan)!important}
div[data-testid="stDataFrame"]{box-shadow:0 15px 35px rgba(0,0,0,.2)}
@keyframes heroRise{from{opacity:0;transform:perspective(1100px) rotateX(5deg) translateY(15px)}to{opacity:1;transform:perspective(1100px) rotateX(1deg) translateY(0)}}
@keyframes orbFloat{0%,100%{transform:translate3d(0,0,35px) rotate(0deg)}50%{transform:translate3d(0,-10px,45px) rotate(8deg)}}
@keyframes ringPulse{0%,100%{opacity:.7;transform:scale(1)}50%{opacity:1;transform:scale(1.04)}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
@media(max-width:700px){.hero{padding:24px 20px}.hero:before{width:100px;height:100px;right:5%;top:12%}.metric-value{font-size:24px}.block-container{padding-left:1rem;padding-right:1rem}}

</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='eyebrow'>PYTHONGURUKOOL / SECURITY LAB</div>", unsafe_allow_html=True)
    st.markdown("## 🛡️ AccessGuard")
    st.caption("NEXUS // IDENTITY INTELLIGENCE")
    page = st.radio("COMMAND NAVIGATION", [
        "Mission Control", "Identity Directory", "Onboarding Studio",
        "Access Request Center", "Approval Queue", "Revoke Access",
        "Risk & Audit Lab", "AI Security Copilot", "Policy Matrix"
    ])
    st.markdown("---")
    st.markdown("<span class='status ok'>● LOCAL DEMO ONLINE</span>", unsafe_allow_html=True)
    st.caption(f"Data file: {DATA_FILE.name}")
    st.caption("Python · Streamlit · JSON · Optional Gemini")
    if st.button("↻ Reload from disk", use_container_width=True):
        st.session_state.nexus_data = load_data()
        st.rerun()
    if st.button("↺ Reset demo data", use_container_width=True):
        st.session_state.nexus_data = seed_data()
        save_data(st.session_state.nexus_data)
        st.rerun()

st.markdown("""
<div class="hero">
 <div class="eyebrow">INTELLIGENT IDENTITY & ACCESS MANAGEMENT / HACKATHON BUILD</div>
 <h1>ACCESSGUARD <span style="color:#5be7ff">NEXUS</span></h1>
 <p>One command surface for workforce identity, least-privilege access, risk-aware approvals,
 audit intelligence, and an optional AI security copilot.</p>
 <span class="chip">ROLE-BASED ACCESS</span><span class="chip">RISK SCORING</span>
 <span class="chip">HUMAN APPROVAL</span><span class="chip">AUDIT TRAIL</span>
 <span class="chip">AI COPILOT READY</span>
</div>
""", unsafe_allow_html=True)

if st.session_state.nexus_notice:
    msg, typ = st.session_state.nexus_notice
    (st.success if typ == "success" else st.error if typ == "error" else st.info)(msg)
    st.session_state.nexus_notice = None

def metric(label, value, foot):
    st.markdown(f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-foot'>{foot}</div></div>", unsafe_allow_html=True)

def employee_rows():
    return [{
        "ID": eid, "Employee": e["name"], "Role": e["role"],
        "Tools": len(e.get("access", [])), "Access": " · ".join(e.get("access", [])),
        "Email": e.get("email", "")
    } for eid, e in employees.items()]

pending_count = sum(1 for r in requests if r["status"] == "Pending Approval")
denials = sum(1 for x in logs if x["status"] == "Denied")
grants = sum(1 for x in logs if x["status"] == "Granted")
high_risk = sum(1 for x in logs if int(x.get("risk", 0)) >= 60)
used_tools = set(t for e in employees.values() for t in e.get("access", []))
unused_tools = sorted(set(TOOLS) - used_tools)

if page == "Mission Control":
    st.markdown("<div class='section-title'>◈ Mission Control</div>", unsafe_allow_html=True)
    cols = st.columns(5)
    with cols[0]: metric("Identities", len(employees), "Registered employees")
    with cols[1]: metric("Active grants", sum(len(e["access"]) for e in employees.values()), "Current assignments")
    with cols[2]: metric("Awaiting approval", pending_count, "Human review required")
    with cols[3]: metric("Denied requests", denials, "Policy blocks in audit log")
    with cols[4]: metric("High-risk events", high_risk, "Risk score ≥ 60")
    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("<div class='section-title'>▤ Live Identity Access Matrix</div>", unsafe_allow_html=True)
        st.dataframe(employee_rows(), use_container_width=True, hide_index=True)
    with right:
        st.markdown("<div class='section-title'>◉ Security Posture</div>", unsafe_allow_html=True)
        risk_pct = min(100, round((high_risk / max(1, len(logs))) * 100))
        st.markdown(f"""<div class='panel'><div class='eyebrow'>RISK EVENT RATIO</div>
        <h2 style='color:white;margin:8px 0'>{risk_pct}%</h2>
        <div style='height:9px;background:#25354c;border-radius:99px;overflow:hidden'>
        <div style='height:100%;width:{risk_pct}%;background:linear-gradient(90deg,#5be7ff,#ff718d)'></div></div>
        <p class='small-muted'>Based on demo heuristic scores, not a certified risk model.</p>
        <hr><div class='eyebrow'>UNASSIGNED COMPANY TOOLS</div>
        <p>{' · '.join(unused_tools) if unused_tools else 'All tools currently assigned'}</p>
        </div>""", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>⌁ Recent Security Events</div>", unsafe_allow_html=True)
    for item in reversed(logs[-6:]):
        cls = "ok" if item["status"] in ("Granted", "Created", "Revoked", "Approved") else ("warn" if item["status"] in ("Pending", "Updated") else "bad")
        st.markdown(f"""<div class='panel' style='padding:12px 16px;margin-bottom:8px'>
        <span class='status {cls}'>{item['status'].upper()}</span>
        <b>{item['id']}</b> · {item['tool']}
        <span style='float:right;color:#8298b7;font-size:11px'>{item['date']}</span>
        <div class='small-muted'>{item.get('detail','')} · risk {item.get('risk',0)}/100</div></div>""", unsafe_allow_html=True)

elif page == "Identity Directory":
    st.markdown("<div class='section-title'>▤ Identity Directory</div>", unsafe_allow_html=True)
    q = st.text_input("Search identities", placeholder="Employee ID, name, role, or email")
    rows = employee_rows()
    if q:
        rows = [r for r in rows if q.lower() in " ".join(map(str, r.values())).lower()]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    if employees:
        eid = st.selectbox("Inspect identity", list(employees.keys()))
        e = employees[eid]
        a, b, c = st.columns(3)
        with a: metric("Identity", eid, e["name"])
        with b: metric("Role", e["role"], "RBAC profile")
        with c: metric("Tool grants", len(e["access"]), "Current access")
        st.markdown("**Identity details**")
        st.json({"name": e["name"], "role": e["role"], "email": e["email"],
                 "experience": e.get("experience", 0), "phone": e.get("phone", ""),
                 "access": e["access"], "created_at": e.get("created_at", "")})

elif page == "Onboarding Studio":
    st.markdown("<div class='section-title'>✦ Onboarding Studio</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='eyebrow'>IDENTITY PROVISIONING</div><p class='small-muted'>New employees start with least-privilege defaults from their selected role. No password is generated or stored.</p></div>", unsafe_allow_html=True)
    with st.form("onboard"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full name", placeholder="First name Last name")
            eid = st.text_input("Employee ID", placeholder="E104").strip().upper()
            role = st.selectbox("Role", ROLES)
        with c2:
            experience = st.number_input("Experience (years)", min_value=0, max_value=60, value=0)
            phone = st.text_input("Phone (optional)")
            st.info("Default permissions: " + ", ".join(ROLE_PERMISSIONS[role]))
        submit = st.form_submit_button("＋ Provision identity", use_container_width=True)
    if submit:
        parts = name.strip().split()
        valid_name = len(parts) >= 2 and all(p.replace("-", "").replace("'", "").isalpha() for p in parts)
        if not valid_name:
            st.error("Enter a valid first and last name.")
        elif not (len(eid) == 4 and eid.startswith("E") and eid[1:].isdigit()):
            st.error("Employee ID must look like E104.")
        elif eid in employees:
            st.error("That employee ID already exists.")
        elif phone and not (phone.isdigit() and len(phone) == 10):
            st.error("Phone must be blank or exactly 10 digits.")
        else:
            first = parts[0].lower()
            last = "".join(parts[1:]).lower()
            employees[eid] = {"name": name.strip().title(), "role": role,
                              "access": ROLE_PERMISSIONS[role].copy(),
                              "email": first + last + "@pythongurukool.com",
                              "experience": int(experience), "phone": phone,
                              "created_at": now_stamp()}
            audit(eid, "ONBOARDING", "Created", f"Provisioned with role {role}", 5)
            save_data(data)
            st.success(f"Identity provisioned: {eid} · {employees[eid]['email']}")
            st.rerun()

elif page == "Access Request Center":
    st.markdown("<div class='section-title'>⇧ Risk-Aware Access Request</div>", unsafe_allow_html=True)
    st.caption("Requests outside role policy are denied. Sensitive or medium-risk requests enter the approval queue.")
    with st.form("access_request"):
        eid = st.selectbox("Requesting employee", list(employees.keys()),
                           format_func=lambda x: f"{x} — {employees[x]['name']} ({employees[x]['role']})")
        tool = st.selectbox("Requested tool", TOOLS)
        justification = st.text_area("Business justification", placeholder="Explain why this access is needed.")
        submit = st.form_submit_button("Evaluate request", use_container_width=True)
    if submit:
        if len(justification.strip()) < 10:
            st.error("Please provide a meaningful justification (at least 10 characters).")
        elif tool in employees[eid]["access"]:
            st.info(f"{employees[eid]['name']} already has {tool} access.")
        else:
            req = create_request(eid, tool, justification)
            st.markdown(f"### Request result: `{req['status']}`")
            st.progress(req["risk"])
            st.write(f"**Risk score:** {req['risk']}/100")
            st.write("**Risk signals:** " + "; ".join(req["risk_reasons"]))
            if req["status"] == "Approved":
                st.success("Low-risk request approved by the demo policy engine.")
            elif req["status"] == "Pending Approval":
                st.warning("Request queued for a human reviewer. Access has not been granted yet.")
            else:
                st.error("Request denied by role policy/risk rules.")
            st.rerun()

elif page == "Approval Queue":
    st.markdown("<div class='section-title'>◈ Human Approval Queue</div>", unsafe_allow_html=True)
    pending = [r for r in requests if r["status"] == "Pending Approval"]
    if not pending:
        st.success("Queue clear — no pending approvals.")
    for req in pending:
        e = employees.get(req["employee_id"], {})
        with st.expander(f"{req['request_id']} · {e.get('name', req['employee_id'])} · {req['tool']} · risk {req['risk']}/100", expanded=True):
            st.write("**Business justification:**", req["justification"])
            st.write("**Risk signals:**", ", ".join(req["risk_reasons"]))
            st.write("**Created:**", req["created_at"])
            st.progress(req["risk"])
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✓ Approve request", key="approve_" + req["request_id"], use_container_width=True):
                    if req["tool"] in ROLE_PERMISSIONS[e.get("role", "Intern")]:
                        if req["tool"] not in e.get("access", []):
                            e.setdefault("access", []).append(req["tool"])
                        req["status"] = "Approved"
                        req["reviewed_by"] = "Demo reviewer"
                        req["reviewed_at"] = now_stamp()
                        audit(req["employee_id"], req["tool"], "Granted",
                              f"Human-approved {req['request_id']}", req["risk"])
                        save_data(data)
                        st.rerun()
                    else:
                        st.error("Cannot approve: employee's current role does not permit this tool.")
            with c2:
                if st.button("✕ Reject request", key="reject_" + req["request_id"], use_container_width=True):
                    req["status"] = "Rejected"
                    req["reviewed_by"] = "Demo reviewer"
                    req["reviewed_at"] = now_stamp()
                    audit(req["employee_id"], req["tool"], "Denied",
                          f"Reviewer rejected {req['request_id']}", req["risk"])
                    save_data(data)
                    st.rerun()

elif page == "Revoke Access":
    st.markdown("<div class='section-title'>⊘ Access Revocation</div>", unsafe_allow_html=True)
    st.warning("Revocation removes access immediately from this demo record and adds an audit event.")
    with st.form("revoke"):
        eid = st.selectbox("Employee", list(employees.keys()),
                           format_func=lambda x: f"{x} — {employees[x]['name']}")
        current = employees[eid]["access"]
        tool = st.selectbox("Tool to revoke", current if current else ["No assigned tools"])
        confirm = st.checkbox("Confirm revocation")
        submit = st.form_submit_button("Revoke access", use_container_width=True)
    if submit:
        if not current or tool == "No assigned tools":
            st.error("No assigned tools to revoke.")
        elif not confirm:
            st.error("Confirm the action first.")
        else:
            employees[eid]["access"].remove(tool)
            score, _ = risk_score(eid, tool, "revoke")
            audit(eid, tool, "Revoked", "Access removed by operator", score)
            save_data(data)
            st.success(f"Revoked {tool} for {employees[eid]['name']}.")
            st.rerun()

elif page == "Risk & Audit Lab":
    st.markdown("<div class='section-title'>⌁ Risk & Audit Lab</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric("Audit events", len(logs), "Persisted records")
    with c2: metric("Grant events", grants, "Successful assignments")
    with c3: metric("Denied events", denials, "Policy blocks")
    with c4: metric("High-risk", high_risk, "Risk score ≥ 60")
    statuses = sorted(set(x["status"] for x in logs))
    chosen = st.multiselect("Status filter", statuses, default=statuses)
    eid_filter = st.selectbox("Employee filter", ["All"] + list(employees.keys()))
    filtered = [x for x in logs if x["status"] in chosen and (eid_filter == "All" or x["id"] == eid_filter)]
    st.dataframe([{"Employee": x["id"], "Tool/Event": x["tool"], "Status": x["status"],
                   "Timestamp": x["date"], "Risk": x.get("risk", 0), "Details": x.get("detail", "")}
                  for x in reversed(filtered)], use_container_width=True, hide_index=True)
    st.download_button("⬇ Export filtered audit JSON", json.dumps(filtered, indent=2),
                       "accessguard_audit.json", "application/json", use_container_width=True)
    st.download_button("⬇ Export employee directory JSON", json.dumps(employees, indent=2),
                       "accessguard_employees.json", "application/json", use_container_width=True)
    st.download_button("⬇ Export access requests JSON", json.dumps(requests, indent=2),
                       "accessguard_requests.json", "application/json", use_container_width=True)
    st.markdown("<div class='section-title'>◈ Access Overlap Explorer</div>", unsafe_allow_html=True)
    if len(employees) >= 2:
        ids = list(employees)
        a = st.selectbox("Employee A", ids, key="overlap_a")
        b = st.selectbox("Employee B", ids, index=1, key="overlap_b")
        sa, sb = set(employees[a]["access"]), set(employees[b]["access"])
        m1, m2, m3 = st.columns(3)
        with m1: metric("Common tools", len(sa & sb), ", ".join(sorted(sa & sb)) or "None")
        with m2: metric("Only employee A", len(sa - sb), ", ".join(sorted(sa - sb)) or "None")
        with m3: metric("Only employee B", len(sb - sa), ", ".join(sorted(sb - sa)) or "None")
    st.markdown("<div class='section-title'>⚠ Least-Privilege Review</div>", unsafe_allow_html=True)
    findings = []
    for emp_id, e in employees.items():
        excess = sorted(set(e["access"]) - set(ROLE_PERMISSIONS.get(e["role"], [])))
        if excess:
            findings.append({"Employee": emp_id, "Name": e["name"], "Role": e["role"],
                             "Out-of-policy access": ", ".join(excess)})
    if findings:
        st.error("Potential least-privilege exceptions detected.")
        st.dataframe(findings, use_container_width=True, hide_index=True)
    else:
        st.success("No current grants outside the defined role permission matrix.")

elif page == "AI Security Copilot":
    st.markdown("<div class='section-title'>✧ AI Security Copilot</div>", unsafe_allow_html=True)
    key_available = bool(get_secret_key()) and genai is not None
    st.markdown(f"<div class='panel'><div class='eyebrow'>GENAI STATUS</div><h3>{'CONNECTED' if key_available else 'OPTIONAL / NOT CONFIGURED'}</h3><p class='small-muted'>The copilot can summarize supplied demo records and suggest next steps. It cannot approve or change access by itself.</p></div>", unsafe_allow_html=True)
    with st.form("copilot"):
        question = st.text_area("Ask the security copilot", placeholder="Which access risks should we investigate first?")
        submit = st.form_submit_button("Analyze security posture", use_container_width=True)
    if submit:
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            context = {
                "employees": {eid: {"name": e["name"], "role": e["role"], "access": e["access"]}
                              for eid, e in employees.items()},
                "recent_logs": logs[-30:],
                "pending_requests": [r for r in requests if r["status"] == "Pending Approval"],
                "role_permissions": ROLE_PERMISSIONS,
                "sensitive_tools": sorted(SENSITIVE_TOOLS),
            }
            with st.spinner("Reviewing the current demo security context..."):
                answer = ai_copilot(question, context)
            if answer:
                st.markdown("<div class='panel'>", unsafe_allow_html=True)
                st.markdown(answer)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("Gemini is not configured, so showing the built-in offline analysis.")
                risky = []
                for eid, e in employees.items():
                    out = sorted(set(e["access"]) - set(ROLE_PERMISSIONS[e["role"]]))
                    if out:
                        risky.append(f"- {eid} ({e['name']}): out-of-policy access: {', '.join(out)}")
                pending = [r for r in requests if r["status"] == "Pending Approval"]
                st.markdown("### Assessment")
                st.write(f"There are {len(employees)} identities, {len(pending)} pending approvals, and {denials} denial events.")
                st.markdown("### Evidence")
                st.write("\n".join(risky) if risky else "No current role-policy exceptions were found.")
                st.markdown("### Recommended next step")
                st.write("Review pending requests, validate business justifications for sensitive tools, and revoke access that is no longer needed.")
    with st.expander("How to enable Gemini"):
        st.code('pip install -U google-genai\n# macOS/Linux:\nexport GEMINI_API_KEY="YOUR_KEY"\n# Windows PowerShell:\n$env:GEMINI_API_KEY="YOUR_KEY"\n# Then restart Streamlit')
        st.caption("Never paste your API key into source code or commit it to a public repository.")

elif page == "Policy Matrix":
    st.markdown("<div class='section-title'>◈ Role Policy Matrix</div>", unsafe_allow_html=True)
    st.caption("The policy engine applies least privilege. Sensitive systems are routed to human review when role policy permits them.")
    matrix = [{"Role": role, **{tool: ("✓" if tool in ROLE_PERMISSIONS[role] else "—") for tool in TOOLS}}
              for role in ROLES]
    st.dataframe(matrix, use_container_width=True, hide_index=True)
    for role in ROLES:
        with st.expander(f"{role} · {len(ROLE_PERMISSIONS[role])} permitted tools"):
            st.write(ROLE_PERMISSIONS[role])
            st.progress(len(ROLE_PERMISSIONS[role]) / len(TOOLS))
    st.markdown("---")
    st.markdown("### Policy principles")
    st.markdown("""
    - **Least privilege:** employees start with only role-defined access.
    - **Risk-aware routing:** sensitive or medium-risk requests require human approval.
    - **Explicit review:** pending requests do not grant access until approved.
    - **Traceability:** grants, denials, onboarding, role changes, and revocations are logged.
    - **Separation of duties:** the AI copilot recommends; it does not execute privileged actions.
    """)
    st.info("Demo limitation: reviewer identity is a placeholder. A real system needs authenticated approvers and server-side authorization.")

st.markdown("---")
st.markdown("<div style='display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;color:#7187a7;font-size:11px'><span>ACCESSGUARD NEXUS · HACKATHON EDITION</span><span>RBAC · RISK ENGINE · HUMAN APPROVAL · AUDIT INTELLIGENCE</span></div>", unsafe_allow_html=True)
