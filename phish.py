import email
import re
import unicodedata
from difflib import SequenceMatcher
from email import policy
from email.utils import parseaddr
from urllib.parse import urlparse


# ---------- INPUT ----------
def read_message():
    print("Paste the message below.")
    print("When you are finished, type END on a new line and press Enter.\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


# ---------- ENGINE ----------
def parse(raw):
    if re.match(r"(?im)^(from|to|subject|date|reply-to):", raw):
        try:
            msg = email.message_from_string(raw, policy=policy.default)
            part = msg.get_body(preferencelist=("plain", "html"))
            text = part.get_content() if part else raw
            return (str(msg["From"] or ""), str(msg["Reply-To"] or ""),
                    str(msg["Subject"] or ""), text)
        except Exception:
            pass
    return "", "", "", raw


# STEP 11 NEW: web addresses written without http:// or https://
TLDS = (r"co\.uk|org\.uk|gov\.uk|ac\.uk|uk|com|net|org|info|io|me|ly|co|"
        r"claims|xyz|top|click|link|online|site|shop|app")
BARE_DOMAIN_PATTERN = (r"(?<![@\w.-])"
                       r"(?:www\.[a-z0-9-]+(?:\.[a-z0-9-]+)+"
                       r"|[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:" + TLDS + r")\b)"
                       r"(?:/[^\s<>\"')]*)?")


# STEP 11 CHANGED: also finds links that have no http:// or https://
def find_links(text):
    with_scheme = r"https?://[^\s<>\"')]+"
    found = re.findall(with_scheme, text)

    # Look for bare addresses in what is left after removing the links found above
    rest = re.sub(with_scheme, " ", text)
    for bare in re.findall(BARE_DOMAIN_PATTERN, rest, re.IGNORECASE):
        found.append("https://" + bare)

    links = []
    for link in found:
        link = link.rstrip(".,;:!?")
        if link not in links:
            links.append(link)
    return links


def get_domain(link):
    return (urlparse(link).hostname or "").lower()


# STEP 8 NEW: one reusable function for every "does the message use these phrases?" check
def check_wording(text, phrases, label, why, base=0.15, per_hit=0.08, cap=0.4):
    lowered = text.lower()
    hits = [phrase for phrase in phrases if phrase in lowered]
    if not hits:
        return []
    weight = min(base + per_hit * len(hits), cap)
    return [{
        "weight": weight,
        "reason": label + ": " + ", ".join(hits[:4]),
        "why": why,
    }]


PRESSURE_PHRASES = [
    "urgent", "immediately", "within 24 hours", "account suspended",
    "account will be closed", "final notice", "act now",
    "verify your account", "unusual activity", "action required",
    "limited time",
]

# STEP 8 NEW: delivery wording. Weak on its own, because real couriers use it too
PARCEL_PHRASES = [
    "parcel", "could not be delivered", "missed delivery", "reschedule",
    "redeliver", "delivery fee", "customs", "package",
]
# STEP 9 NEW: fake job offer wording. Each phrase is common in genuine job ads too,
# so it is the combination with the checks below that matters
JOB_PHRASES = [
    "spare time", "part-time", "work from home", "remote position", "remote part-time",
    "free training", "full training", "no experience", "paid immediately",
    "payment made immediately", "reviewed your cv", "reviewed your profile",
    "online employee", "human resources", "hr team", "hr manager",
]

# STEP 9 NEW: asking you to move the conversation to a chat app
CHAT_APP_PHRASES = ["whatsapp", "wa.me", "telegram", "t.me/"]

# STEP 9 NEW: a pattern (not a fixed phrase) for big "daily pay" claims
EARNINGS_PATTERN = (r"daily (earnings|income|pay|salary)"
                    r"|salary:\s*daily"
                    r"|earn[^.\n]{0,30}(daily|a day|per day)")


def check_earnings(text):
    match = re.search(EARNINGS_PATTERN, text, re.IGNORECASE)
    if not match:
        return []
    return [{
        "weight": 0.35,
        "reason": "Promises daily pay: '" + match.group(0).strip() + "'",
        "why": "Real jobs rarely promise hundreds of pounds a day for a few minutes of "
               "easy work. This is the main hook in fake job offers.",
    }]
# STEP 10 NEW: "you could be owed..." claim-style wording
CLAIM_PHRASES = [
    "you could be owed", "you may be owed", "be owed up to", "owed on average",
    "mis-sold", "check for free", "check in 30 secs", "eligible to claim",
    "financed a vehicle", "thousands checking now",
]

# STEP 10 NEW: the "Text STOP to..." line that mass-marketing texts end with
OPTOUT_PATTERN = r"\b(text|reply|send)\s+(stop|exit)\b|exit\s*=\s*\d+"


def check_optout(text):
    match = re.search(OPTOUT_PATTERN, text, re.IGNORECASE)
    if not match:
        return []
    return [{
        "weight": 0.12,
        "reason": "Opt-out line typical of mass marketing texts: '" + match.group(0) + "'",
        "why": "Texts sent to thousands of numbers have to offer a way to opt out. "
               "A real person messaging you doesn't add this line.",
    }]
# STEP 12 NEW: see through disguised wording
ZERO_WIDTH = "\u200b\u200c\u200d\u2060\ufeff"


def clean_text(text):
    """Turns look-alike characters (like fullwidth letters) back into normal ones,
    straightens curly apostrophes (phones type them) and removes invisible characters,
    so word checks still work."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    for ch in ZERO_WIDTH:
        text = text.replace(ch, "")
    return text


# Letters from these alphabets are often used to imitate English letters
LOOKALIKE_SCRIPTS = ("CYRILLIC", "GREEK", "FULLWIDTH", "MATHEMATICAL", "KELVIN")


def count_odd_characters(text):
    """Counts invisible, broken or look-alike characters sitting inside words."""
    count = 0
    for word in text.split():
        if not any(ch.isascii() and ch.isalpha() for ch in word):
            continue
        for ch in word:
            if ch.isascii():
                continue
            category = unicodedata.category(ch)
            name = unicodedata.name(ch, "")
            if category in ("Cf", "Co", "Cn") or ch == "\ufffd" or name.startswith(LOOKALIKE_SCRIPTS):
                count = count + 1
    return count


def check_obfuscation(text):
    # Leave web addresses out, because "?" is normal inside them
    no_urls = re.sub(r"\S*(?:https?://|www\.|\.[a-z]{2,4}/)\S*", " ", text, flags=re.IGNORECASE)

    count = count_odd_characters(no_urls)
    # A "?" dropped into a word, as in "?lexible" or "straight?orward"
    count += len(re.findall(r"[A-Za-z]\?[A-Za-z]|(?<![\w?])\?[A-Za-z]{2,}", no_urls))
    # The same letter split off from its word again and again, as in "Wor k" and "lin k".
    # (One-off cases like "vitamin d" are normal, so a letter must repeat to count.)
    split_letters = re.findall(r"(?<=[A-Za-z]) ([bcdfghjklmnpqrstvwxz])(?= |\n|$)", no_urls)
    for letter in set(split_letters):
        if split_letters.count(letter) >= 2:
            count += split_letters.count(letter)

    if count < 2:
        return []
    weight = min(0.25 + 0.03 * count, 0.5)
    return [{
        "weight": weight,
        "reason": "Wording looks deliberately disguised (" + str(count)
                  + " odd characters or split-up words)",
        "why": "Scammers swap letters for look-alike symbols or split words up so that "
               "spam filters don't recognise them. Honest senders have no reason to do this.",
    }]
# STEP 13 NEW: more scam wording families. Each phrase is also used in some genuine
# messages, so every family is weighted so that one or two matches stay below the flag line
PRIZE_PHRASES = [
    "selected to win", "you have been selected", "you've been selected", "you have won",
    "you've won", "you are a winner", "lucky winner", "claim your prize",
    "claim your reward", "congratulations", "free gift",
]

TECH_SUPPORT_PHRASES = [
    "virus detected", "infected with", "computer has been infected",
    "do not turn off your computer", "certified technician", "call microsoft",
    "call apple support", "your computer is at risk", "security warning", "malware",
]

INVESTMENT_PHRASES = [
    "crypto", "bitcoin", "trading platform", "guaranteed returns", "guaranteed profit",
    "risk-free", "passive income", "investment opportunity", "double your", "forex",
    "places left", "limited spots",
]

ACCOUNT_SECURITY_PHRASES = [
    "unusual sign-in", "sign-in activity", "suspicious sign-in", "suspicious activity",
    "confirm your identity", "verify your identity", "confirm your details",
    "account will be limited", "account has been limited", "account has been locked",
    "account has been suspended", "update your payment", "update your details",
    "payment has failed", "payment failed", "payment was declined",
    "unable to process your payment", "security alert", "login attempt",
]

# Messages pretending to be a relative, friend or boss who needs money or a favour fast.
# Genuine messages say some of these too, so it takes three or more to matter
IMPERSONATION_PHRASES = [
    "my new number", "dropped my phone", "lost my phone",
    "banking app is locked", "can you transfer", "could you transfer", "pay you back",
    "are you at your desk", "confidential payment", "can't take calls",
    "can't talk right now", "gift card", "keep this between us",
]

SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
              "is.gd", "buff.ly", "cutt.ly"]

# STEP 13 CHANGED: dvla, hsbc, lloyds, natwest, santander, monzo, tesco, nhs, tvlicensing added
BRANDS = {
    "paypal": ["paypal.com"],
    "microsoft": ["microsoft.com", "live.com", "office.com"],
    "apple": ["apple.com", "icloud.com"],
    "amazon": ["amazon.com", "amazon.co.uk"],
    "google": ["google.com", "gmail.com"],
    "netflix": ["netflix.com"],
    "dhl": ["dhl.com"],
    "barclays": ["barclays.co.uk", "barclays.com"],
    "evri": ["evri.com"],
    "royalmail": ["royalmail.com"],
    "dpd": ["dpd.co.uk", "dpd.com"],
    "hmrc": ["hmrc.gov.uk", "gov.uk"],
    "dvla": ["dvla.gov.uk", "gov.uk"],
    "hsbc": ["hsbc.co.uk", "hsbc.com"],
    "lloyds": ["lloydsbank.com", "lloydsbank.co.uk", "lloydsbankinggroup.com"],
    "natwest": ["natwest.com"],
    "santander": ["santander.co.uk", "santander.com"],
    "monzo": ["monzo.com"],
    "tesco": ["tesco.com"],
    "nhs": ["nhs.uk"],
    "tvlicensing": ["tvlicensing.co.uk"],
}

def is_real_domain(host, real_domains):
    for real in real_domains:
        if host == real or host.endswith("." + real):
            return True
    return False


def check_brand_lookalike(host, where):
    findings = []
    parts = re.split(r"[.-]", host)
    for brand, real_domains in BRANDS.items():
        if is_real_domain(host, real_domains):
            continue
        if brand in host:
            findings.append({
                "weight": 0.45,
                "reason": where + " uses the name '" + brand + "' but does not belong to the real "
                          + brand + ": " + host,
                "why": "Scammers put a famous name inside their own address.",
            })
        else:
            for part in parts:
                if SequenceMatcher(None, part, brand).ratio() > 0.8:
                    findings.append({
                        "weight": 0.5,
                        "reason": where + " has '" + part + "', which looks like a misspelling of '"
                                  + brand + "': " + host,
                        "why": "Scammers swap or change a letter (like 1 for l) "
                               "so the address looks right at a glance.",
                    })
                    break
    return findings


def check_links(links):
    findings = []
    for link in links:
        host = get_domain(link)
        if not host:
            continue

        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
            findings.append({
                "weight": 0.5,
                "reason": "Link goes to a number address: " + host,
                "why": "Real companies use a website name, not a string of numbers.",
            })

        if host in SHORTENERS:
            findings.append({
                "weight": 0.2,
                "reason": "Shortened link: " + host,
                "why": "Short links hide where you will really end up.",
            })

        if "xn--" in host:
            findings.append({
                "weight": 0.4,
                "reason": "Website name uses disguised characters: " + host,
                "why": "Some letters from other alphabets look identical to normal ones, "
                       "so a fake site can look real.",
            })

        if link.startswith("http://"):
            findings.append({
                "weight": 0.08,
                "reason": "Link is not encrypted (http, not https): " + host,
                "why": "Trustworthy sites that ask for logins nearly always use https.",
            })

        findings.extend(check_brand_lookalike(host, "Link"))
    return findings


def check_sender(sender, reply_to):
    findings = []
    name, address = parseaddr(sender)
    from_dom = address.split("@")[-1].lower() if "@" in address else ""
    if not from_dom:
        return findings

    # Display name says one company, address belongs to another
    for brand, real_domains in BRANDS.items():
        if brand in name.lower() and not is_real_domain(from_dom, real_domains):
            findings.append({
                "weight": 0.5,
                "reason": "Sender name says '" + name + "' but the address is from " + from_dom,
                "why": "Anyone can type any name. The address is the part that is hard to fake.",
            })

    # Is the sender's own address a fake or misspelled brand?
    findings.extend(check_brand_lookalike(from_dom, "Sender address"))

    # Replies go somewhere different from where the message came from
    reply_address = parseaddr(reply_to)[1]
    reply_dom = reply_address.split("@")[-1].lower() if "@" in reply_address else ""
    if (reply_dom and reply_dom != from_dom
            and not reply_dom.endswith("." + from_dom)
            and not from_dom.endswith("." + reply_dom)):
        findings.append({
            "weight": 0.3,
            "reason": "Replies would go to " + reply_dom + ", not " + from_dom,
            "why": "Scammers send from one address but collect your reply at another.",
        })
    return findings


def calculate_risk(findings):
    safe = 1.0
    for finding in findings:
        safe = safe * (1 - finding["weight"])
    return round((1 - safe) * 100)


def get_level(score):
    if score >= 70:
        return "HIGH RISK"
    if score >= 35:
        return "SUSPICIOUS"
    return "LOW RISK"


ADVICE = {
    "HIGH RISK": "Do not click any links or reply. Contact the company using "
                 "a phone number or website you already trust.",
    "SUSPICIOUS": "Be careful. Do not click links in this message. Check with "
                  "the sender another way before doing anything.",
    "LOW RISK": "No strong warning signs found, but this is not a guarantee. "
                "Stay alert for anything that feels odd.",
}


def by_weight(finding):
    return finding["weight"]


# STEP 13 CHANGED: five more wording checks
def analyse(raw):
    sender, reply_to, subject, text = parse(raw)
    links = find_links(text)
    original = subject + " " + text
    whole = clean_text(original)
    findings = (check_wording(whole, PRESSURE_PHRASES, "Pressure wording",
                              "Scammers rush you so you act before you think. "
                              "Real companies rarely threaten to close your account within hours.")
                + check_wording(whole, PARCEL_PHRASES, "Delivery wording",
                                "Fake delivery texts are very common. Real couriers use these "
                                "words too, so this only matters alongside a suspicious link.",
                                base=0.1, per_hit=0.07, cap=0.25)
                + check_wording(whole, JOB_PHRASES, "Job offer wording",
                                "Fake job offers promise easy work for your spare time. "
                                "Each phrase is normal in real job ads, so this counts most "
                                "when combined with the signs below.",
                                base=0.15, per_hit=0.06, cap=0.35)
                + check_earnings(whole)
                + check_wording(whole, CHAT_APP_PHRASES, "Asks you to chat on a messaging app",
                                "Scammers move you to WhatsApp or Telegram, where there is "
                                "no company record and the messages are hard to report.",
                                base=0.3, per_hit=0.0, cap=0.3)
                + check_wording(whole, CLAIM_PHRASES, "Compensation-claim wording",
                                "Texts saying you are 'owed' money are usually mass-sent "
                                "marketing that collects your details, not a record of your "
                                "own finances.",
                                base=0.15, per_hit=0.08, cap=0.4)
                + check_wording(whole, PRIZE_PHRASES, "Prize or reward wording",
                                "Unexpected prizes are bait. You can't win a competition "
                                "you never entered. Genuine prize draws exist too, so this "
                                "alone is not enough to flag a message.",
                                base=0.15, per_hit=0.07, cap=0.3)
                + check_wording(whole, TECH_SUPPORT_PHRASES, "Computer virus warning wording",
                                "Real companies don't text or email to say your computer is "
                                "infected. Scammers want you to call their 'technician'.",
                                base=0.15, per_hit=0.08, cap=0.4)
                + check_wording(whole, INVESTMENT_PHRASES, "Investment pitch wording",
                                "Unsolicited investment tips promising easy money are a "
                                "common way to lose savings.",
                                base=0.15, per_hit=0.08, cap=0.4)
                + check_wording(whole, ACCOUNT_SECURITY_PHRASES, "Account security warning wording",
                                "Scammers pretend your account has a problem so you'll click "
                                "a link and enter your details. Real banks also send security "
                                "messages, so check the link and sender.",
                                base=0.15, per_hit=0.06, cap=0.3)
                + check_wording(whole, IMPERSONATION_PHRASES, "Possible impersonation wording",
                                "Scammers pose as a relative or boss with a new number or a "
                                "reason they can't talk, then ask for money. One of these "
                                "phrases is normal; several together are not.",
                                base=0.0, per_hit=0.12, cap=0.45)
                + check_optout(whole)
                + check_obfuscation(original)
                + check_links(links)
                + check_sender(sender, reply_to))
    findings.sort(key=by_weight, reverse=True)
    score = calculate_risk(findings)
    level = get_level(score)

    notes = []
    if not sender:
        notes.append("No sender found, so the sender checks were skipped. "
                     "Paste the full email, including the From: line, for a better check.")

    return {
        "sender": sender,
        "subject": subject,
        "links": links,
        "findings": findings,
        "notes": notes,
        "score": score,
        "level": level,
        "advice": ADVICE[level],
    }

# ---------- OUTPUT ----------
if __name__ == "__main__":
    raw = read_message()

    if not raw.strip():
        print("\nNo message entered. Please paste the message text and try again.")
    else:
        result = analyse(raw)

        print("\n==============================")
        print("Phishing risk:", str(result["score"]) + "%  (" + result["level"] + ")")
        print("==============================")
        print(result["advice"])

        for note in result["notes"]:
            print("\nNote:", note)

        print("\nFrom:   ", result["sender"] or "(not found)")
        print("Subject:", result["subject"] or "(not found)")
        print("Links found:", len(result["links"]))

        print("\nWarning signs found:", len(result["findings"]))
        number = 1
        for finding in result["findings"]:
            print("\n  " + str(number) + ". [" + str(round(finding["weight"] * 100)) + "%]", finding["reason"])
            print("     Why it matters:", finding["why"])
            number = number + 1
