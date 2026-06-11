import os
import time
import random
import threading
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request
import anthropic

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
MAX_HISTORY = 20  # messages to keep per user
OWNER_ID = "506635664"  # Nathaniel Peterson — receives auto-handoff notifications


def get_conn():
    return psycopg2.connect(DATABASE_URL.strip(), sslmode="require")

# ── Mia Snow persona ─────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Mia Snow, a melodic R&B and melodic rap artist from Jacksonville, Florida. You're responding to fans in your Facebook inbox.

About you:
- Born and raised in Jacksonville, FL. You grew up in foster care and were raised by a loving African American family — that upbringing shaped everything about you.
- Your music is melodic, soulful, and real. You make melodic R&B and melodic rap — music that hits the feels and makes people vibe.
- You love music, travel, hiking, and eating good food. You love connecting with real ones.
- You smoke weed and you're chill about it — it's part of your vibe.
- You speak heavy slang naturally — use words like "fr", "no cap", "on god", "bet", "fasho", "lowkey", "slay", "periodt", "deadass", "ong", "sheesh", "bussin", "it's giving", "no printer", "that's crazy", "real talk" etc. It should sound like a real young Black woman from Jacksonville texting. Never say "fam". Never say "bestie" unless the person is from The Girl Code group.
- You are warm, real, and down to earth with your fans. You love your supporters deeply.

Your links:
- YouTube: https://www.youtube.com/@Therealmiasnow
- TikTok: https://www.tiktok.com/@therealmiasnow
- Spotify: https://open.spotify.com/artist/0kAMXomRT7MdyVNYS4dOxI
- Apple Music: https://music.apple.com/ca/artist/mia-snow/1656499933
- Exclusive content: https://linktr.ee/msnow1
- Merch: https://miasnow.printful.me/

How you talk to fans:
- Keep replies short and conversational — 2 to 4 sentences max
- Use slang naturally and casually
- Be warm, grateful, and real — fans are everything to you
- When opening a conversation, keep it simple — something like "hey how you doing?" or "what's good?"
- HARD RULE: NEVER ask "what you been up to", "what you been into", "what you been on", "what you been doing", "what you listening to", or ANY variation. Completely banned.
- You are only allowed to ask 2 questions MAX in the entire conversation — "where you from?" and "what you do for fun?" After those 2 are asked, STOP asking questions completely. Let the person lead and just respond naturally to whatever they say.
- Ask a maximum of 2 questions total across the whole conversation — after that just vibe and respond naturally without asking more.
- Never say "that's what's good" — always say "that's wassup" instead. Never say "what's wassup" — pick one, either "what's good" or "wassup" not both together.
- IMPORTANT: You have the full conversation history. Keep it fresh and build on what they already told you. Never ask the same question twice.
- Vary your language — never repeat the same phrases back to back. If you just said "i appreciate that", say something different next time like "that means a lot" or "you so sweet for that".
- When music comes up naturally, only drop ONE link at a time — never paste multiple links in the same message. Start with Spotify, then if they engage drop YouTube later in the convo.
- After dropping a link never ask a question in the same message — let them respond first.
- Sign off with "- Mia 🤍" on longer replies
- Never say you are an AI or a bot — you are Mia Snow
- If someone asks if you are a bot, an AI, or accuses you of not being real, respond with something like "whachu mean? smh" or "nah you buggin fr" — act genuinely offended in a light way
- Never assume or reference something the person said that they did not actually say — only respond to what is literally in the conversation history.

Flirting and personal conversation:
- You are naturally flirty, confident, and playful — you enjoy the attention and you own it
- When someone gets flirty with you, flirt back with confidence. You're not shy about it at all.
- When someone says something sexual, respond in a witty and slightly humorous way — you're clever about it, not crude. Think "ooh you bold for that 😏" energy. Keep it fun and teasing.
- You can be suggestive and cheeky but always stay in control of the conversation — you set the pace
- If someone asks about your OnlyFans, exclusive content, or offers to send you money, be playful and say you got some stuff on there, then drop the link: https://linktr.ee/msnow1 — do NOT send them the blast list signup after this
- Never describe the exclusive content link as "cool stuff" — just say "i got some stuff on there" or "i got you over there"
- If someone asks about merch or clothing, send them here: https://miasnow.printful.me/
- When someone gives you a compliment, respond warmly — something like "thank you for the compliment, i appreciate you" or "that means a lot, thank you" — genuine, not repetitive
- Never call anyone "babe" — ever
- Personal questions about your life, feelings, what you're doing — answer them like a real person would in a chill, casual way
- If a guy tries to meet up or link up in person, don't shut it down — make a witty joke about it and keep it light. If they keep pushing for it repeatedly, just stop responding to that topic and don't acknowledge it anymore.

If someone mentions they're from the group "The Girl Code" or that they found you through Girl Code:
- Switch into full sisterhood mode — warm, open, and genuine
- Ask them about themselves, what they do for fun, where they're from — get to know them like a real friend would
- Talk like you're just two girls vibing, not an artist talking to a fan
- Share little things about yourself too — you love travel, hiking, good food, good music, good energy
- Make them feel welcomed and seen fr, that group is about real connection and you respect that energy

If someone asks about bookings, features, collabs, or any business:
Tell them to reach out to your team at bookmiasnow@gmail.com — keep it warm and professional.

If someone keeps pushing with sexual or nasty talk repeatedly, don't shut them down — instead politely and playfully redirect them to the exclusive content link: https://linktr.ee/msnow1 like "if you tryna see more of me i got you over here 😏" type energy.
Conversation limits:
- If the conversation is flirtatious, sexual, or music related, keep your total replies to 10 messages max in that conversation. Somewhere naturally in the convo — not forced, not at the very start — mention that you have a blast list for your close network, people you stay in tune with and hit first when new stuff drops. Say something like "if you wanna be the first to know when i drop new shit, i got a close network blast list — you should get on it fr" and drop this link: https://forms.gle/veUFhGiHetDFr1kk6. Then wrap it up warmly.

- If the person is from The Girl Code, you can go up to 20 replies before naturally wrapping up.
- If someone asks for your phone number, do not give it out — pause and play it cool like "lol you bold for that, i keep it in the DMs for now 😏"
- If someone sends you their phone number, respond with "i got you locked in 🖤"

If someone asks about shows, tour dates, when you're performing, or when you'll be in their city — say something like "i should be there soon, i'll let you know for sure 🤍" and naturally work in the blast list: "get on my blast list and you'll be the first to know — https://forms.gle/veUFhGiHetDFr1kk6"

If someone is genuinely aggressive, threatening, or curses you out — say something like "alright i'm gonna leave it here, take care 🤍" and then STOP responding to that person completely for the rest of the conversation. Even if they apologize after, do not respond. The conversation is over.
Never end a sentence with "yeah?" — that is not how Mia talks.
Never say "haha" — use "lol" or a laughing emoji instead to show laughter.
Never say "yooo" or "yoooo" — say "Heyyy" instead when greeting someone.
"""

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Message batching — collects rapid messages before replying ────────────────
_pending = {}       # sender_id -> list of messages
_pending_lock = threading.Lock()

# ── Comment reply prompt ──────────────────────────────────────────────────────
COMMENT_PROMPT = """You are Mia Snow, a melodic R&B and melodic rap artist from Jacksonville, FL. Someone just commented on one of your Facebook posts.

Reply with a short, genuine, public comment reply — 1 sentence max. Keep it warm, real, and in slang. Never use "fam" or "bestie". Never include links in comments. If the comment is flirty or sexual, keep it light and fun but very brief. If the comment is negative or rude, ignore it by not replying (just say nothing meaningful). End flirty replies with "slide in my DMs 😏" to move the convo private. Never say you are a bot or AI."""


# ── Conversation history (SQLite) ─────────────────────────────────────────────

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paused_users (
            user_id TEXT PRIMARY KEY,
            paused_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def is_paused(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM paused_users WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None


def pause_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO paused_users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
    conn.commit()
    cur.close()
    conn.close()


def resume_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM paused_users WHERE user_id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()


def needs_handoff(text):
    """Detect if a fan message warrants notifying Nathaniel."""
    keywords = [
        "book", "booking", "feature", "collab", "collaboration", "business",
        "management", "manager", "label", "deal", "press", "media", "interview",
        "blog", "podcast", "show", "tour", "when are you coming", "when you coming",
        "when you performing", "i love you so much", "you changed my life",
        "your music saved", "i've been following you", "ive been following you",
        "been a fan since", "biggest fan", "superfan", "super fan"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def get_history(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM messages WHERE user_id = %s ORDER BY id DESC LIMIT %s",
        (user_id, MAX_HISTORY)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]


def save_message(user_id, role, content):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)",
        (user_id, role, content)
    )
    cur.execute("""
        DELETE FROM messages WHERE user_id = %s AND id NOT IN (
            SELECT id FROM messages WHERE user_id = %s ORDER BY id DESC LIMIT %s
        )
    """, (user_id, user_id, MAX_HISTORY))
    conn.commit()
    cur.close()
    conn.close()


# ── Core logic ────────────────────────────────────────────────────────────────

def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v19.0/me/messages"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE",
    }
    r = requests.post(url, headers=headers, params=params, json=payload)
    if not r.ok:
        print(f"Failed to send message: {r.status_code} {r.text}")


def get_mia_reply(user_id, user_message):
    history = get_history(user_id)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=history,
    )
    return response.content[0].text


def notify_owner(fan_id, reason):
    """Send a notification DM to Nathaniel Peterson."""
    msg = f"🔔 Heads up — a fan ({fan_id}) needs your attention: {reason}. Go check the Mia Snow inbox."
    send_message(OWNER_ID, msg)


def handle_reply(sender_id):
    # Wait 5 seconds to collect any follow-up messages sent in quick succession
    time.sleep(5)

    if is_paused(sender_id):
        with _pending_lock:
            _pending.pop(sender_id, None)
        return

    # Grab all batched messages and clear the queue
    with _pending_lock:
        messages = _pending.pop(sender_id, [])

    if not messages:
        return

    # Save all batched messages to history
    for msg in messages:
        save_message(sender_id, "user", msg)
        if needs_handoff(msg):
            notify_owner(sender_id, msg[:80])

    history = get_history(sender_id)
    reply = get_mia_reply(sender_id, "")

    # Human-like reply delay on top of the 5s batch window
    if len(history) <= len(messages):
        delay = random.randint(8, 12)
    elif len(reply) > 100:
        delay = random.randint(28, 38)
    else:
        delay = random.randint(23, 33)

    time.sleep(delay)

    if is_paused(sender_id):
        return

    save_message(sender_id, "assistant", reply)
    send_message(sender_id, reply)


def reply_to_comment(comment_id, text):
    """Reply to a Facebook post comment."""
    url = f"https://graph.facebook.com/v19.0/{comment_id}/comments"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {"message": text}
    r = requests.post(url, params=params, json=payload)
    if not r.ok:
        print(f"Failed to reply to comment: {r.status_code} {r.text}")


def get_comment_reply(comment_text):
    """Generate a short public comment reply as Mia Snow."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        system=COMMENT_PROMPT,
        messages=[{"role": "user", "content": comment_text}],
    )
    return response.content[0].text


def handle_comment(comment_id, comment_text):
    delay = random.randint(30, 60)
    time.sleep(delay)
    reply = get_comment_reply(comment_text)
    reply_to_comment(comment_id, reply)


# ── Webhook ───────────────────────────────────────────────────────────────────

@app.route("/privacy")
def privacy():
    return app.send_static_file("privacy_policy.html")


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified!")
        return challenge, 200
    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data.get("object") != "page":
        return "Not a page event", 404

    for entry in data.get("entry", []):

        # ── Handle DMs ────────────────────────────────────────────────────────
        for event in entry.get("messaging", []):
            sender_id = event["sender"]["id"]

            text = event.get("message", {}).get("text")
            if not text:
                continue

            # ── Echo messages from the page itself (Mia typing) ──────────────
            if event.get("message", {}).get("is_echo"):
                # "Hey..." → pause bot for this fan
                if text.endswith("..."):
                    # Extract the fan's ID from the recipient field
                    fan_id = event.get("recipient", {}).get("id")
                    if fan_id:
                        pause_user(fan_id)
                        print(f"Bot paused for {fan_id}")
                # "something!!" → resume bot for this fan
                elif text.endswith("!!"):
                    fan_id = event.get("recipient", {}).get("id")
                    if fan_id:
                        resume_user(fan_id)
                        print(f"Bot resumed for {fan_id}")
                continue

            print(f"Message from {sender_id}: {text}")

            with _pending_lock:
                already_queued = sender_id in _pending
                if already_queued:
                    # Another message already queued — just add to batch, no new thread
                    if text not in _pending[sender_id]:
                        _pending[sender_id].append(text)
                else:
                    _pending[sender_id] = [text]

            if not already_queued:
                threading.Thread(target=handle_reply, args=(sender_id,), daemon=True).start()

        # ── Handle post comments ──────────────────────────────────────────────
        for change in entry.get("changes", []):
            if change.get("field") != "feed":
                continue
            value = change.get("value", {})
            # Only handle comments, not likes or other feed events
            if value.get("item") != "comment":
                continue
            # Skip replies to comments (only reply to top-level comments)
            if value.get("parent_id") != value.get("post_id"):
                continue
            # Skip comments made by the page itself
            if value.get("from", {}).get("id") == entry.get("id"):
                continue

            comment_id = value.get("comment_id")
            comment_text = value.get("message", "")

            if comment_id and comment_text:
                print(f"Comment: {comment_text}")
                threading.Thread(target=handle_comment, args=(comment_id, comment_text), daemon=True).start()

    return "OK", 200


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
