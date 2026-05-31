import os
import asyncio
import logging
from typing import Optional

import aiohttp
import discord


logging.basicConfig(
    level=os.getenv("DISCORD_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "").strip()
GATEWAY_TOKEN = os.getenv("GATEWAY_TOKEN") or os.getenv("API_SERVER_KEY", "")
API_SERVER_PORT = os.getenv("API_SERVER_PORT", "8642")
HERMES_API_URL = os.getenv(
    "DISCORD_HERMES_API_URL",
    f"http://127.0.0.1:{API_SERVER_PORT}/v1/chat/completions",
)

COMMAND_PREFIX = os.getenv("DISCORD_COMMAND_PREFIX", "!hm").strip()
MODEL_NAME = os.getenv("DISCORD_HERMES_MODEL", os.getenv("LLM_MODEL", "hermes"))
MAX_TOKENS = int(os.getenv("DISCORD_MAX_TOKENS", "1200"))

ALLOWED_CHANNELS = {
    item.strip()
    for item in os.getenv("DISCORD_ALLOWED_CHANNELS", "").split(",")
    if item.strip()
}

ALLOWED_USERS = {
    item.strip()
    for item in os.getenv("DISCORD_ALLOWED_USERS", "").split(",")
    if item.strip()
}


def is_allowed(message: discord.Message) -> bool:
    if message.author.bot:
        return False

    if ALLOWED_USERS and str(message.author.id) not in ALLOWED_USERS:
        return False

    # DM 沒有 channel allowlist 問題
    if isinstance(message.channel, discord.DMChannel):
        return True

    if ALLOWED_CHANNELS and str(message.channel.id) not in ALLOWED_CHANNELS:
        return False

    return True


def extract_prompt(message: discord.Message, bot_user: discord.ClientUser) -> Optional[str]:
    content = (message.content or "").strip()

    mention_1 = f"<@{bot_user.id}>"
    mention_2 = f"<@!{bot_user.id}>"

    if content.startswith(COMMAND_PREFIX):
        return content[len(COMMAND_PREFIX):].strip()

    if content.startswith(mention_1):
        return content[len(mention_1):].strip()

    if content.startswith(mention_2):
        return content[len(mention_2):].strip()

    # DM 裡可以直接講話
    if isinstance(message.channel, discord.DMChannel):
        return content

    return None


async def ask_hermes(prompt: str, username: str) -> str:
    if not GATEWAY_TOKEN:
        return "HuggingMes 還沒有設定 GATEWAY_TOKEN，Discord Bot 無法呼叫 Hermes API。"

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Hermes Agent connected to Discord. "
                    "Reply clearly and helpfully. Keep answers concise unless the user asks for details."
                ),
            },
            {
                "role": "user",
                "content": f"Discord user {username} says:\n{prompt}",
            },
        ],
        "max_tokens": MAX_TOKENS,
    }

    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json",
    }

    timeout = aiohttp.ClientTimeout(total=180)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(HERMES_API_URL, headers=headers, json=payload) as resp:
            text = await resp.text()

            if resp.status >= 400:
                logging.error("Hermes API error %s: %s", resp.status, text[:1000])
                return f"Hermes API 回傳錯誤：HTTP {resp.status}"

            data = await resp.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        logging.exception("Unexpected Hermes API response: %s", data)
        return "Hermes API 有回應，但格式不是預期的 OpenAI chat completions 格式。"


async def send_long_message(destination, text: str):
    # Discord 單則訊息上限約 2000 字，保守切 1800
    chunks = []
    while text:
        chunks.append(text[:1800])
        text = text[1800:]

    for chunk in chunks:
        await destination.send(chunk)


class HermesDiscordClient(discord.Client):
    async def on_ready(self):
        logging.info("Discord bot logged in as %s", self.user)

    async def on_message(self, message: discord.Message):
        if not self.user:
            return

        if not is_allowed(message):
            return

        prompt = extract_prompt(message, self.user)
        if not prompt:
            return

        async with message.channel.typing():
            reply = await ask_hermes(prompt, str(message.author))

        await send_long_message(message.channel, reply)


async def main():
    if not DISCORD_BOT_TOKEN:
        logging.info("DISCORD_BOT_TOKEN not set; Discord bot disabled.")
        return

    intents = discord.Intents.default()

    # 若你要用 !hm 指令讀取頻道文字，Discord Developer Portal 也要開 Message Content Intent。
    intents.message_content = os.getenv("DISCORD_MESSAGE_CONTENT_INTENT", "true").lower() == "true"

    client = HermesDiscordClient(intents=intents)
    await client.start(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
