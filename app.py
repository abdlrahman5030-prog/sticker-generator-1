import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait
import barcode
from barcode.writer import ImageWriter
import io
from PIL import Image

# إعدادات الصفحة
st.set_page_config(page_title="مولد الاستيكرات")
st.title("أداة توليد الاستيكرات الاحترافية")

# رفع ملف البيانات
uploaded_file = st.file_uploader("ارفع ملف الـ CSV الخاص بك", type=["csv"])
barcode_type = st.selectbox("نوع الكود", ["upca", "code128"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("تم رفع الملف بنجاح!")
    
    if st.button("بدء توليد الاستيكرات (PDF)"):
        output = io.BytesIO()
        # هنا بنحدد مقاس الورقة (عرض 200، طول 300) - تقدر تغيرهم حسب مقاس الاستيكر
        c = canvas.Canvas(output, pagesize=(200, 300))
        
        for index, row in df.iterrows():
            # --- منطقة التصميم (Coordinates) ---
            # c.drawString(العرض من اليمين X, الارتفاع من تحت Y, النص)
            
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(100, 270, str(row.get('Size', '18M'))) # المقاس فوق
            
            c.setFont("Helvetica", 9)
            c.drawString(20, 240, f"STYLE#: {row.get('Style', '')}")
            c.drawString(20, 225, f"COLOR: {row.get('Color', '')}")
            
            # توليد الباركود
            code_class = barcode.get_barcode_class(barcode_type)
            val = str(row.get('Barcode_Value', '000000000000'))
            my_barcode = code_class(val, writer=ImageWriter())
            
            b_img = io.BytesIO()
            my_barcode.write(b_img)
            b_img.seek(0)
            img = Image.open(b_img)
            
            # مكان الباركود (العرض، الارتفاع، عرض الصورة، طول الصورة)
            c.drawInlineImage(img, 20, 80, width=160, height=80)
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20, 50, "RETAIL PRICE:")
            c.setFont("Helvetica-Bold", 18)
            c.drawString(120, 45, f"$ {row.get('Price', '0.00')}")
            
            c.showPage() # صفحة جديدة لكل استيكر
            
        c.save()
        st.download_button("تحميل الملف النهائي", data=output.getvalue(), file_name="stickers_ready.pdf")
