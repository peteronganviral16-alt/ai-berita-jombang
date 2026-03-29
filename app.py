import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Jurnalis Jombang", page_icon="📝", layout="wide")

# --- DATABASE KECAMATAN JOMBANG ---
KECAMATAN = ["Jombang Kota", "Mojoagung", "Ploso", "Jogoroto", "Perak", "Ngoro", "Diwek", "Sumobito", "Tembelang", "Kesamben", "Kudu", "Ngusikan"]

# --- FUNGSI SCRAPER TINGKAT LANJUT ---
def extract_news_advanced(url):
    try:
        # Header agar tidak terbaca sebagai Robot/Bot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Cari Judul (Cek berbagai tag umum)
        title = ""
        h1_tag = soup.find('h1')
        meta_og_title = soup.find('meta', property='og:title')
        
        if h1_tag:
            title = h1_tag.get_text(strip=True)
        elif meta_og_title:
            title = meta_og_title['content']
        else:
            title = "Berita Lokal Terkini"

        # 2. Cari Isi Berita (Filter paragraf yang terlalu pendek/menu)
        paragraphs = soup.find_all('p')
        content_list = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Hanya ambil paragraf yang terlihat seperti berita (minimal 60 karakter)
            if len(text) > 60 and "iklan" not in text.lower() and "baca juga" not in text.lower():
                content_list.append(text)
        
        # Gabungkan 3 paragraf pertama agar padat
        final_content = " ".join(content_list[:3])
        
        if not final_content:
            return title, "Gagal menarik isi berita secara otomatis. Situs ini mungkin dilindungi. Silakan salin teks manual ke tab 'Tulis Berita Manual'."

        return title, final_content

    except Exception as e:
        return "Error Koneksi", f"Gagal mengakses link. Pastikan link benar. Error: {str(e)}"

# --- FUNGSI REWRITE (MENYUSUN ULANG) ---
def format_whatsapp_msg(title, content, mode, location="Jombang"):
    header = "📢 *KABAR JOMBANG TERKINI*" if mode == "Santai" else "📰 *RILIS BERITA RESMI*"
    
    msg = f"{header}\n\n"
    msg += f"*TOPIK:* {title.upper()}\n"
    msg += f"*LOKASI:* {location}\n\n"
    msg += f"*RINGKASAN KEJADIAN:* \n{content}\n\n"
    msg += f"--- \n_Diterbitkan otomatis via AI Jurnalis Jombang pada {datetime.now().strftime('%d/%m/%Y %H:%M')}_"
    return msg

# --- TAMPILAN DASHBOARD ---
st.markdown("<h1 style='text-align: center;'>🛡️ AI Jurnalis Pribadi Jombang</h1>", unsafe_allow_html=True)
st.divider()

tab1, tab2 = st.tabs(["🔗 Olah dari Link", "✍️ Tulis Berita Manual"])

# --- TAB 1: DARI LINK ---
with tab1:
    st.subheader("Otomatiskan Link Berita Jadi Pesan WA")
    link_input = st.text_input("Tempel Link Berita (Beritajatim/Radar/Detik):")
    loc_1 = st.selectbox("Pilih Lokasi Kejadian", KECAMATAN, key="loc1")
    gaya_1 = st.selectbox("Gaya Penulisan", ["Formal (Rilis)", "Santai (Grup WA)"], key="style1")
    
    if st.button("Proses Link Sekarang"):
        if link_input:
            with st.spinner("Sedang menembus server berita..."):
                t, c = extract_news_advanced(link_input)
                hasil = format_whatsapp_msg(t, c, gaya_1, loc_1)
                
                st.success("Berita Berhasil Disusun!")
                st.text_area("Pratinjau Teks:", hasil, height=300)
                
                # Link WhatsApp
                encoded_msg = urllib.parse.quote(hasil)
                wa_url = f"https://wa.me/?text={encoded_msg}"
                st.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold;">Kirim ke WhatsApp ✅</button></a>', unsafe_allow_html=True)
        else:
            st.warning("Masukkan link dulu!")

# --- TAB 2: MANUAL ---
with tab2:
    st.subheader("Buat Berita Sendiri (Laporan Warga)")
    t_man = st.text_input("Apa kejadiannya? (Contoh: Pohon Tumbang)")
    loc_2 = st.selectbox("Lokasi Kejadian", KECAMATAN, key="loc2")
    isi_man = st.text_area("Ceritakan detail kejadiannya (Siapa, Jam Berapa, Kronologi):")
    gaya_2 = st.selectbox("Gaya Penulisan", ["Formal (Rilis)", "Santai (Grup WA)"], key="style2")

    if st.button("Buat Berita Manual"):
        if t_man and isi_man:
            hasil_m = format_whatsapp_msg(t_man, isi_man, gaya_2, loc_2)
            st.success("Draf Berita Siap!")
            st.text_area("Pratinjau Teks:", hasil_m, height=250)
            
            # Link WhatsApp
            encoded_msg_m = urllib.parse.quote(hasil_m)
            wa_url_m = f"https://wa.me/?text={encoded_msg_m}"
            st.markdown(f'<a href="{wa_url_m}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer; font-weight:bold;">Kirim ke WhatsApp ✅</button></a>', unsafe_allow_html=True)
        else:
            st.warning("Mohon isi judul dan kronologi kejadian.")

st.divider()
st.caption("AI Jurnalis Jombang v1.1 - Membantu warga mendapatkan informasi terverifikasi.")
