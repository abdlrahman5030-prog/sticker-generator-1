import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import barcode
from barcode.writer import ImageWriter
import io
import os
from PIL import Image

st.set_page_config(page_title="Sticker Pro Precision")

st.title("مولد الاستيكرات بالأبعاد الدقيقة")

# الإعدادات في الشريط الجانبي
export_format = st.sidebar.selectbox("صيغة التصدير", ["PDF", "CSV"])
layout = st.sidebar.radio("تنسيق الطباعة", ["استيكر واحد لكل صفحة", "تجميع A4 (توفير ورق)"])

uploaded_file = st.file_uploader("ارفع ملف الـ CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    if st.button("توليد الملف النهائي"):
        output = io.BytesIO()
        
        # مقاس الاستيكر بناءً على طلبك: 4.5 سم عرض × 3.8 سم ارتفاع
        width, height = 4.5 * cm, 3.8 * cm
        c = canvas.Canvas(output, pagesize=(width, height))
        
        template_path = "template.png.png"

        for index, row in df.iterrows():
            # رسم الخلفية PNG
            if os.path.exists(template_path):
                c.drawImage(template_path, 0, 0, width=width, height=height)
            
            # --- توزيع البيانات بناءً على إحداثيات الصور المرسلة ---
            
            # 1. المقاس (24M) - خط Arial كبير
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(width/2, 3.1 * cm, str(row.get('Size', '')))
            
            # 2. الباركود (3.9 سم عرض × 1 سم ارتفاع)
            try:
                val = str(row.get('Barcode_Value', '000000000000'))
                upc = barcode.get('upca', val, writer=ImageWriter())
                barcode_img = io.BytesIO()
                upc.write(barcode_img)
                c.drawInlineImage(Image.open(barcode_img), 0.3 * cm, 2.0 * cm, width=3.9 * cm, height=1.0 * cm)
            except: pass

            # 3. النصوص الصغيرة (STYLE, COLOR, DIM, LABEL)
            # المسافة البادئة 0.5 سم كما في صورتك
            c.setFont("Helvetica", 6)
            left_margin = 0.5 * cm
            
            c.drawString(left_margin, 1.7 * cm, f"STYLE#: {row.get('Style', '')}")
            c.drawString(left_margin, 1.4 * cm, f"COLOR: {row.get('Color', '')}")
            c.drawString(left_margin, 1.1 * cm, str(row.get('Description', '')))
            
            # النصوص جهة اليمين
            right_col = 3.0 * cm
            c.drawString(right_col, 1.7 * cm, f"DIM: {row.get('Dim', '')}")
            c.drawString(right_col, 1.4 * cm, f"LABEL: {row.get('Label', '')}")
            
            # 4. السعر (الأسفل يمين) - مسافة 0.8 سم من اليمين و 0.45 سم من الأسفل
            c.setFont("Helvetica-Bold", 11)
            price_text = f"$ {row.get('Price', '0.00')}"
            c.drawRightString(width - 0.8 * cm, 0.5 * cm, price_text)
            
            c.showPage()
            
        c.save()
        st.download_button("تحميل الملف الجاهز للإليستريتور", data=output.getvalue(), file_name="final_stickers.pdf")
