import os
from PIL import Image, ImageEnhance, ImageFilter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from rembg import remove
from io import BytesIO

TOKEN = "8182435669:AAFVvyFkX5NAe5O6p-ZbLQljkFAVOSO-F7c"

# إنشاء المجلدات
os.makedirs('./temp', exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً! أنا بوت تعديل الصور 🎨\n\n"
        "أرسل لي صورة واختر التعديل الذي تريده!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """حفظ الصورة وإظهار خيارات التعديل"""
    
    # تحميل الصورة
    photo = await update.message.photo[-1].get_file()
    photo_bytes = await photo.download_as_bytearray()
    
    # حفظ الصورة في الذاكرة
    context.user_data['photo'] = photo_bytes
    
    # إنشاء أزرار الخيارات
    keyboard = [
        [InlineKeyboardButton("🎭 إزالة الخلفية", callback_data='remove_bg')],
        [InlineKeyboardButton("⚫ أبيض وأسود", callback_data='grayscale')],
        [InlineKeyboardButton("🔄 قلب الصورة", callback_data='flip')],
        [InlineKeyboardButton("🔆 زيادة السطوع", callback_data='brightness')],
        [InlineKeyboardButton("🖼️ تصغير الحجم", callback_data='resize')],
        [InlineKeyboardButton("🌫️ طمس (Blur)", callback_data='blur')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "اختر التعديل الذي تريده:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة اختيار المستخدم"""
    query = update.callback_query
    await query.answer()
    
    # الحصول على الصورة من الذاكرة
    photo_bytes = context.user_data.get('photo')
    if not photo_bytes:
        await query.message.reply_text("❌ الصورة منتهية، أرسل صورة جديدة")
        return
    
    await query.message.reply_text("جاري المعالجة... ⏳")
    
    try:
        # فتح الصورة
        img = Image.open(BytesIO(photo_bytes))
        
        # تطبيق التعديل حسب الاختيار
        if query.data == 'remove_bg':
            # إزالة الخلفية
            output = remove(photo_bytes)
            output_img = Image.open(BytesIO(output))
            
        elif query.data == 'grayscale':
            # أبيض وأسود
            output_img = img.convert('L')
            
        elif query.data == 'flip':
            # قلب الصورة
            output_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            
        elif query.data == 'brightness':
            # زيادة السطوع
            enhancer = ImageEnhance.Brightness(img)
            output_img = enhancer.enhance(1.5)
            
        elif query.data == 'resize':
            # تصغير الحجم إلى النصف
            new_size = (img.width // 2, img.height // 2)
            output_img = img.resize(new_size, Image.Resampling.LANCZOS)
            
        elif query.data == 'blur':
            # طمس
            output_img = img.filter(ImageFilter.GaussianBlur(radius=5))
        
        # حفظ الصورة المعدلة
        output_buffer = BytesIO()
        output_img.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        # إرسال الصورة
        await query.message.reply_photo(
            photo=output_buffer,
            caption="✅ تم التعديل بنجاح!"
        )
        
    except Exception as e:
        await query.message.reply_text(f"❌ حدث خطأ: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 بوت تعديل الصور يعمل...")
    app.run_polling()