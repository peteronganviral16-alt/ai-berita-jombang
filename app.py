import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import urllib.parse

# --- KONFIGURASI API ---
# API Key Anda
API_KEY = "AIzaSyBg0-0TwWSyHE577XfDugE3spu3QzP6-TY"
genai.configure(api_key=API_KEY)

# PERBAIKAN: Menggunakan pemanggilan model yang paling kompatibel
model = genai.GenerativeModel('gemini-pro') 

st.set_page_config(page_title="AI Jurnalis Jombang", page_icon="📝")

# --- CSS SEDERHANA ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #1e3d59;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI PROSES ---
def proses_berita(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = res.apparent_encoding
        
        if res.status_code != 200:
            return f"Koneksi Gagal (Status {res.status_code})", None, None

        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Ambil Judul & Isi
        h1 = soup.find('h1')
        t_asli = h1.get_text(strip=True) if h1 else "Berita Jombang"
        
        p_tags = soup.find_all('p')
        isi_asli = " ".join([p.get_text(strip=True) for p in p_tags if len(p.get_text(strip=True)) > 50])

        if len(isi_asli) < 100:
            return "Isi berita tidak terdeteksi.", None, None

        # --- PERINTAH AI (REWRITE) ---
        prompt = f"""
        Tulis ulang berita berikut menjadi artikel blog 5 paragraf yang unik.
        Aturan:
        1. JANGAN gunakan template. Tulis ulang total dengan kata-kata baru.
        2. Gaya bahasa jurnalisme santun Jombang.
        3. Buat judul baru yang menarik.
        4. Artikel harus mengalir alami, hilangkan semua iklan.
        
        Isi Berita Sumber: {isi_asli[:2000]}
        """
        
        # Eksekusi AI
        response = model.generate_content(prompt)
        teks_ai = response.text.strip()
        
        # Olah hasil
        baris = teks_ai.split('\n')
        judul_baru = baris[0].replace('*', '').strip()
        isi_baru = "\n\n".join(baris[1:]).strip()

        # Format HTML
        html_out = f"<h2>{judul_baru}</h2>"
        for p in baris[1:]:
            if len(p.strip()) > 10:
                html_out += f"<p>{p.strip()}</p>"
        html_out += "<br><p><strong>Tags:</strong> #Jombang #KabarJombang #UpdateJombang</p>"

        return judul_baru, html_out, isi_baru

    except Exception as e:
        return f"Sistem Error: {str(e)}", None, None

# --- UI ---
st.title("🛡️ AI Jurnalis Jombang")
st.write("Teknologi Rewrite Otomatis - Tanpa Template")
st.divider()

link = st.text_input("Tempel Link Berita:")

if st.button("Generate Sekarang"):
    if link:
        with st.spinner("AI sedang menulis ulang..."):
            j, h, t = proses_berita(link)
            
            if h and "Error" not in j and "Sistem" not in j:
                st.success("Berhasil!")
                with st.expander("Pratinjau", expanded=True):
                    st.markdown(h, unsafe_allow_html=True)
                
                st.write("### Kode HTML Blogspot:")
                st.code(h, language="html")
                
                msg = f"*{j}*\n\n{t[:200]}...\n\nBaca di Blog!"
                wa = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{wa}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:12px;border-radius:10px;font-weight:bold;cursor:pointer;">Share ke WhatsApp</button></a>', unsafe_allow_html=True)
            else:
                st.error(j)
