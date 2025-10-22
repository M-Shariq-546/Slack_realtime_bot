import os
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI

# Enable debug logging
logging.basicConfig(level=logging.INFO)

# --- Environment setup ---
SLACK_BOT_TOKEN = "slack-bot-token"  # replace with your Slack Bot Token
SLACK_APP_TOKEN = "slack-app-token"  # replace with your Slack App Token
OPENAI_API_KEY = "your_openai_key"  # replace with your OpenAI key

# Initialize Slack and OpenAI clients
app = App(token=SLACK_BOT_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


# --- Helper function ---
def get_ai_reply(user_text: str) -> str:
    """Generate a reply using OpenAI or fallback to simple logic."""
    if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-your-"):
        # Simple fallback response if OpenAI not set up
        if "hello" in user_text.lower():
            return "Hey there! 👋 How can I help you today?"
        elif "bye" in user_text.lower():
            return "Goodbye! Have a great day 😊"
        else:
            return "I'm here and listening, tell me more!"
    else:
        # Use OpenAI API
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful, friendly Slack chatbot."},
                    {"role": "user", "content": user_text},
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            return "Sorry, I'm having trouble connecting to my brain right now 🤖."


# --- Handle direct messages ---
@app.event("message")
def handle_message_events(event, say, logger):
    user = event.get("user")
    text = event.get("text", "")

    # Ignore bot's own messages
    if not user or "bot_id" in event:
        return

    logger.info(f"Received DM or channel message from {user}: {text}")
    reply = get_ai_reply(text)
    say(reply)


# --- Handle mentions in channels ---
@app.event("app_mention")
def handle_app_mention(event, say, logger):
    user = event.get("user")
    text = event.get("text", "")

    logger.info(f"Bot was mentioned by {user}: {text}")
    reply = get_ai_reply(text)
    say(reply)


# --- Run app ---
if __name__ == "__main__":
    logging.info("🚀 Starting Slack chatbot...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()