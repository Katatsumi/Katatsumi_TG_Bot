import os
import time
import glob
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
load_dotenv()
# Настройки бота
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("BOT_TOKEN not found in .env file")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Папка загрузки файлов
DOWNLOAD_FOLDER =  os.getenv('DOWNLOAD_FOLDER') # Измените при необходимости

# Настройки Selenium
options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_FOLDER,  # Указание папки загрузки
    "download.prompt_for_download": False,  # Отключение подтверждений
    "safebrowsing.enabled": True
})
options.add_argument("--headless")  # Запуск без GUI
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Отправь мне ссылку на плейлист Spotify, и я попробую скачать его для тебя.")

@dp.message_handler(lambda message: message.text.startswith("https://open.spotify.com/playlist/"))
async def download_spotify_playlist(message: types.Message):
    playlist_url = message.text
    await message.answer("Скачиваю плейлист, подождите...")

    try:
        # Запуск браузера
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://example_download_service.com")

        # Ожидание загрузки страницы
        wait = WebDriverWait(driver, 10)
        input_field = wait.until(EC.presence_of_element_located((By.ID, "url-input")))
        input_field.send_keys(playlist_url)
        input_field.send_keys(Keys.RETURN)

        # Ожидание кнопки скачивания
        download_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "download-btn")))
        download_button.click()

        # Ждем загрузки файла
        time.sleep(15)  # Можно увеличить, если файлы скачиваются медленно

        driver.quit()

        # Поиск скачанных файлов
        files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*.mp3"))  # Ищем mp3-файлы
        if not files:
            await message.answer("Ошибка: не удалось найти скачанные файлы.")
            return

        # Отправка файлов
        for file_path in files:
            with open(file_path, "rb") as audio:
                await message.answer_document(audio)
            os.remove(file_path)  # Удаляем после отправки

    except Exception as e:
        await message.answer(f"Ошибка при скачивании: {e}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
