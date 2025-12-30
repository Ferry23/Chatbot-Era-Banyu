import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize Firebase
if not firebase_admin._apps:
    firebase_key = os.environ.get("FIREBASE_SERVICE_ACCOUNT_KEY")
    if firebase_key:
        cred_dict = json.loads(firebase_key)
        cred = credentials.Certificate(cred_dict)
    else:
        try:
            cred = credentials.Certificate("firebase_credentials.json")
        except FileNotFoundError:
            raise Exception("Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT_KEY or provide firebase_credentials.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def get_all_products_from_firebase():
    try:
        products_ref = db.collection('products')
        docs = products_ref.where('isActive', '==', True).stream()

        product_list = []
        for doc in docs:
            d = doc.to_dict()
            item = {
                "Nama Produk": d.get('name', 'Tanpa Nama'),
                "Harga": f"Rp {d.get('price', 0)} / {d.get('unit', 'pcs')}",
                "Stok": d.get('currentStock', 0),
                "Material": d.get('material', '-'),
                "Minimal Order": d.get('minOrderQuantity', 1),
                "Deskripsi": d.get('description', '')
            }
            product_list.append(item)
        return product_list
    except Exception as e:
        print(f"Error fetching Firebase: {e}")
        return []

def get_response(msg):
    # Get product data
    product_knowledge = get_all_products_from_firebase()
    if not product_knowledge:
        return "Maaf, saat ini saya tidak dapat mengakses data produk. Silakan hubungi admin."

    product_context = json.dumps(product_knowledge, indent=2, ensure_ascii=False)

    # Company information
    company_info = """
    Era Banyu adalah perusahaan spesialis pengemasan produk untuk berbagai industri. Kami menyediakan solusi kemasan berkualitas tinggi dan custom sesuai kebutuhan.

    Layanan kami mencakup:
    - Industri umum
    - Otomotif, alat musik, dan peralatan
    - Makanan dan minuman
    - Peralatan medis dan tekstil
    - Panel surya & suku cadang elektronik
    - Logistik, plastik, kertas, dan perlengkapan kantor

    Kami fokus pada pengemasan yang aman, efisien, dan estetik. Dari industri makanan hingga elektronik, kami punya solusinya!

    Untuk konsultasi, hubungi tim kami melalui email info@erabanyu.com atau WhatsApp.
    """

    system_prompt = f"""
    Kamu adalah Customer Service 'Era Banyu Packaging'.

    INFORMASI PERUSAHAAN:
    {company_info}

    DATA PRODUK REAL-TIME:
    {product_context}

    Instruksi:
    1. Jawab pertanyaan user berdasarkan informasi perusahaan dan data produk di atas.
    2. Jika user tanya harga, sebutkan angka spesifik dari data.
    3. Perhatikan 'Minimal Order'. Jika user ingin beli eceran tapi minimal order tinggi, beritahu mereka.
    4. Jawab dengan ramah dalam Bahasa Indonesia.
    5. Jawab dengan intinya saja, hindari jawaban yang panjang.
    6. HANYA jawab pertanyaan yang berkaitan dengan Era Banyu Packaging. Jika pertanyaan di luar konteks ini, katakan "Maaf, saya hanya bisa membantu dengan informasi terkait Era Banyu Packaging."
    7. Untuk pertanyaan umum seperti salam, jawab ramah tapi tetap dalam konteks perusahaan.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.5,
            max_tokens=300,  # Reduced for optimization
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error Groq: {e}")
        return "Maaf, sedang ada gangguan koneksi. Silakan coba lagi nanti."