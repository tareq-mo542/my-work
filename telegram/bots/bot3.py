import os
from rembg import remove
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

Token = "8130730306:AAFieLE5rAJeWHDk3cjRsmEBTZuzi_sshhI"
# إنشاء مجلد للملفات إذا لم يكن موجوداً
if not os.path.exists('./files'):
    os.makedirs('./files')
if not os.path.exists('./output'):
    os.makedirs('./output')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='هلا يا دمعة تفضل شو بقدر اساعدك\n\nأرسل لي صورة وأنا بزيل الخلفية! 📸'
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text='هلا بالخال ابعتلي الصورة اغلبك 🎨'
    )

async def process_image(photo_name):
    """دالة لإزالة الخلفية من الصورة"""
    input_path = f'./files/{photo_name}'
    output_path = f'./output/no_bg_{photo_name}'
    
    # إزالة الخلفية
    with open(input_path, 'rb') as inp:
        with open(output_path, 'wb') as out:
            input_data = inp.read()
            output_data = remove(input_data)
            out.write(output_data)
    
    # حذف الملف الأصلي
    os.remove(input_path)
    
    return output_path

async def handler_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دالة معالجة الصور"""
    try:
        # التحقق من نوع الملف
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            unique_file_id = update.message.photo[-1].file_unique_id
            photo_name = f"{unique_file_id}.jpg"
        
        elif update.message.document:
            file_id = update.message.document.file_id
            _, f_ext = os.path.splitext(update.message.document.file_name)
            unique_file_id = update.message.document.file_unique_id
            photo_name = f'{unique_file_id}{f_ext}'
        
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='أرسل صورة من فضلك! 📸'
            )
            return
        
        # تحميل الصورة
        photo_file = await context.bot.get_file(file_id)
        await photo_file.download_to_drive(custom_path=f'./files/{photo_name}')
        
        # إرسال رسالة الانتظار
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='ثواني وبتكون جاهزة يا زلمتي... ⏳'
        )
        
        # معالجة الصورة
        processed_path = await process_image(photo_name)
        
        # إرسال الصورة المعالجة
        with open(processed_path, 'rb') as photo:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=photo,
                filename=f'no_bg_{photo_name}'
            )
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='✅ تم إزالة الخلفية بنجاح!'
        )
        
        # حذف الملف المعالج
        os.remove(processed_path)
        
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'حدث خطأ: {str(e)}'
        )
        print(f"Error: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(Token).build()
    
    # Command handlers
    help_handler = CommandHandler('help', help_command)
    start_handler = CommandHandler('start', start)
    
    # Message handler - استخدم MessageHandler بدلاً من CommandHandler!
    message_handler = MessageHandler(filters.PHOTO | filters.Document.IMAGE, handler_message)
    
    application.add_handler(help_handler)
    application.add_handler(start_handler)
    application.add_handler(message_handler)
    
    print("🤖 البوت يعمل الآن...")
    application.run_polling()