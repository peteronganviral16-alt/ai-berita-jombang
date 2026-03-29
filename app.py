import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import urllib.parse

# --- KONFIGURASI API KEY TERBARU ---
NEW_API_KEY = "AIzaSyBg0-0TwWSyHE577XfDugE3spu3QzP6-TY"
genai.configure(api_key=NEW_API_KEY)

st.set_page_config(page_title="AI Jurnalis Jombang Pro", page_icon="🏢")

# --- FUNGSI DETEKSI MODEL OTOMATIS ---
def ambil_model_aktif():
    try:
        # Mencari model yang didukung oleh API Key baru ini
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if '1.5-flash' in m.name or '1.5-pro' in m.name or 'gemini-pro' in m.name:
                    return m.name
    except:
        return None
    return None

# --- FUNGSI REWRITE BERITA ---
def rewrite_berita(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Ambil Judul & Isi Mentah
        h1 = soup.find('h1')
        t_asli = h1.get_text(strip=True) if h1 else "Berita Jombang"
        paragraphs = soup.find_all('p')
        isi_mentah = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])

        if len(isi_mentah) < 100:
            return "Gagal: Konten berita tidak terbaca dari link ini.", None

        # Pilih Model Secara Otomatis
        nama_model = ambil_model_aktif()
        if not nama_model:
            return "Error: API Key tidak memiliki akses ke model Gemini.", None

        model_ai = genai.GenerativeModel(nama_model)
        
        # Prompt Rewrite Tanpa Template
        prompt = f"""
        Tulis ulang berita berikut menjadi artikel blog 5 paragraf yang unik, segar, dan informatif.
        Aturan:
        1. JANGAN pakai template kaku. Olah kata-kata secara kreatif.
        2. Gunakan gaya bahasa jurnalisme lokal Jombang yang menarik.
        3. Buat judul baru yang menarik (Headline).
        4. Artikel harus mengalir alami dalam 5 paragraf utuh.
        
        Berita Sumber: {isi_mentah[:2000]}
        """
        
        response = model_ai.generate_content(prompt)
        teks_ai = response.text.strip()
        
        # Pisahkan Judul dan Isi
        baris = teks_ai.split('\n')
        judul_baru = baris[0].replace('*', '').replace('#', '').strip()
        
        # Buat format HTML Blogspot
        html_out = f"<h2>{judul_baru}</h2>"
        for p in baris[1:]:
            if len(p.strip()) > 10:
                html_out += f"<p>{p.strip()}</p>"
        html_out += "<br><p><strong>Tags:</strong> #Jombang #KabarJombang #UpdateJombang #InfoJombang</p>"

        return judul_baru, html_out

    except Exception as e:
        return f"Sistem Error: {str(e)}", None

# --- TAMPILAN DASHBOARD ---
st.markdown("<h1 style='text-align: center;'>🛡️ AI Jurnalis Jombang Pro</h1>", unsafe_allow_html=True)
st.caption(f"Model Aktif: {ambil_model_aktif() if ambil_model_aktif() else 'Mencari...'}")
st.divider()

url_link = st.text_input("🔗 Tempel Link Berita Jombang:")

if st.button("🚀 Olah Berita (Rewrite Cerdas)"):
    if url_link:
        with st.spinner("AI sedang berpikir dan menulis ulang artikel unik..."):
            judul, html_hasil = rewrite_berita(url_link)
            
            if html_hasil and "Error" not in judul:
                st.success("Berita Berhasil Ditulis Ulang!")
                
                with st.expander("👁️ Pratinjau Artikel", expanded=True):
                    st.markdown(html_hasil, unsafe_allow_html=True)
                
                st.divider()
                st.write("### 💻 Kode HTML (Copy ke Blogspot):")
                st.code(html_hasil, language="html")
                
                wa_msg = f"*{judul}*\n\nBaca artikel selengkapnya di Blog Jombang kami!"
                wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
                st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:12px;border-radius:10px;font-weight:bold;cursor:pointer;">📲 Bagikan ke WhatsApp</button></a>', unsafe_allow_html=True)
            else:
                st.error(judul)
    else:
        st.warning("Masukkan link berita terlebih dahulu.")

st.divider()
st.info("💡 Setiap kali kamu klik tombol, AI akan merangkai kalimat yang berbeda agar artikelmu unik.")
