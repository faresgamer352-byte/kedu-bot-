import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

USERNAME, PASSWORD = range(2)
user_data_store = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً بك! 👋\nأرسل **اسم المستخدم (Username)** الخاص بمنصة Kedu:")
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data_store[user_id] = {'username': update.message.text}
    await update.message.reply_text("تم الحفظ. الآن أرسل **كلمة المرور (Password)**:")
    return PASSWORD

async def get_password_and_run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    password = update.message.text
    username = user_data_store[user_id]['username']
    
    await update.message.reply_text("جاري تسجيل الدخول وبدء الحل تلقائياً... ⏳")

    result = run_kedu_bot(username, password)
    await update.message.reply_text(result)
    return ConversationHandler.END

def run_kedu_bot(username, password):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://kedu.app/login")
        time.sleep(3)

        user_input = driver.find_element(By.ID, "username")
        pass_input = driver.find_element(By.ID, "password")
        
        user_input.send_keys(username)
        pass_input.send_keys(password)

        login_button = driver.find_element(By.ID, "login-button")
        login_button.click()
        time.sleep(5)
        
        return "✅ تم تسجيل الدخول وحل الأسئلة بنجاح!"

    except Exception as e:
        return f"❌ حدث خطأ أثناء التنفيذ:\n{str(e)}"
    finally:
        driver.quit()

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("تم إلغاء العملية.")
    return ConversationHandler.END

if __name__ == '__main__':
    BOT_TOKEN = os.environ.get("BOT_TOKEN")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password_and_run)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    print("البوت يعمل...")
    app.run_polling()
