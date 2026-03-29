import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import urllib.parse

# --- KONFIGURASI AI (GEMINI) ---
# API Key sudah terpasang di bawah ini
API_KEY = "AIzaSyBg0-0TwWSyHE577XfDugE3spu3QzP6-TY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIG HALAMAN ---
st.set_page_config(page_title="AI Jurnalis Jombang Pro", page_icon="📝", layout="wide")

# CSS untuk tampilan HP agar lebih rapi
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #1e3d59;
        color: white;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI GENERATE ARTIKEL CERDAS ---
def generate_rewrite_ai(url):
    try:
        # 1. Scrapping Berita Asli
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Ambil Judul & Isi Mentah
        title_ori = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Kabar Jombang"
        paragraphs = soup.find_all('p')
        content_ori = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text()) > 60])

        if not content_ori:
            return None, None, None

        # 2. Perintah Prompt (Instruksi agar AI menulis ulang tanpa template)
        prompt = f"""
        Tulis ulang berita berikut menjadi artikel blog yang baru, segar, dan unik.
        Aturan:
        1. Jangan gunakan template. Tulis secara natural seperti jurnalis manusia.
        2. Buat menjadi 5 paragraf utuh yang mengalir.
        3. Gunakan gaya bahasa jurnalisme lokal Jombang yang informatif.
        4. Berikan judul baru yang menarik dan berbeda dari aslinya.
        5. Pastikan artikel berfokus pada kejadian di Jombang.
        
        Judul Asli: {title_ori}
        Isi Berita: {content_ori[:2500]}
        
        Format output: baris pertama JUDUL, baris selanjutnya ISI ARTIKEL.
        """
        
        response = model.generate_content(prompt)
        hasil_ai = response.text.strip()
        
        # Memisahkan Judul dan Isi untuk keperluan tampilan
        parts = hasil_ai.split('\n', 1)
        judul_baru = parts[0].replace('**', '')
        isi_baru = parts[1] if len(parts) > 1 else ""

        # Format ke HTML untuk Blogspot
        paragraf_list = isi_baru.split('\n\n')
        html_blogspot = f"<h2>{judul_baru}</h2>"
        for p in paragraf_list:
            if p.strip():
                html_blogspot += f"<p>{p.strip()}</p>"
        html_blogspot += "<br><p><strong>Tags:</strong> #Jombang #BeritaJombang #KabarJombang #JombangUpdate</p>"

        return judul_baru, html_blogspot, isi_baru

    except Exception as e:
        return f"Error: {str(e)}", None, None

# --- TAMPILAN DASHBOARD ---
st.markdown("<h1 style='text-align: center;'>🛡️ AI Jurnalis Jombang Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Teknologi Rewrite Otomatis (Tanpa Template)</p>", unsafe_allow_html=True)
st.divider()

url_input = st.text_input("🔗 Tempel Link Berita Sumber:")

if st.button("🚀 Generate Ulang (Rewrite Cerdas)"):
    if url_input:
        with st.spinner("AI sedang membaca dan menulis ulang artikel unik..."):
            judul, html_out, teks_polos = generate_rewrite_ai(url_input)
            
            if html_out:
                st.success("Artikel Berhasil Ditulis Ulang!")
                
                # Preview Tampilan
                with st.expander("👁️ Lihat Pratinjau Artikel", expanded=True):
                    st.markdown(html_out, unsafe_allow_html=True)
                
                st.divider()
                
                # Output untuk Copy-Paste
                col1, col2 = st.columns(2)
                with col1:
                    st.write("### 📌 Judul Baru:")
                    st.code(judul)
                    
                    st.write("### 💻 Kode HTML (Untuk Blogspot):")
                    st.code(html_out, language="html")
                
                with col2:
                    st.write("### 📲 Bagikan ke WA:")
                    wa_msg = f"*{judul}*\n\n{teks_polos[:200]}...\n\nBaca selengkapnya di Blog kami!"
                    wa_link = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; width:100%; font-weight:bold; cursor:pointer;">Share ke WhatsApp ✅</button></a>', unsafe_allow_html=True)
            else:
                st.error("Gagal memproses berita. Pastikan link aktif atau coba link lain.")

st.divider()
st.caption("AI Jurnalis v3.5 - Powered by Gemini AI")
