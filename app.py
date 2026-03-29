import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import urllib.parse

# --- KONFIGURASI AI ---
# API Key kamu tetap aman
API_KEY = "AIzaSyBg0-0TwWSyHE577XfDugE3spu3QzP6-TY"
genai.configure(api_key=API_KEY)

# PERBAIKAN: Menggunakan nama model yang lebih stabil
model = genai.GenerativeModel('gemini-1.5-flash-latest')

st.set_page_config(page_title="AI Jurnalis Jombang Pro", page_icon="📝")

# --- CSS CUSTOM ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #1e3d59;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI UTAMA ---
def generate_rewrite_ai(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = response.apparent_encoding
        
        if response.status_code != 200:
            return f"Error: Gagal akses situs (Status {response.status_code})", None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ambil Judul & Konten
        title_tag = soup.find('h1')
        title_ori = title_tag.get_text(strip=True) if title_tag else "Berita Jombang"
        
        paragraphs = soup.find_all('p')
        content_list = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
        content_ori = " ".join(content_list[:8])

        if len(content_ori) < 100:
            return "Error: Isi berita tidak terbaca atau terlalu pendek.", None, None

        # --- PROMPT TANPA TEMPLATE ---
        prompt = f"""
        Tulis ulang berita berikut menjadi artikel blog 5 paragraf yang unik dan segar.
        Instruksi:
        1. Jangan pakai template kaku. Gunakan gaya bahasa jurnalis asli.
        2. Tulis dalam Bahasa Indonesia yang baik untuk warga Jombang.
        3. Berikan judul baru yang menarik dan berbeda dari aslinya.
        4. Artikel harus mengalir natural tanpa iklan.
        
        Berita Asli: {content_ori}
        """
        
        # Eksekusi AI
        response_ai = model.generate_content(prompt)
        full_text = response_ai.text.strip()
        
        # Pisahkan Judul dan Isi
        lines = full_text.split('\n', 1)
        judul_baru = lines[0].replace('#', '').strip()
        isi_baru = lines[1].strip() if len(lines) > 1 else full_text

        # Format HTML
        paragraf_html = isi_baru.split('\n')
        html_out = f"<h2>{judul_baru}</h2>"
        for p in paragraf_html:
            if len(p.strip()) > 10:
                html_out += f"<p>{p.strip()}</p>"
        html_out += "<br><p><strong>Tags:</strong> #Jombang #KabarJombang #UpdateJombang</p>"

        return judul_baru, html_out, isi_baru

    except Exception as e:
        return f"Error: {str(e)}", None, None

# --- UI ---
st.markdown("<h1 style='text-align: center;'>🛡️ AI Jurnalis Jombang Pro</h1>", unsafe_allow_html=True)
st.divider()

url_input = st.text_input("🔗 Tempel Link Berita Sumber:", placeholder="https://...")

if st.button("🚀 Generate Ulang (Rewrite Cerdas)"):
    if url_input:
        with st.spinner("AI sedang merangkai kata..."):
            j, h, t = generate_rewrite_ai(url_input)
            
            if h and "Error" not in j:
                st.success("Berita Berhasil Ditulis Ulang!")
                with st.expander("👁️ Pratinjau", expanded=True):
                    st.markdown(h, unsafe_allow_html=True)
                
                st.write("### 💻 Copy Kode HTML:")
                st.code(h, language="html")
                
                wa_msg = f"*{j}*\n\n{t[:200]}...\n\nBaca selengkapnya di Blog!"
                wa_link = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
                st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:12px;border-radius:10px;font-weight:bold;cursor:pointer;">Share ke WhatsApp</button></a>', unsafe_allow_html=True)
            else:
                st.error(f"{j}")

st.divider()
st.caption("AI Jurnalis v3.6 - Fixed Model Issue")
