# 🤖 IP Геолокатор для Telegram

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-purple.svg)](https://core.telegram.org/bots)
[![License](https://img.shields.io/github/license/yourusername/ip-geolocator-bot.svg)](LICENSE)

**Telegram бот для получения геолокации по IPv4 адресу с картой Яндекс.Карты**

## ✨ **Демо**

![Демо бота](screenshots/demo.jpg)
*Введите IP → Получите локацию + карту*

## 🚀 **Функции**

- ✅ **Валидация IPv4** адресов
- 🌐 **ip-api.com** — бесплатная геолокация
- 🗺️ **Яндекс.Карты Static API** — красный маркер на карте
- 💎 **Markdown** форматирование
- 🛡️ **Обработка ошибок** + fallback
- ⚡ **Асинхронный** `python-telegram-bot v20+`

## 🛠️ **Установка**

```bash
# Клонировать репозиторий
git clone https://github.com/YOUR_USERNAME/ip-geolocator-bot.git
cd ip-geolocator-bot

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установить зависимости
pip install -r requirements.txt

⚙️ Конфигурация

    Создай своего бота через @BotFather

    Скопируй токен и замени в bot.py:

    python
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

    Яндекс.Карты ключ (опционально):

    python
    YANDEX_MAPS_KEY = "your_yandex_key_here"

▶️ Запуск

bash
python bot.py

Бот готов! Отправь /start в Telegram.
📁 Структура проекта

text
ip-geolocator-bot/
├── bot.py              # Основной код бота
├── requirements.txt    # Зависимости
├── README.md          # Документация
├── screenshots/        # Скриншоты
│   └── demo.png
└── LICENSE            # Лицензия

🔧 Настройки Яндекс.Карты

    Zoom: 9 (глобальный вид)

    Размер: 400x300

    Маркер: pm2rdm (красный круг)

    Тема: dark (тёмная карта)

🐳 Docker (опционально)

text
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]

bash
docker build -t ip-geolocator-bot .
docker run ip-geolocator-bot

⚠️ Лимиты сервисов
Сервис	Лимит	Статус
ip-api.com	45 req/мин	✅ Бесплатно
Яндекс.Карты	По тарифу	🔑 Требует ключ
📈 Roadmap

    Базовый IP геолокатор

    Яндекс.Карты интеграция

    Rate limiting

    База данных логов

    Webhook deploy

    Inline режим

🤝 Контакты

    Автор: Твой GitHub

    Telegram: @yourusername

📄 Лицензия

MIT License © 2026

⭐ Поставь звезду, если бот понравился!

text

### 3. **Структура репозитория**

ip-geolocator-bot/
├── bot.py
├── requirements.txt
├── README.md
├── screenshots/
│ └── demo.png
├── .gitignore
└── LICENSE

text

### 4. **.gitignore**

Byte-compiled / optimized files

pycache/
*.py[cod]
*$py.class
Environment variables

.env
*.env
Logs

logs/
*.log
Virtual environment

venv/
env/
IDE

.vscode/
.idea/

text

### 5. **LICENSE** (MIT)

MIT License

Copyright (c) 2026 YOUR_USERNAME

Permission is hereby granted, free of charge, to any person obtaining a copy...

text

### 6. **Команды для GitHub**

```bash
# 1. Инициализация
git init
git add .
git commit -m "Initial: IP Geolocator Telegram Bot with Yandex Maps"

# 2. Создай репозиторий на GitHub и:
git remote add origin https://github.com/YOUR_USERNAME/ip-geolocator-bot.git
git branch -M main
git push -u origin main
