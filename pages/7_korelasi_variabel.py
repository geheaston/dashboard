import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats

st.set_page_config(
    page_title="7. Korelasi Variabel",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 Korelasi & Validasi Variabel (Cross-Variable Analysis)")

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

# Persiapan data
df_clean = df.dropna(subset=['LON', 'LAT', 'CH']).copy()

# Deteksi kolom sifat hujan
if 'SH%' in df_clean.columns and df_clean['SH%'].notna().sum() > 0:
    sh_col = 'SH%'
elif 'SHpercent' in df_clean.columns and df_clean['SHpercent'].notna().sum() > 0:
    sh_col = 'SHpercent'
else:
    sh_col = None

# ============================================================================
# ROW 1: MATRIX KORELASI
# ============================================================================
st.markdown("### 🔢 Matrix Korelasi Antar Variabel")

# Siapkan dataframe untuk korelasi
corr_cols = ['CH']
if sh_col:
    corr_cols.append(sh_col)
if 'AnomCH' in df_clean.columns:
    corr_cols.append('AnomCH')

df_for_corr = df_clean[corr_cols].dropna()

if len(df_for_corr) < 2:
    st.error("❌ Data tidak cukup untuk analisis korelasi")
    st.stop()

# Hitung correlation matrix
corr_matrix = df_for_corr.corr()

# Tampilkan heatmap
try:
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(3),
        texttemplate='%{text:.3f}',
        textfont={"size": 12},
        colorbar=dict(title="Korelasi (r)")
    ))
    
    fig_heatmap.update_layout(
        title='Matriks Korelasi Pearson',
        height=500,
        width=600
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
except Exception as e:
    st.error(f"❌ Error membuat heatmap: {e}")

st.markdown("---")

# ============================================================================
# ROW 2: PILIH VARIABEL UNTUK SCATTER PLOT
# ============================================================================
st.markdown("### 📊 Analisis Scatter Plot & Trendline")

col_var1, col_var2 = st.columns(2)

with col_var1:
    var_x = st.selectbox(
        "Variabel X (Sumbu Horizontal):",
        options=corr_cols,
        index=0
    )

with col_var2:
    available_y = [v for v in corr_cols if v != var_x]
    var_y = st.selectbox(
        "Variabel Y (Sumbu Vertikal):",
        options=available_y,
        index=0
    )

# ============================================================================
# ROW 3: SCATTER PLOT DENGAN TRENDLINE
# ============================================================================
st.markdown(f"### 📈 Scatter Plot: {var_x} vs {var_y}")

try:
    # Filter data untuk kedua variabel
    df_scatter = df_clean[[var_x, var_y]].dropna()
    
    # Hitung korelasi
    corr_coef, p_value = stats.pearsonr(df_scatter[var_x], df_scatter[var_y])
    
    # Buat scatter plot
    fig_scatter = px.scatter(
        df_scatter,
        x=var_x,
        y=var_y,
        trendline='ols',
        trendline_color_override='red',
        title=f'Hubungan {var_x} dan {var_y}',
        labels={var_x: var_x, var_y: var_y},
        height=500,
        opacity=0.6
    )
    
    fig_scatter.update_traces(
        marker=dict(
            size=6,
            color='#4ECDC4',
            opacity=0.6,
            line=dict(width=0)
        ),
        selector=dict(mode='markers')
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
except Exception as e:
    st.error(f"❌ Error membuat scatter plot: {e}")

st.markdown("---")

# ============================================================================
# ROW 4: STATISTIK KORELASI DETAIL
# ============================================================================
st.markdown("### 📊 Statistik Korelasi Detail")

col_stat1, col_stat2, col_stat3 = st.columns(3)

with col_stat1:
    st.metric(
        label="Koefisien Korelasi Pearson (r)",
        value=f"{corr_coef:.4f}",
        help="Range -1 to 1. Nilai mendekati 1 atau -1 = hubungan kuat"
    )

with col_stat2:
    st.metric(
        label="P-Value",
        value=f"{p_value:.6f}",
        help="Jika < 0.05 = korelasi statistik signifikan"
    )

with col_stat3:
    r_squared = corr_coef ** 2
    st.metric(
        label="R² (Coefficient of Determination)",
        value=f"{r_squared:.4f}",
        help=f"Variabilitas {var_y} yang dijelaskan oleh {var_x}"
    )

# Interpretasi
st.markdown("#### 📝 Interpretasi")

col_interp1, col_interp2 = st.columns([1, 2])

with col_interp1:
    st.markdown("**Kekuatan Korelasi:**")
    if abs(corr_coef) < 0.3:
        strength = "🔵 Lemah"
    elif abs(corr_coef) < 0.7:
        strength = "🟡 Sedang"
    else:
        strength = "🔴 Kuat"
    st.write(strength)

with col_interp2:
    st.markdown("**Arah Korelasi:**")
    if corr_coef > 0:
        direction = "📈 **Positif**: Ketika X naik, Y cenderung naik"
    else:
        direction = "📉 **Negatif**: Ketika X naik, Y cenderung turun"
    st.write(direction)

# Signifikansi statistik
st.markdown("**Signifikansi Statistik:**")
if p_value < 0.05:
    sig_text = f"✅ **SIGNIFIKAN** (p = {p_value:.6f} < 0.05) - Korelasi tidak terjadi secara kebetulan"
else:
    sig_text = f"❌ **TIDAK SIGNIFIKAN** (p = {p_value:.6f} ≥ 0.05) - Korelasi mungkin terjadi secara kebetulan"

st.write(sig_text)

st.markdown("---")

# ============================================================================
# ROW 5: DETEKSI OUTLIERS
# ============================================================================
st.markdown("### 🔍 Deteksi Data Pencilan (Outliers)")

# Hitung residuals
from numpy.polynomial.polynomial import Polynomial

x_vals = df_scatter[var_x].values
y_vals = df_scatter[var_y].values

p = Polynomial.fit(x_vals, y_vals, 1)
y_pred = p(x_vals)
residuals = y_vals - y_pred
std_residuals = np.std(residuals)

# Identifikasi outliers (lebih dari 2 std dev dari trendline)
outlier_threshold = 2
df_scatter['Residual'] = residuals
df_scatter['IsOutlier'] = np.abs(residuals) > (outlier_threshold * std_residuals)

num_outliers = df_scatter['IsOutlier'].sum()

col_out1, col_out2 = st.columns(2)

with col_out1:
    st.metric(
        label="Jumlah Outliers Terdeteksi",
        value=num_outliers,
        help=f"Data yang menyimpang >2σ dari garis tren"
    )

with col_out2:
    pct_outliers = (num_outliers / len(df_scatter)) * 100
    st.metric(
        label="Persentase Outliers",
        value=f"{pct_outliers:.2f}%",
        help="Persentase dari total data"
    )

if num_outliers > 0:
    st.markdown("#### 📋 Daftar Data Pencilan")
    
    df_outliers = df_scatter[df_scatter['IsOutlier']][['var_x', 'var_y', 'Residual']].copy()
    df_outliers = df_outliers.rename(columns={'var_x': var_x, 'var_y': var_y})
    df_outliers = df_outliers.round(4)
    
    st.dataframe(
        df_outliers,
        use_container_width=True,
        height=300,
        column_config={
            var_x: st.column_config.NumberColumn(var_x, format='%.4f'),
            var_y: st.column_config.NumberColumn(var_y, format='%.4f'),
            'Residual': st.column_config.NumberColumn('Residual (Error)', format='%.4f')
        }
    )

st.markdown("---")

# ============================================================================
# ROW 6: COMPLETE CORRELATION TABLE
# ============================================================================
st.markdown("### 📋 Tabel Korelasi Lengkap")

# Buat tabel korelasi
corr_table = []
for i, col1 in enumerate(corr_cols):
    for j, col2 in enumerate(corr_cols):
        if i < j:
            r_val = corr_matrix.loc[col1, col2]
            
            # Hitung p-value
            temp_df = df_clean[[col1, col2]].dropna()
            if len(temp_df) > 2:
                _, p_val = stats.pearsonr(temp_df[col1], temp_df[col2])
            else:
                p_val = np.nan
            
            corr_table.append({
                'Variabel 1': col1,
                'Variabel 2': col2,
                'Korelasi (r)': f"{r_val:.4f}",
                'P-Value': f"{p_val:.6f}",
                'Signifikan': '✅' if p_val < 0.05 else '❌'
            })

df_corr_table = pd.DataFrame(corr_table)

st.dataframe(
    df_corr_table,
    use_container_width=True,
    column_config={
        'Variabel 1': st.column_config.TextColumn('Variabel 1'),
        'Variabel 2': st.column_config.TextColumn('Variabel 2'),
        'Korelasi (r)': st.column_config.TextColumn('Korelasi (r)'),
        'P-Value': st.column_config.TextColumn('P-Value'),
        'Signifikan': st.column_config.TextColumn('Signifikan')
    }
)

# Download
csv = df_corr_table.to_csv(index=False)
st.download_button(
    label="Download CSV - Tabel Korelasi",
    data=csv,
    file_name="korelasi_variabel.csv",
    mime="text/csv"
)

st.markdown("---")

# ============================================================================
# ROW 7: PENJELASAN METODOLOGI
# ============================================================================
st.markdown("### 📚 Penjelasan Metodologi")

st.markdown("""
#### **Pearson Correlation Coefficient (r)**
- Mengukur hubungan linear antara dua variabel
- Range: -1 sampai +1
- **r = 1:** Korelasi positif sempurna
- **r = 0:** Tidak ada korelasi
- **r = -1:** Korelasi negatif sempurna

#### **P-Value**
- Probabilitas bahwa korelasi terjadi secara kebetulan (null hypothesis)
- Jika p < 0.05: Korelasi **statistik signifikan**
- Jika p ≥ 0.05: Korelasi **tidak signifikan**

#### **R² (Coefficient of Determination)**
- Menunjukkan proporsi variabilitas dalam Y yang dijelaskan oleh X
- Contoh: R² = 0.64 berarti 64% variasi Y dapat dijelaskan oleh X

#### **Outliers Detection**
- Mengidentifikasi data yang menyimpang jauh dari trendline
- Threshold: ±2 standar deviasi dari garis regresi
- Data pencilan sering mengindikasikan: kesalahan pengukuran, kondisi ekstrim, atau data anomali
""")

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #888;'>
    Halaman Korelasi Variabel | Analisis Hubungan Lintas Parameter Cuaca
</div>
""", unsafe_allow_html=True)
