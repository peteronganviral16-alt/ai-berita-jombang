import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import urllib.parse
import time

# --- KONFIGURASI AI ---
API_KEY = "AIzaSyBg0-0TwWSyHE577XfDugE3spu3QzP6-TY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Jurnalis Jombang Pro", page_icon="📝")

# --- FUNGSI AMBIL & OLAH BERITA ---
def generate_rewrite_ai(url):
    try:
        # Header lebih lengkap agar tidak diblokir situs berita (JPNN, dll)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = response.apparent_encoding
        
        if response.status_code != 200:
            return f"Error: Situs menolak akses (Status {response.status_code})", None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ambil Judul
        title_tag = soup.find('h1')
        title_ori = title_tag.get_text(strip=True) if title_tag else "Berita Jombang"
        
        # Ambil Isi Berita (Cari di paragraf)
        paragraphs = soup.find_all('p')
        content_list = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50]
        content_ori = " ".join(content_list[:8]) # Ambil 8 paragraf pertama saja

        if len(content_ori) < 100:
            return "Error: Isi berita terlalu pendek atau tidak terbaca.", None, None

        # --- PROMPT AI (Tanpa Template) ---
        prompt = f"""
        Tulis ulang berita ini menjadi artikel blog yang baru dan unik.
        Instruksi khusus:
        1. Tulis dalam bahasa Indonesia yang formal tapi enak dibaca warga Jombang.
        2. Buat artikel ini mengalir secara alami dalam 5 paragraf utuh.
        3. Jangan gunakan kalimat pembuka yang selalu sama (JANGAN TEMPLATE).
        4. Berikan judul baru yang menarik (Clickbait positif).
        5. Fokus pada inti informasi tanpa menyertakan iklan atau link eksternal.

        Berita Asli:
        Judul: {title_ori}
        Konten: {content_ori}

        Format Hasil: Berikan Judul di baris pertama, lalu langsung isi 5 paragraf di bawahnya.
        """
        
        response_ai = model.generate_content(prompt)
        full_text = response_ai.text.strip()
        
        # Pisahkan Judul dan Isi
        parts = full_text.split('\n', 1)
        judul_baru = parts[0].replace('#', '').strip()
        isi_baru = parts[1].strip() if len(parts) > 1 else full_text

        # Format HTML untuk Blogspot
        paragraf_html = isi_baru.split('\n')
        html_out = f"<h2>{judul_baru}</h2>"
        for p in paragraf_html:
            if len(p.strip()) > 10:
                html_out += f"<p>{p.strip()}</p>"
        
        html_out += "<br><p><strong>Tags:</strong> #Jombang #BeritaJombang #KabarUpdate #JatimUpdate</p>"

        return judul_baru, html_out, isi_baru

    except Exception as e:
        return f"Error: {str(e)}", None, None

# --- UI STREAMLIT ---
st.markdown("<h1 style='text-align: center;'>🛡️ AI Jurnalis Jombang Pro</h1>", unsafe_allow_html=True)
st.divider()

url_input = st.text_input("🔗 Tempel Link Berita Sumber:", placeholder="Contoh: https://jatim.jpnn.com/...")

if st.button("🚀 Generate Ulang (Rewrite Cerdas)"):
    if url_input:
        with st.spinner("Sedang memproses... AI sedang merangkai kata unik."):
            judul, html_out, teks_polos = generate_rewrite_ai(url_input)
            
            if html_out and "Error" not in judul:
                st.success("Selesai! Artikel unik telah siap.")
                
                with st.expander("👁️ Pratinjau Tampilan", expanded=True):
                    st.markdown(html_out, unsafe_allow_html=True)
                
                st.write("### 💻 Copy Kode HTML untuk Blogspot:")
                st.code(html_out, language="html")
                
                wa_msg = f"*{judul}*\n\n{teks_polos[:200]}...\n\nBaca selengkapnya di Blog!"
                wa_link = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
                st.markdown(f'<a href="{wa_link}" target="_blank"><button style="width:100%;background-color:#25D366;color:white;border:none;padding:12px;border-radius:10px;font-weight:bold;cursor:pointer;">Share ke WhatsApp</button></a>', unsafe_allow_html=True)
            else:
                st.error(f"Gagal: {judul if judul else 'Terjadi kesalahan teknis'}")
    else:
        st.warning("Silakan tempel link berita terlebih dahulu.")
