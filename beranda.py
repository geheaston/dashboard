import streamlit as st

st.set_page_config(
    page_title="Dashboard Analisis Cuaca & Iklim",
    page_icon="🌦️",
    layout="wide"
)

# Judul Utama
st.title("🌦️ Dashboard Analisis Cuaca & Iklim Berbasis Grid")

# Deskripsi Aplikasi
st.markdown("""
---
## 📊 Tentang Aplikasi

Aplikasi ini merupakan dashboard interaktif untuk visualisasi dan analisis data cuaca berbasis **GRID (spasial)** 
yang berasal dari satelit/model global, bukan data stasiun pengamatan titik.

### 📈 Fitur Utama

Aplikasi ini menyediakan analisis mendalam terhadap tiga parameter cuaca utama:

1. **Curah Hujan (CH)**
   - Visualisasi sebaran spasial curah hujan di berbagai lokasi
   - Analisis distribusi frekuensi dan statistik curah hujan
   - Filter interaktif berdasarkan rentang nilai

2. **Sifat Hujan (SH%)**
   - Analisis pola sifat hujan dalam bentuk persentase
   - Klasifikasi menjadi kategori (Bawah Normal, Normal, Atas Normal)
   - Peta sebaran spasial dengan skala warna divergen

3. **Anomali Curah Hujan (AnomCH)**
   - Identifikasi area dengan curah hujan di atas/di bawah normal
   - Visualisasi anomali positif dan negatif
   - Analisis perubahan iklim berbasis grid

---

## 📁 Data Sumber

**Dataset:** GSMaP Blend (Global Satellite Mapping of Precipitation)

- **Format:** File Excel (.xls)
- **Resolusi Spasial:** Grid berbasis koordinat latitude/longitude
- **Parameter Tersedia:**
  - `LON` - Titik koordinat Bujur (X)
  - `LAT` - Titik koordinat Lintang (Y)
  - `CH` - Nilai Curah Hujan
  - `SH%` / `SHpercent` - Sifat Hujan (%)
  - `AnomCH` - Anomali Curah Hujan

---

## 🧭 Panduan Penggunaan

### Cara Navigasi

1. **Sidebar Menu** - Gunakan navigasi di sebelah kiri untuk berpindah antar halaman
2. **Filter Parameter** - Setiap halaman dilengkapi slider filter untuk eksplorasi data lebih detail
3. **Interaksi Peta** - Zoom, pan, dan hover untuk melihat detail informasi grid

### Langkah-Langkah Analisis

**Halaman 1 - Analisis Curah Hujan:**
- Amati pola spasial curah hujan di peta interaktif
- Gunakan slider untuk filter rentang nilai curah hujan
- Lihat distribusi frekuensi pada histogram
- Ekspor data hasil filter untuk analisis lebih lanjut

**Halaman 2 - Analisis Sifat Hujan:**
- Klasifikasi area berdasarkan sifat hujan (Bawah/Normal/Atas Normal)
- Identifikasi hot-spot anomali sifat hujan
- Analisis proporsi setiap kategori

**Halaman 3 - Analisis Anomali:**
- Deteksi area dengan anomali positif (hujan lebih banyak dari normal)
- Deteksi area dengan anomali negatif (hujan lebih sedikit dari normal)
- Nilai 0 menunjukkan kondisi mendekati normal

---

## 🎯 Tujuan Aplikasi

Dashboard ini dirancang untuk:
- ✅ Memudahkan visualisasi data cuaca skala regional
- ✅ Mendukung pengambilan keputusan berbasis data spasial
- ✅ Mempercepat identifikasi pola anomali iklim
- ✅ Menyediakan platform analisis interaktif yang user-friendly

---

## 💡 Tips Penggunaan

1. **Data Spasial** - Setiap titik pada peta merepresentasikan satu grid dengan koordinat tetap
2. **Filter Dinamis** - Gunakan slider untuk fokus pada rentang nilai spesifik
3. **Ekspor Data** - Semua hasil analisis dapat diunduh/disalin untuk presentasi lebih lanjut
4. **Interpretasi Warna** - Warna pada peta menunjukkan intensitas parameter (semakin gelap = nilai semakin tinggi)

---

## 📞 Informasi Teknis

- **Framework:** Streamlit
- **Library Visualisasi:** Plotly
- **Data Processing:** Pandas
- **Sumber Data:** GSMaP Satellite Data

---

**Mulai analisis Anda sekarang dengan memilih halaman dari menu di sebelah kiri! 🚀**
""")

st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p style='color: #888; font-size: 12px;'>Dashboard Analisis Cuaca & Iklim | Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)
