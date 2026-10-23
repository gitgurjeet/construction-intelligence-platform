import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = "gemini-flash-lite-latest"


def analyze_image(client, image_bytes, mime_type, prompt, retries=3):
    """Photo + prompt AI ko bhejta hai, JSON wapas deta hai. 503 pe retry karta hai."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )
            return json.loads(response.text)
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


PPE_PROMPT = """You are a construction site safety inspector.
Analyze this site photo. Reply ONLY with JSON in exactly this format:
{
  "safety_score": <number 0-100>,
  "overall_status": "Safe" | "Needs Attention" | "Unsafe",
  "ppe_detection": {
    "helmet": "Yes" | "No" | "Not visible",
    "high_vis_vest": "Yes" | "No" | "Not visible",
    "safety_boots": "Yes" | "No" | "Not visible",
    "harness": "Yes" | "No" | "Not visible"
  },
  "hazards": [
    {"issue": "<short text>", "severity": "Low" | "Medium" | "High" | "Critical", "remedy": "<short fix>"}
  ]
}
If the photo is not a construction site, set safety_score to 0 and explain in hazards."""

st.set_page_config(page_title="Construction Intelligence Platform", layout="wide")
st.title("Multimodal Construction Intelligence Platform")

# Sidebar
st.sidebar.header("Settings")
user_key = st.sidebar.text_input("Gemini API Key (optional)", type="password")
api_key = user_key or os.getenv("GEMINI_API_KEY")
if not api_key:
    st.sidebar.warning("API key nahi mili. .env ya yahan daalo.")

tab1, tab2, tab3, tab4 = st.tabs([
    "Safety & PPE Audit",
    "Crack Diagnostics",
    "Planning & Valuation",
    "Site Assistant",
])

with tab1:
    st.subheader("Site Safety & PPE Audit")
    site_photo = st.file_uploader(
        "Site photo upload karo", type=["jpg", "jpeg", "png"], key="ppe_photo"
    )

    if site_photo is not None:
        st.image(site_photo, caption="Uploaded site photo", width=500)

        if st.button("Analyze Safety", key="ppe_btn"):
            if not api_key:
                st.error("Pehle API key do.")
            else:
                try:
                    client = genai.Client(api_key=api_key)
                    with st.spinner("AI analyze kar raha hai..."):
                        result = analyze_image(
                            client, site_photo.getvalue(), site_photo.type, PPE_PROMPT
                        )

                    c1, c2 = st.columns(2)
                    c1.metric("Safety Score", result.get("safety_score", "-"))
                    c2.metric("Status", result.get("overall_status", "-"))

                    st.markdown("**PPE Check**")
                    for item, status in result.get("ppe_detection", {}).items():
                        st.write(f"- {item}: {status}")

                    st.markdown("**Hazards**")
                    for h in result.get("hazards", []):
                        st.write(
                            f"- **{h.get('severity')}**: {h.get('issue')} "
                            f"-> {h.get('remedy')}"
                        )

                    st.download_button(
                        "Download JSON report",
                        data=json.dumps(result, indent=2),
                        file_name="safety_report.json",
                        mime="application/json",
                    )
                except Exception as e:
                    st.error(f"AI se jawab nahi mila: {e}")

CRACK_PROMPT = """You are a structural engineer inspecting a concrete or wall surface.
Analyze this photo. Reply ONLY with JSON in exactly this format:
{
  "defect_type": "Hairline" | "Settlement" | "Structural Shear" | "Thermal Expansion" | "Spalling" | "No defect",
  "estimated_width_mm": <number>,
  "severity": "Low" | "Medium" | "High" | "Critical",
  "root_causes": ["<short text>", "<short text>"],
  "recommended_repairs": ["<short text>", "<short text>"],
  "urgency": "Monitor" | "Repair within 3 months" | "Repair within 1 week" | "Immediate action"
}
If the photo is not a concrete or wall surface, set defect_type to "No defect" and explain in root_causes."""

with tab2:
    st.subheader("Crack Diagnostics & Structural Integrity")
    crack_photo = st.file_uploader(
        "Deewar / concrete ki photo upload karo",
        type=["jpg", "jpeg", "png"],
        key="crack_photo",
    )

    if crack_photo is not None:
        st.image(crack_photo, caption="Uploaded surface photo", width=500)

        if st.button("Diagnose Crack", key="crack_btn"):
            if not api_key:
                st.error("Pehle API key do.")
            else:
                try:
                    client = genai.Client(api_key=api_key)
                    with st.spinner("AI diagnose kar raha hai..."):
                        result = analyze_image(
                            client, crack_photo.getvalue(), crack_photo.type, CRACK_PROMPT
                        )

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Defect Type", result.get("defect_type", "-"))
                    c2.metric("Crack Width (mm)", result.get("estimated_width_mm", "-"))
                    c3.metric("Severity", result.get("severity", "-"))
                    st.write(f"**Urgency:** {result.get('urgency', '-')}")

                    st.markdown("**Root Causes**")
                    for cause in result.get("root_causes", []):
                        st.write(f"- {cause}")

                    st.markdown("**Recommended Repairs**")
                    for fix in result.get("recommended_repairs", []):
                        st.write(f"- {fix}")

                    st.download_button(
                        "Download JSON report",
                        data=json.dumps(result, indent=2),
                        file_name="crack_report.json",
                        mime="application/json",
                    )
                except Exception as e:
                    st.error(f"AI se jawab nahi mila: {e}")

def format_inr(amount):
    """Rupees ko Lakhs / Crores mein dikhata hai."""
    if amount >= 1_00_00_000:
        return f"Rs {amount / 1_00_00_000:.2f} Cr"
    return f"Rs {amount / 1_00_000:.2f} Lakh"


# Approx rates (assumption, sirf estimate ke liye)
BUILD_COST_PER_SQFT = {
    "Residential House": 1800,
    "Apartment Building": 2000,
    "Commercial Building": 2500,
    "Industrial Shed": 1500,
}
MARKET_RATE_PER_SQFT = {"Tier 1": 9000, "Tier 2": 5500, "Tier 3": 3500}

with tab3:
    st.subheader("Planning & Real Estate Valuation")

    col1, col2 = st.columns(2)
    structure = col1.selectbox("Structure type", list(BUILD_COST_PER_SQFT.keys()))
    tier = col2.selectbox("Location tier", list(MARKET_RATE_PER_SQFT.keys()))
    area = st.number_input("Built-up area (sqft)", min_value=100, value=1500, step=100)
    progress = st.slider("Completion %", 0, 100, 40)

    total_budget = area * BUILD_COST_PER_SQFT[structure]
    spent = total_budget * progress / 100
    full_value = area * MARKET_RATE_PER_SQFT[tier]
    current_value = full_value * progress / 100

    steel_kg = area * 4        # approx 4 kg steel per sqft
    cement_bags = area * 0.4   # approx 0.4 bag per sqft

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Budget", format_inr(total_budget))
    m2.metric("Spent So Far", format_inr(spent))
    m3.metric("Current Asset Value", format_inr(current_value))

    m4, m5 = st.columns(2)
    m4.metric("Steel Required (kg)", f"{steel_kg:,.0f}")
    m5.metric("Cement Required (bags)", f"{cement_bags:,.0f}")

    st.progress(progress / 100, text=f"Project progress: {progress}%")
    st.caption("Note: rates approximate assumptions hain, sirf estimate ke liye.")

WEATHER_ALERTS = {
    "Normal": [
        "Regular safety briefing karo aur PPE check karo.",
        "Scaffolding aur ladders ki daily inspection karo.",
    ],
    "High Wind": [
        "Crane operations turant suspend karo.",
        "Ooncha scaffolding aur loose sheets secure karo, ooncha kaam roko.",
        "Loose material (tiles, pipes) neeche utaar do.",
    ],
    "Heavy Rain": [
        "Electrical hazard: temporary wiring aur panels ko dhako, power off karo.",
        "Fresh concrete ko tarpaulin se cover karo, curing protocol follow karo.",
        "Fisalan wali jagah aur excavation pits check karo.",
    ],
    "Extreme Heat": [
        "Workers ko har ghante paani aur chhaanv mein break do.",
        "Dopahar ka heavy kaam shift karo (subah ya shaam).",
        "Concrete ko jaldi sookhne se bachane ke liye curing/paani do.",
    ],
}


def ask_ai_text(client, prompt, retries=3):
    """Sirf text prompt bhejta hai, 503 pe retry karta hai."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return response.text
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))


with tab4:
    st.subheader("Daily Site Assistant & Weather Advisory")

    weather = st.selectbox("Aaj ka mausam", list(WEATHER_ALERTS.keys()))
    if weather == "Normal":
        st.success("Normal conditions")
    else:
        st.warning(f"{weather} alert")
    for tip in WEATHER_ALERTS[weather]:
        st.write(f"- {tip}")

    st.divider()
    st.markdown("**Construction Engineering Assistant**")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Construction ke baare mein kuch bhi pucho...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        if not api_key:
            st.error("Pehle API key do.")
        else:
            try:
                client = genai.Client(api_key=api_key)
                history_text = "\n".join(
                    f"{m['role']}: {m['content']}"
                    for m in st.session_state.chat_history
                )
                prompt = (
                    "You are a helpful construction engineering assistant. "
                    f"Current site weather: {weather}. "
                    "Answer briefly and practically. Conversation so far:\n"
                    + history_text
                )
                with st.spinner("Soch raha hai..."):
                    answer = ask_ai_text(client, prompt)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": answer}
                )
                with st.chat_message("assistant"):
                    st.write(answer)
            except Exception as e:
                st.error(f"AI se jawab nahi mila: {e}")