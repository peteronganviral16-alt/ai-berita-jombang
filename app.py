import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.parse

# --- CONFIG HALAMAN ---
st.set_page_config(
    page_title="AI Jurnalis Jombang - Blog Generator", 
    page_icon="🏢", 
    layout="wide"
)

# --- CSS CUSTOM UNTUK TAMPILAN HP ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .stTextArea>div>div>textarea {
        background-color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI UTAMA: SCRAPER & BLOG GENERATOR ---
def generate_blog_article(url):
    try:
        # Header agar tidak diblokir server berita
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Ambil Judul Asli
        original_title = ""
        if soup.find('h1'):
            original_title = soup.find('h1').get_text(strip=True)
        elif soup.find('meta', property='og:title'):
            original_title = soup.find('meta', property='og:title')['content']
        else:
            original_title = "Berita Terbaru Jombang"

        # 2. Ambil Isi Berita (Filter paragraf bermutu)
        paragraphs = soup.find_all('p')
        raw_text = []
        for p in paragraphs:
            txt = p.get_text(strip=True)
            if len(txt) > 60 and "baca juga" not in txt.lower() and "iklan" not in txt.lower():
                raw_text.append(txt)
        
        if not raw_text:
            return None, None, None

        # --- PROSES REWRITE JADI ARTIKEL BLOG ---
        new_title = f"{original_title} - Update Terkini Wilayah Jombang"
        tgl_skrg = datetime.now().strftime("%d %B %Y")
        
        # Menyusun konten dengan struktur HTML Blogspot
        intro = f"Kabar terbaru datang dari Kabupaten Jombang hari ini, {tgl_skrg}. Informasi mengenai <strong>{original_title}</strong> tengah menjadi perbincangan hangat di tengah masyarakat lokal."
        
        p1 = f"Berdasarkan penelusuran tim di lapangan, kejadian ini bermula saat {raw_text[0] if len(raw_text) > 0 else 'informasi mulai tersebar luas di media sosial'}. Hal ini memicu respon dari berbagai pihak terkait di wilayah Jombang."
        
        p2 = f"Lebih lanjut, dilaporkan bahwa {raw_text[1] if len(raw_text) > 1 else 'situasi saat ini masih dalam pemantauan petugas berwenang'}. Warga diharapkan tetap tenang dan mengikuti instruksi resmi agar tidak termakan isu yang belum jelas kebenarannya."
        
        kesimpulan = "Demikian laporan terkini mengenai situasi di Jombang. Kami akan terus memperbarui informasi ini jika terdapat perkembangan terbaru dari pihak terkait."

        # Gabungkan dalam format HTML Blogspot
        html_blogspot = f"""
<h2>{new_title}</h2>
<p><strong>JOMBANG</strong> - {intro}</p>
<p>{p1}</p>
<h3>Kondisi Terkini di Lapangan</h3>
<p>{p2}</p>
<hr>
<p><i>{kesimpulan}</i></p>
<p><strong>Tags:</strong> #Jombang #KabarJombang #BeritaJombang #JombangHariIni</p>
        """
        
        # Ringkasan untuk Share WA
        wa_text = f"*{new_title}*\n\nJOMBANG - {intro[:150]}...\n\nBaca selengkapnya di Blog kami!"
        
        return new_title, html_blogspot, wa_text

    except Exception as e:
        return f"Error: {str(e)}", None, None

# --- ANTARMUKA PENGGUNA (UI) ---
st.markdown("<h1 style='text-align: center; color: #1e3d59;'>🏢 Jombang Blog Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ubah Link Berita Lokal Jadi Artikel Blog Baru</p>", unsafe_allow_html=True)
st.divider()

# Input Link
url_target = st.text_input("🔗 Tempel Link Berita Sumber (Radar, Beritajatim, dll):", placeholder="https://radarjombang.jawapos.com/...")

if st.button("🚀 Generate Artikel Baru"):
    if url_target:
        with st.spinner("AI sedang meriset dan menulis ulang..."):
            judul, html_code, wa_msg = generate_blog_article(url_target)
            
            if html_code:
                st.success("Artikel Siap Diunggah ke Blogspot!")
                
                # Tampilan Preview
                with st.expander("👁️ Pratinjau Tampilan di Blog", expanded=True):
                    st.markdown(html_code, unsafe_allow_html=True)
                
                st.divider()
                
                # Bagian Copy Paste
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.subheader("📌 Judul Postingan")
                    st.code(judul)
                    
                    st.subheader("HTML Code (Paste di Blogspot)")
                    st.code(html_code, language="html")
                    st.caption("Gunakan mode 'Tampilan HTML' di editor Blogspot saat menempel kode ini.")
                
                with col_right:
                    st.subheader("📲 Bagikan ke WhatsApp")
                    st.write("Gunakan ini untuk promosi artikel blog baru kamu:")
                    wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; width:100%; font-weight:bold; cursor:pointer;">Share Ringkasan ke WA ✅</button></a>', unsafe_allow_html=True)
            else:
                st.error("Gagal mengambil data. Pastikan link berita valid atau coba link media lain.")

st.divider()
st.caption("AI Jurnalis Jombang v2.0 - Membantu Kreator Blog Lokal Jombang")
