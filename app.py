import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Jurnalis Jombang", page_icon="📝", layout="wide")

# --- DATABASE LOKAL & FILTER ---
DB_JOMBANG = {
    "trusted": ["beritajatim.com", "jombangkab.go.id", "radarjombang.jawapos.com", "kabarjombang.com"],
    "hoax_trigger": ["sebarkan", "viral", "hadiah", "pinjaman", "darurat", "detik ini juga"],
    "kecamatan": ["Jombang Kota", "Mojoagung", "Ploso", "Jogoroto", "Perak", "Ngoro", "Diwek", "Sumobito"]
}

# --- FUNGSI AMBIL BERITA DARI LINK (SCRAPER) ---
def extract_news_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ambil Judul
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Berita Tanpa Judul"
        
        # Ambil Paragraf
        paragraphs = soup.find_all('p')
        content = " ".join([p.get_text() for p in paragraphs[:5]]) # Ambil 5 paragraf awal
        
        return title, content
    except Exception as e:
        return None, None

# --- FUNGSI REWRITE (PENULISAN ULANG) ---
def rewrite_news(title, content, mode):
    prefix = "📢 *LAPORAN WARGA JOMBANG*" if mode == "Santai" else "📰 *RILIS PERS RESMI*"
    
    # Logika sederhana menyusun ulang berita
    draf = f"{prefix}\n\n"
    draf += f"*TOPIK:* {title.upper()}\n\n"
    draf += f"*RINGKASAN:* \n{content[:500]}...\n\n"
    draf += f"_Diterbitkan via AI Jurnalis Jombang pada {datetime.now().strftime('%d/%m/%Y %H:%M')}_"
    
    return draf

# --- TAMPILAN DASHBOARD WEB ---
st.markdown("<h1 style='text-align: center;'>🛡️ AI Jurnalis Pribadi Jombang</h1>", unsafe_allow_html=True)
st.divider()

tab1, tab2 = st.tabs(["🔗 Proses Link Berita", "✍️ Tulis Berita Manual"])

# --- TAB 1: PROSES DARI LINK ---
with tab1:
    st.subheader("Olah Berita dari Link Media Lain")
    link_input = st.text_input("Tempel Link Berita Jombang (Beritajatim/Radar/dll):")
    gaya = st.selectbox("Pilih Gaya Penulisan", ["Formal (Rilis)", "Santai (Grup WA)"], key="style1")
    
    if st.button("Proses & Tulis Ulang"):
        if link_input:
            with st.spinner("AI sedang membaca dan menyusun ulang..."):
                t, c = extract_news_from_url(link_input)
                if t:
                    hasil = rewrite_news(t, c, gaya)
                    st.success("Berita Baru Berhasil Dibuat!")
                    st.text_area("Hasil Draf:", hasil, height=250)
                    
                    # Tombol Kirim ke WhatsApp
                    wa_link = f"https://wa.me/?text={urllib.parse.quote(hasil)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px;">Kirim ke WhatsApp ✅</button></a>', unsafe_allow_html=True)
                else:
                    st.error("Gagal mengambil berita. Pastikan link valid.")

# --- TAB 2: TULIS MANUAL ---
with tab2:
    st.subheader("Buat Berita Pribadi dari Kejadian Lapangan")
    col_a, col_b = st.columns(2)
    with col_a:
        judul_pribadi = st.text_input("Apa kejadiannya?")
        lokasi = st.selectbox("Lokasi (Kecamatan)", DB_JOMBANG["kecamatan"])
    with col_b:
        waktu = st.text_input("Waktu Kejadian", value="Baru saja")
    
    kronologi = st.text_area("Ceritakan kronologi singkat (Siapa, Kenapa, Bagaimana):")
    gaya_p = st.selectbox("Pilih Gaya Penulisan", ["Formal (Rilis)", "Santai (Grup WA)"], key="style2")

    if st.button("Buat Berita Manual"):
        if judul_pribadi and kronologi:
            draf_manual = f"📍 *LAPORAN DARI {lokasi.upper()}*\n\n"
            draf_manual += f"*KEJADIAN:* {judul_pribadi}\n"
            draf_manual += f"*WAKTU:* {waktu}\n\n"
            draf_manual += f"*DETAIL:* \n{kronologi}\n\n"
            draf_manual += f"_Dilaporkan secara mandiri via AI Jombang._"
            
            st.success("Berita Manual Siap!")
            st.text_area("Hasil Draf:", draf_manual, height=200)
            
            # Tombol Kirim ke WhatsApp
            wa_link_m = f"https://wa.me/?text={urllib.parse.quote(draf_manual)}"
            st.markdown(f'<a href="{wa_link_m}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px;">Kirim ke WhatsApp ✅</button></a>', unsafe_allow_html=True)
        else:
            st.warning("Mohon lengkapi judul dan kronologi.")

# --- FOOTER ---
st.divider()
st.caption("AI Jurnalis Jombang v1.0 - Pastikan selalu verifikasi fakta sebelum menyebarkan berita.")
