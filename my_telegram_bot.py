import os
import logging
import requests
from bs4 import BeautifulSoup
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Конфигурация API ключа OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')  # Убедитесь, что у вас установлена эта переменная окружения
client = openai.OpenAI()  # Создание клиента OpenAI

def fetch_article(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('article')
        return article.text if article else "Статья не найдена"
    except requests.RequestException as e:
        logging.error(f"Ошибка при получении статьи: {str(e)}")
        return f"Ошибка при получении статьи: {str(e)}"

def rewrite_article(article_text):
    try:
        response = client.completions.create(
            model="text-davinci-003",
            prompt="Переформулируйте следующий текст: " + article_text,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Ошибка при рерайтинге статьи: {str(e)}")
        return f"Ошибка при рерайтинге статьи: {str(e)}"

async def send_rewritten_article(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = 'https://colorflowers.ru/a-vy-uzhe-gotovy-k-8-marta/'
    logging.info(f"Handling /send_article command for URL: {url}")
    original_article = fetch_article(url)
    rewritten_article = rewrite_article(original_article)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=rewritten_article)

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logging.error("Токен не установлен. Проверьте переменную окружения TELEGRAM_BOT_TOKEN.")
        return
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("send_article", send_rewritten_article))
    application.run_polling()

if __name__ == '__main__':
    main()
