import requests
import os
import sys

# جلب المفاتيح من نظام GitHub Secrets (أكثر أماناً)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FB_TOKEN = os.getenv("FB_TOKEN")
PAGE_ID = "me" 

def solve_and_post():
    try:
        # 1. اكتشاف الموديل المتاح
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        response = requests.get(list_url)
        models_data = response.json()
        
        available_models = [m['name'] for m in models_data.get('models', [])
                           if 'generateContent' in m.get('supportedGenerationMethods', [])]

        if not available_models:
            print("❌ لا يوجد موديل مفعل.")
            return

        target_model = available_models[0]
        
        # 2. توليد النص + الهاشتاجات + الكلمات المفتاحية
        gen_url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={GEMINI_API_KEY}"
        
                # تعديل البرومبت ليركز على الترند المغربي
        prompt = (
            "أنت خبير في السوشيال ميديا المغربية. "
            "أولاً: حدد موضوعاً واحداً رائجاً (Trend) في المغرب اليوم (أخبار، رياضة، فن، أو مناسبة وطنية/دينية). "
            "ثانياً: اكتب منشور فيسبوك تفاعلي بلهجة مغربية بيضاء (مفهومة) أو لغة عربية سليمة حسب طبيعة الموضوع. "
            "ثالثاً: أضف هاشتاجات مغربية رائجة مثل #المغرب #Maroc وهاشتاجات متعلقة بالموضوع. "
            "رابعاً: وجه سؤالاً للجمهور المغربي للتفاعل. "
            "وفي السطر الأخير اكتب 'Keywords:' متبوعة بـ 3 كلمات إنجليزية للبحث عن صورة تناسب هذا الترند."
        )
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        res = requests.post(gen_url, json=payload).json()
        full_response = res['candidates'][0]['content']['parts'][0]['text']
        
        # فصل النص عن كلمات البحث
        if "Keywords:" in full_response:
            post_text, keywords = full_response.split("Keywords:")
            keywords = keywords.strip().replace(" ", ",")
        else:
            post_text, keywords = full_response, "islamic,ramadan"

        # 3. جلب الصورة التلقائية
        image_url = f"https://loremflickr.com/1080/1080/{keywords}/all"

        # 4. النشر على فيسبوك
        fb_url = f"https://graph.facebook.com/v21.0/{PAGE_ID}/photos"
        fb_payload = {
            'url': image_url,
            'caption': post_text.strip(),
            'access_token': FB_TOKEN
        }
        
        fb_res = requests.post(fb_url, data=fb_payload).json()

        if 'id' in fb_res:
            print(f"✅ تم النشر بنجاح!")
        else:
            print(f"❌ خطأ فيسبوك: {fb_res}")

    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")

if __name__ == "__main__":
    solve_and_post()
