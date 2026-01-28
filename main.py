import logging
import ipaddress
import aiohttp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = ""
IP_API_URL = "http://ip-api.com/json"  # /{query}


def is_valid_ipv4(ip: str) -> bool:
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def format_ip_info(data: dict) -> str:
    if data.get("status") != "success":
        msg = data.get("message", "unknown error")
        return f"Запрос к ip-api не удался: {msg}"

    parts = []

    query = data.get("query")
    if query:
        parts.append(f"IP: {query}")

    country = data.get("country")
    city = data.get("city")
    region = data.get("regionName")
    if any([country, region, city]):
        loc = ", ".join(x for x in [country, region, city] if x)
        parts.append(f"Локация: {loc}")

    isp = data.get("isp")
    org = data.get("org")
    if isp or org:
        isp_org = ", ".join(x for x in [isp, org] if x)
        parts.append(f"Провайдер: {isp_org}")

    as_name = data.get("as")
    if as_name:
        parts.append(f"AS: {as_name}")

    lat = data.get("lat")
    lon = data.get("lon")
    if lat is not None and lon is not None:
        parts.append(f"Координаты: {lat}, {lon}")

    timezone = data.get("timezone")
    if timezone:
        parts.append(f"Часовой пояс: {timezone}")

    zip_code = data.get("zip")
    if zip_code:
        parts.append(f"Почтовый индекс: {zip_code}")

    if not parts:
        return "Не удалось получить полезную информацию по этому IP."

    return "\n".join(parts)


async def call_ip_api(ip: str) -> dict:
    url = f"{IP_API_URL}/{ip}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params={"lang": "ru"}) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"ip-api HTTP {resp.status}: {text}")
            return await resp.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите IPv4-адрес в формате x.x.x.x, где x от 0 до 255."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    ip_str = text.strip()

    if ip_str == "":
        await update.message.reply_text(
            "Вы отправили пустое сообщение. Введите IPv4-адрес в формате x.x.x.x."
        )
        return

    if not is_valid_ipv4(ip_str):
        await update.message.reply_text(
            "Это не похоже на корректный IPv4-адрес.\n"
            "Формат: x.x.x.x, где x от 0 до 255."
        )
        return

    try:
        data = await call_ip_api(ip_str)
        info = format_ip_info(data)
        await update.message.reply_text(info)
    except Exception as e:
        logger.exception("Ошибка при запросе ip-api")
        await update.message.reply_text(
            f"Произошла ошибка при запросе к ip-api: {e}"
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()


if __name__ == "__main__":
    main()
