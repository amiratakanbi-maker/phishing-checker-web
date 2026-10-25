import re

import streamlit as st

from phish import analyse

st.set_page_config(page_title="Phishing Message Checker", page_icon="🛡️")

# ---------- Example messages people can load to try the checker ----------
EXAMPLES = {
    "Choose an example...": "",
    "Parcel delivery text (scam)": (
        "EVRI: PARCEL COULD NOT BE DELIVERED ON 02 MARCH 2026 at 11:57 AM due to no one "
        "being home. Reschedule your missed delivery now at: https://evr.i275103uk.com"
    ),
    "Job offer text (scam)": (
        "Hello! This is TikTok HR. We'd like to invite you to be our online employee. "
        "With just a mobile phone and working in your spare time, you can earn 300-800 "
        "daily. Leave a message now and get a 8 bonus. Please contact us for details. "
        "WA: http://wa.me/44XXXXXXXXXX"
    ),
    "Email with sender details (scam)": (
        'From: "PayPal Support" <help@paypa1-secure.com>\n'
        "Reply-To: attacker@mailbox.ru\n"
        "Subject: Account suspended\n"
        "\n"
        "Dear customer, your account will be closed within 24 hours.\n"
        "Verify your account here: https://paypa1-secure.com/login"
    ),
    "Delivery text (genuine)": (
        "Evri: Your parcel from ASOS will be delivered tomorrow between 10:00 and 14:00. "
        "Track it at https://www.evri.com/track/ab12cd34"
    ),
    "Bank card alert (genuine)": (
        "Barclays: A payment of GBP 34.20 to TESCO STORES was made on your card ending "
        "1234. If this wasn't you, call the number on the back of your card."
    ),
}


def plain(text):
    """Makes text from the message safe to show. Text in a message is written by the
    sender, so it must never be allowed to turn into a clickable link or formatting."""
    return re.sub(r"([!-/:-@\[-`{-~])", r"\\\1", text)


# ---------- Button and menu actions ----------
def load_example():
    st.session_state.message = EXAMPLES[st.session_state.example]
    st.session_state.result = None


def clear_all():
    st.session_state.message = ""
    st.session_state.example = "Choose an example..."
    st.session_state.result = None


if "message" not in st.session_state:
    st.session_state.message = ""
if "result" not in st.session_state:
    st.session_state.result = None
if "example" not in st.session_state:
    st.session_state.example = "Choose an example..."


# ---------- Showing the result ----------
def show_result(result):
    score = result["score"]
    level = result["level"]

    st.markdown("---")
    st.metric("Phishing risk", str(score) + "%")
    st.progress(score / 100)

    banner = "**" + level + "**\n\n" + result["advice"]
    if level == "HIGH RISK":
        st.error(banner)
    elif level == "SUSPICIOUS":
        st.warning(banner)
    else:
        st.success(banner)

    for note in result["notes"]:
        st.info(note)

    st.subheader("Why this result?")
    if not result["findings"]:
        st.write("No warning signs were found.")
    number = 1
    for finding in result["findings"]:
        pct = str(round(finding["weight"] * 100))
        st.markdown(plain(str(number) + ". " + finding["reason"] + " (adds " + pct + "% risk)"))
        with st.expander("Why does this matter?"):
            st.markdown(plain(finding["why"]))
        number = number + 1

    if result["links"]:
        st.subheader("Links found in the message")
        st.caption("Shown as plain text on purpose. Do not type or click these.")
        for link in result["links"]:
            st.code(link, language=None)


# ---------- The page ----------
st.title("🛡️ Phishing Message Checker")
st.write(
    "Got a text or email you're not sure about? Paste it below and this tool will "
    "estimate how likely it is to be a scam, and explain why."
)
st.caption(
    "This tool does not save the messages you paste. Even so, please don't paste "
    "anything containing passwords or card numbers."
)

st.selectbox("Try an example", list(EXAMPLES.keys()), key="example", on_change=load_example)

st.text_area(
    "Paste the message here",
    key="message",
    height=250,
    max_chars=10000,
    placeholder="Paste the text message or email here. For emails, include the From: line if you can.",
)

col1, col2 = st.columns(2)
with col1:
    check = st.button("Check message", type="primary")
with col2:
    st.button("Clear", on_click=clear_all)

if check:
    text = st.session_state.message
    if not text.strip():
        st.session_state.result = None
        st.warning("Please paste a message first.")
    else:
        try:
            st.session_state.result = analyse(text)
        except Exception:
            st.session_state.result = None
            st.error(
                "Sorry, something went wrong while checking that message. "
                "Please try again with just the message text."
            )

if st.session_state.result:
    show_result(st.session_state.result)

st.markdown("---")
with st.expander("How does this work?"):
    st.write(
        "The checker looks for warning signs that scam messages often share: "
        "pressure to act quickly, links that go to look-alike or number-only websites, "
        "senders pretending to be a well-known company, fake job and prize offers, "
        "claims that you are owed money, and wording that has been disguised to get past "
        "spam filters. Each warning sign adds to the risk score."
    )
    st.write(
        "It is a guide, not a guarantee. A low score does not prove a message is safe, "
        "and a high score does not prove it is a scam. If in doubt, contact the company "
        "using a phone number or website you already trust."
    )

with st.expander("Think it's a scam? Report it"):
    st.write(
        "In the UK you can forward suspicious texts to 7726 (it's free) and suspicious "
        "emails to report@phishing.gov.uk."
    )
