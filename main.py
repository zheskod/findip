import logging
import ipaddress
import aiohttp
import io
from PIL import Image, ImageDraw, ImageFont
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

BOT_TOKEN = "8369028686:AAHtfct88TRx3KX4DQGA9sPWgaw27Anbp9g"
IP_API_URL = "http://ip-api.com/json"
YANDEX_MAPS_KEY = "05e04a7c-a39a-47b5-bdaf-246c496e8bf1"


def is_valid_ipv4(ip: str) -> bool:
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def format_ip_info(data: dict) -> str:
    if data.get("status") != "success":
        msg = data.get("message", "unknown error")
        return f"❌ Запрос к ip-api не удался: {msg}"

    parts = []

    query = data.get("query")
    if query:
        parts.append(f"🌐 *IP:* `{query}`")

    country = data.get("country")
    city = data.get("city")
    region = data.get("regionName")
    if any([country, region, city]):
        loc = ", ".join(x for x in [country, region, city] if x)
        parts.append(f"📍 *Локация:* {loc}")

    isp = data.get("isp")
    org = data.get("org")
    if isp or org:
        isp_org = ", ".join(x for x in [isp, org] if x)
        parts.append(f"📡 *Провайдер:* {isp_org}")

    as_name = data.get("as")
    if as_name:
        parts.append(f"🔗 *AS:* {as_name}")

    lat = data.get("lat")
    lon = data.get("lon")
    if lat is not None and lon is not None:
        parts.append(f"🗺️ *Координаты:* `{lat}, {lon}`")

    timezone = data.get("timezone")
    if timezone:
        parts.append(f"⏰ *Часовой пояс:* {timezone}")

    zip_code = data.get("zip")
    if zip_code:
        parts.append(f"📮 *Почтовый индекс:* {zip_code}")

    if not parts:
        return "ℹ️ Не удалось получить полезную информацию по этому IP."

    return "\n".join(parts)


async def generate_yandex_map(lat: float, lon: float) -> bytes:
    size = "400,300"
    zoom = 9
    theme = "dark"
    # Формат: долгота,широта,pm2rdm (красный круглый маркер)
    markers = f"{lon},{lat},pm2rdm"

    url = "https://static-maps.yandex.ru/1.x/"
    params = {
        "key": YANDEX_MAPS_KEY,
        "l": "map",  # обычная карта
        "size": size,
        "theme" : theme, # тема карты (светлая/темная)
        "z": zoom,
        "pt": markers  # метка
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                logger.info(f"Yandex статус: {resp.status}")
                if resp.status == 200:
                    image_data = await resp.read()
                    logger.info(f"✅ Yandex карта: {len(image_data)} байт")
                    return image_data
                else:
                    text = await resp.text()
                    logger.error(f"Yandex {resp.status}: {text}")
                    return create_map_fallback(lat, lon)
    except Exception as e:
        logger.error(f"Yandex ошибка: {e}")
        return create_map_fallback(lat, lon)


def create_map_fallback(lat: float, lon: float) -> bytes:
    """Резервная картинка Яндекс.Карты."""
    img = Image.new('RGB', (400, 300), color='#E3F2FD')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 24)
        except:
            font = ImageFont.load_default()

    draw.text((20, 40), "🗺️ Яндекс.Карты", fill='#1976D2', font=font)
    draw.text((20, 100), f"Широта: {lat:.4f}°", fill='#D32F2F', font=font)
    draw.text((20, 150), f"Долгота: {lon:.4f}°", fill='#D32F2F', font=font)
    draw.text((20, 210), "Красный маркер ↓", fill='#666', font=font)

    # Метка
    draw.ellipse([160, 240, 240, 280], fill='#F44336', outline='white', width=3)

    map_bytes = io.BytesIO()
    img.save(map_bytes, format='PNG')
    map_bytes.seek(0)
    return map_bytes.getvalue()


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
        "🔍 *IP Геолокатор с Яндекс.Картами*\n\n"
        "Введите IPv4-адрес в формате `x.x.x.x`\n\n",
        parse_mode='Markdown'
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    ip_str = text.strip()

    if ip_str == "":
        await update.message.reply_text(
            "Вы отправили пустое сообщение. Введите IPv4-адрес."
        )
        return

    if not is_valid_ipv4(ip_str):
        await update.message.reply_text(
            "❌ Это не похоже на корректный IPv4-адрес.\n"
            "Формат: x.x.x.x, где x от 0 до 255."
        )
        return

    processing_msg = await update.message.reply_text("🔄 Получаю данные и карту...")

    try:
        data = await call_ip_api(ip_str)
        info = format_ip_info(data)
        await processing_msg.edit_text(info, parse_mode='Markdown')

        # Яндекс карта при наличии координат
        lat = data.get("lat")
        lon = data.get("lon")
        if lat is not None and lon is not None:
            map_img = await generate_yandex_map(float(lat), float(lon))
            await update.message.reply_photo(
                photo=map_img,
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.exception("Ошибка обработки")
        await processing_msg.edit_text(f"Ошибка: {e}")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 IP Геолокатор с Яндекс.Картами запущен!")
    print("✅ Тест: 8.8.8.8")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
