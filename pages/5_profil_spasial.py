import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="5. Profil Spasial",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Profil Spasial (Zonal & Meridional Profile)")

# ============================================================================
# FUNGSI LOAD DATA DENGAN CACHE
# ============================================================================
@st.cache_data
def load_data():
    """Load data dari file Excel dengan cache untuk performa optimal"""
    try:
        file_path = "data/BlendGSMAP_POS.202605dec02.xls"
        df = pd.read_excel(file_path, engine='xlrd')
        
        # Strip whitespace dari nama kolom
        df.columns = df.columns.str.strip()
        
        # Strip whitespace dari data text (jika ada)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
        
        # Konversi kolom numerik
        numeric_cols = ['LON', 'LAT', 'CH', 'SH%', 'SHpercent', 'AnomCH']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Error membaca file data: {e}")
        return None

# Load data
df = load_data()

if df is None:
    st.stop()

# Validasi kolom
if 'CH' not in df.columns:
    st.error("❌ Kolom 'CH' tidak ditemukan dalam data")
    st.stop()

# ============================================================================
# FILTER DATA DI SIDEBAR
# ============================================================================
st.sidebar.markdown("### 🔍 Filter Profil")

# Radio button untuk pilihan profil
profil_tipe = st.sidebar.radio(
    "📍 Pilih Tipe Profil Spasial:",
    options=['Barat-Timur (Bujur/LON)', 'Utara-Selatan (Lintang/LAT)'],
    help="Pilih arah profil yang ingin dianalisis"
)

# Pilih parameter untuk divisualisasikan
param_option = st.sidebar.selectbox(
    "📊 Parameter Visualisasi:",
    options=['Curah Hujan (CH)', 'Sifat Hujan (SH%)'],
    help="Pilih parameter yang akan ditampilkan pada profil"
)

# ============================================================================
# PROSES DATA BERDASARKAN PILIHAN
# ============================================================================
df_clean = df.dropna(subset=['LON', 'LAT', 'CH']).copy()

if param_option == 'Curah Hujan (CH)':
    param_col = 'CH'
    param_label = 'Curah Hujan (mm)'
else:
    # Deteksi kolom sifat hujan
    if 'SH%' in df.columns and df['SH%'].notna().sum() > 0:
        param_col = 'SH%'
    elif 'SHpercent' in df.columns and df['SHpercent'].notna().sum() > 0:
        param_col = 'SHpercent'
    else:
        st.error("❌ Kolom Sifat Hujan tidak ditemukan")
        st.stop()
    
    param_label = 'Sifat Hujan (%)'
    df_clean = df_clean.dropna(subset=[param_col])

if profil_tipe == 'Barat-Timur (Bujur/LON)':
    # Aggregasi berdasarkan LON
    profil_data = df_clean.groupby('LON')[param_col].agg(['mean', 'std', 'count']).reset_index()
    profil_data = profil_data.sort_values('LON')
    profil_data = profil_data[profil_data['count'] >= 1]  # Filter dengan minimal 1 data point
    
    x_axis = 'LON'
    x_label = 'Longitude (Bujur) - Barat (←) ke Timur (→)'
    title_profil = 'Profil Barat-Timur: Rata-rata ' + param_label

else:
    # Aggregasi berdasarkan LAT
    profil_data = df_clean.groupby('LAT')[param_col].agg(['mean', 'std', 'count']).reset_index()
    profil_data = profil_data.sort_values('LAT')
    profil_data = profil_data[profil_data['count'] >= 1]  # Filter dengan minimal 1 data point
    
    x_axis = 'LAT'
    x_label = 'Latitude (Lintang) - Utara (↑) ke Selatan (↓)'
    title_profil = 'Profil Utara-Selatan: Rata-rata ' + param_label

# ============================================================================
# ROW 1: STATISTIK PROFIL
# ============================================================================
st.markdown("### 📊 Ringkasan Profil Spasial")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Jumlah Titik Profil",
        value=len(profil_data),
        help="Jumlah unique coordinate points"
    )

with col2:
    st.metric(
        label="Mean (Rata-rata)",
        value=f"{profil_data['mean'].mean():.2f}",
        help="Rata-rata dari semua titik profil"
    )

with col3:
    st.metric(
        label="Standar Deviasi",
        value=f"{profil_data['std'].mean():.2f}",
        help="Variabilitas rata-rata antar titik"
    )

with col4:
    st.metric(
        label="Range",
        value=f"{profil_data['mean'].max() - profil_data['mean'].min():.2f}",
        help="Perbedaan antara nilai tertinggi dan terendah"
    )

st.markdown("---")

# ============================================================================
# ROW 2: LINE CHART PROFIL
# ============================================================================
st.markdown("### 📈 Grafik Profil Spasial")

try:
    fig = go.Figure()
    
    # Tambah garis rata-rata
    fig.add_trace(go.Scatter(
        x=profil_data[x_axis],
        y=profil_data['mean'],
        mode='lines+markers',
        name='Rata-rata',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8),
        hovertemplate=f"<b>{x_label.split(' - ')[0]}</b>: %{{x:.4f}}<br>{param_label}: %{{y:.2f}}<extra></extra>"
    ))
    
    # Tambah area untuk std dev (confidence band)
    fig.add_trace(go.Scatter(
        x=profil_data[x_axis],
        y=profil_data['mean'] + profil_data['std'],
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.add_trace(go.Scatter(
        x=profil_data[x_axis],
        y=profil_data['mean'] - profil_data['std'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        name='±1 Std Dev',
        fillcolor='rgba(255, 107, 107, 0.2)',
        hoverinfo='skip'
    ))
    
    fig.update_xaxes(title_text=x_label)
    fig.update_yaxes(title_text=param_label)
    
    fig.update_layout(
        title=title_profil,
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
except Exception as e:
    st.error(f"❌ Error membuat grafik: {e}")

st.markdown("---")

# ============================================================================
# ROW 3: ANALISIS TREN
# ============================================================================
st.markdown("### 🔍 Analisis Tren")

# Hitung tren (simple linear regression)
from numpy.polynomial.polynomial import Polynomial

x_values = profil_data[x_axis].values
y_values = profil_data['mean'].values

# Fit polynomial degree 1 (linear)
p = Polynomial.fit(x_values, y_values, 1)
coeffs = p.convert().coef
slope = coeffs[1]
intercept = coeffs[0]

col_trend1, col_trend2 = st.columns(2)

with col_trend1:
    st.markdown("#### 📊 Statistik Tren Linear")
    st.write(f"**Slope (Kemiringan):** `{slope:.6f}`")
    st.write(f"**Intercept (Potongan Y):** `{intercept:.2f}`")
    
    if abs(slope) < 0.01:
        trend_desc = "📍 **Relatif stabil/flat** (tren lemah)"
    elif slope > 0:
        trend_desc = f"📈 **Meningkat** dari {x_axis} barat ke timur/utara ke selatan"
    else:
        trend_desc = f"📉 **Menurun** dari {x_axis} barat ke timur/utara ke selatan"
    
    st.write(trend_desc)

with col_trend2:
    st.markdown("#### 📌 Interpretasi Geografis")
    
    if profil_tipe == 'Barat-Timur (Bujur/LON)':
        st.markdown("""
        Profil Barat-Timur menunjukkan variabilitas curah hujan dari:
        - **Barat:** Pulau Sumatera, Selat Malaka
        - **Timur:** Pulau Papua, Arafura
        
        Berguna untuk analisis monsun dan pengaruh laut.
        """)
    else:
        st.markdown("""
        Profil Utara-Selatan menunjukkan variabilitas curah hujan dari:
        - **Utara:** Laut Jawa, Laut Cina Selatan
        - **Selatan:** Samudra Hindia
        
        Berguna untuk analisis meridional circulation.
        """)

st.markdown("---")

# ============================================================================
# ROW 4: TABEL DATA PROFIL
# ============================================================================
st.markdown("### 📋 Data Profil Detail")

df_profil_display = profil_data.copy()
df_profil_display['mean'] = df_profil_display['mean'].round(2)
df_profil_display['std'] = df_profil_display['std'].round(2)
df_profil_display[x_axis] = df_profil_display[x_axis].round(4)

df_profil_display = df_profil_display.rename(columns={
    x_axis: ('Bujur (LON)' if x_axis == 'LON' else 'Lintang (LAT)'),
    'mean': f'Rata-rata {param_label}',
    'std': 'Standar Deviasi',
    'count': 'Jumlah Data Point'
})

st.dataframe(
    df_profil_display,
    use_container_width=True,
    height=400,
    column_config={
        'Bujur (LON)': st.column_config.NumberColumn('Bujur (LON)', format='%.4f'),
        'Lintang (LAT)': st.column_config.NumberColumn('Lintang (LAT)', format='%.4f'),
        f'Rata-rata {param_label}': st.column_config.NumberColumn(f'Rata-rata {param_label}', format='%.2f'),
        'Standar Deviasi': st.column_config.NumberColumn('Standar Deviasi', format='%.2f'),
        'Jumlah Data Point': st.column_config.NumberColumn('Jumlah Data Point', format='%d')
    }
)

# Download data
csv = df_profil_display.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="profil_spasial.csv",
    mime="text/csv",
    help="Unduh data profil spasial"
)

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #888;'>
    Halaman Profil Spasial | Analisis Variabilitas Zonal & Meridional
</div>
""", unsafe_allow_html=True)
