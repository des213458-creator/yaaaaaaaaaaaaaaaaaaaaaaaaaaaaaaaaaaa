# Render M3U8 Telegram Bot (N_m3u8DL-RE)

هذا المشروع مُهيأ للنشر على Render.com ويستخدم دائمًا N_m3u8DL-RE لتحميل .m3u8 ثم يرسل الفيديو إلى Telegram.

## خطوات النشر السريعة (مبتدئين)
1. ادفع (push) هذا المجلد إلى GitHub في مستودع جديد.
2. افتح https://render.com وسجّل الدخول بواسطة GitHub.
3. اضغط New → Web Service → اختر المستودع.
4. عند الإعدادات ضع:
   - Build Command: `bash install.sh`
   - Start Command: `python bot.py`
5. بعد الإنشاء، أضف Environment Variables في صفحة الخدمة:
   - `BOT_TOKEN` = (التوكن من BotFather)
6. اضغط Deploy (أو Manual Deploy بعد حفظ المتغيرات).
7. افتح البوت في Telegram وجرب `/start` ثم `/download <link>.m3u8`

ملاحظات:
- إذا كانت الملفات كبيرة جدًا، قد يفشل رفعها إلى Telegram بسبب حدود الحجم.
- إذا لم يجد install.sh ملف N تلقائيًا، يمكنك رفع ملف `N_m3u8DL-RE` يدوياً إلى جذر الريبو عبر GitHub (Add file → Upload files).
