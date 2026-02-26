import os
import asyncio
import aiohttp
from datetime import datetime
import pytz

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

ASIA_KOLKATA = pytz.timezone("Asia/Kolkata")

WEBHOOK_NAME = "Core Platform API"
WEBHOOK_AVATAR = "https://yt3.googleusercontent.com/8SG9uDv2ITO754-r_Uoq4_nkuBBzY8iD6piQ6t85eEANlA9v-9jTE9VFJ4YE2CkZftIQYlVM=s900-c-k-c0x00ffffff-no-rj"

API_COLOR = 3447003
AUDIT_COLOR = 15158332
NEW_DEVICE_COLOR = 16098851

BATCH_SIZE = 10
FLUSH_INTERVAL = 2

api_log_queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=5000)
audit_log_queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=2000)


def now_iso():
    return datetime.now(tz=ASIA_KOLKATA).isoformat()


def status_style(status_code: int):
    if 200 <= status_code < 300:
        return 5763719, "✅", "Success"
    if 300 <= status_code < 400:
        return 3447003, "🔁", "Redirect"
    if status_code in (401, 403):
        return 16776960, "🔒", "Unauthorized"
    if 400 <= status_code < 500:
        return 16753920, "⚠️", "Client Error"
    return 15548997, "💥", "Server Error"


async def enqueue_api_log(embed: dict):
    try:
        api_log_queue.put_nowait(embed)
    except asyncio.QueueFull:
        pass


async def enqueue_audit_log(embed: dict):
    try:
        audit_log_queue.put_nowait(embed)
    except asyncio.QueueFull:
        pass


def build_api_embed(
    method: str,
    path: str,
    status: int,
    device_id: str | None,
    ip: str | None,
    user_id: str | None,
    latency_ms: float | None = None,
    trace_id=None,
):
    color, emoji, label = status_style(status)

    fields = [
        {"name": "Method", "value": method, "inline": True},
        {"name": "Status", "value": f"{status} ({label})", "inline": True},
        {"name": "User", "value": user_id or "anonymous", "inline": False},
        {"name": "Endpoint", "value": path, "inline": False},
        {"name": "Device", "value": device_id or "unknown", "inline": True},
        {"name": "IP Address", "value": ip or "unknown", "inline": True},
        {"name": "Trace ID", "value": trace_id or "unknown", "inline": True},
    ]

    if latency_ms is not None:
        fields.append(
            {"name": "Latency", "value": f"{latency_ms:.2f} ms", "inline": True}
        )

    return {
        "title": f"{emoji} API Request",
        "color": color,
        "fields": fields,
        "timestamp": now_iso(),
    }


def build_audit_embed(
    action: str,
    method: str,
    path: str,
    device_id: str | None,
    ip: str | None,
    user_id: str | None,
    trace_id: None
):
    return {
        "title": f"🚨 Security Event - {action}",
        "color": AUDIT_COLOR,
        "fields": [
            {"name": "Method", "value": method, "inline": True},
            {"name": "User", "value": user_id or "anonymous", "inline": True},
            {"name": "Endpoint", "value": path, "inline": False},
            {"name": "Device", "value": device_id or "unknown", "inline": True},
            {"name": "IP Address", "value": ip or "unknown", "inline": True},
            {"name": "Trace ID", "value": trace_id or "unknown", "inline": True},
        ],
        "timestamp": now_iso(),
    }


def build_new_device_embed(user_id: str, device_id: str, ip: str | None, trace_id: str | None = None):
    return {
        "title": "🆕 New Device Login Detected",
        "color": NEW_DEVICE_COLOR,
        "fields": [
            {"name": "User", "value": user_id, "inline": False},
            {"name": "Device ID", "value": device_id, "inline": True},
            {"name": "IP Address", "value": ip or "unknown", "inline": True},
            {"name": "Trace ID", "value": trace_id or "unknown", "inline": True},
        ],
        "timestamp": now_iso(),
    }


async def _worker(queue: asyncio.Queue[dict]):
    if not DISCORD_WEBHOOK_URL:
        print("Discord webhook missing")
        return

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            embeds = []

            try:
                item = await asyncio.wait_for(
                    queue.get(),
                    timeout=FLUSH_INTERVAL,
                )
                embeds.append(item)
            except asyncio.TimeoutError:
                pass

            while not queue.empty() and len(embeds) < BATCH_SIZE:
                embeds.append(queue.get_nowait())

            if not embeds:
                continue

            payload = {
                "username": WEBHOOK_NAME,
                "avatar_url": WEBHOOK_AVATAR,
                "embeds": embeds[:10],
            }

            try:
                async with session.post(
                    DISCORD_WEBHOOK_URL,
                    json=payload,
                ) as resp:
                    if resp.status >= 400:
                        print(f"Discord webhook error: {resp.status}")
            except Exception:
                pass


async def api_log_worker():
    await _worker(api_log_queue)


async def audit_log_worker():
    await _worker(audit_log_queue)