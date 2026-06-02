import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="6. Klastering & Zonasi",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Klastering & Zonasi Spasial (K-Means Clustering)")

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

# Siapkan features untuk clustering
feature_cols = ['CH']
if sh_col and df_clean[sh_col].notna().sum() > 0:
    feature_cols.append(sh_col)
if 'AnomCH' in df_clean.columns and df_clean['AnomCH'].notna().sum() > 0:
    feature_cols.append('AnomCH')

df_cluster = df_clean.dropna(subset=feature_cols).copy()

if len(df_cluster) < 3:
    st.error("❌ Data tidak cukup untuk clustering")
    st.stop()

# ============================================================================
# FILTER DATA DI SIDEBAR
# ============================================================================
st.sidebar.markdown("### 🔍 Pengaturan Clustering")

# Number input untuk jumlah cluster
n_clusters = st.sidebar.number_input(
    "🎯 Jumlah Klaster (k):",
    min_value=2,
    max_value=min(10, len(df_cluster)),
    value=3,
    step=1,
    help="Tentukan jumlah klaster untuk K-Means clustering"
)

# ============================================================================
# PERFORM K-MEANS CLUSTERING
# ============================================================================
# Standardisasi features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_cluster[feature_cols])

# Jalankan K-Means
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

# Tambah label klaster ke dataframe
df_cluster['Klaster'] = clusters

# ============================================================================
# ROW 1: STATISTIK CLUSTERING
# ============================================================================
st.markdown("### 📊 Statistik Klaster")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Jumlah Klaster",
        value=n_clusters,
        help="Jumlah zona spasial yang diidentifikasi"
    )

with col2:
    inertia = kmeans.inertia_
    st.metric(
        label="Inertia (Kompakness)",
        value=f"{inertia:.2f}",
        help="Semakin kecil = semakin compact cluster"
    )

with col3:
    silhouette_score = None
    try:
        from sklearn.metrics import silhouette_score
        sil_score = silhouette_score(X_scaled, clusters)
        st.metric(
            label="Silhouette Score",
            value=f"{sil_score:.3f}",
            help="Range -1 to 1 (1=excellent separation)"
        )
    except:
        st.metric(label="Silhouette Score", value="N/A")

st.markdown("---")

# ============================================================================
# ROW 2: PETA KLASTER SPASIAL
# ============================================================================
st.markdown("### 🗺️ Peta Klastering Spasial")

try:
    # Define colors untuk clusters
    colors = px.colors.qualitative.Set1[:n_clusters]
    
    fig_map = px.scatter_mapbox(
        df_cluster,
        lat='LAT',
        lon='LON',
        color='Klaster',
        hover_data={
            'LAT': ':.4f',
            'LON': ':.4f',
            'CH': ':.2f',
            'Klaster': True
        },
        color_continuous_scale=colors,
        zoom=3,
        center=dict(lat=df_cluster['LAT'].mean(), lon=df_cluster['LON'].mean()),
        mapbox_style='carto-positron',
        title='Peta Zonasi Spasial berdasarkan K-Means',
        labels={
            'LAT': 'Latitude',
            'LON': 'Longitude',
            'Klaster': 'Klaster'
        }
    )
    
    fig_map.update_traces(
        marker=dict(
            size=8,
            opacity=0.8,
            line=dict(width=0)
        )
    )
    
    fig_map.update_layout(
        height=500,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
except Exception as e:
    st.error(f"❌ Error membuat peta: {e}")

st.markdown("---")

# ============================================================================
# ROW 3: KARAKTERISTIK KLASTER
# ============================================================================
st.markdown("### 📊 Karakteristik Setiap Klaster")

# Hitung karakteristik per klaster
cluster_stats = []
for k in range(n_clusters):
    cluster_data = df_cluster[df_cluster['Klaster'] == k]
    
    stats = {
        'Klaster': k,
        'Jumlah Grid': len(cluster_data),
        'Persen Area': f"{(len(cluster_data) / len(df_cluster) * 100):.1f}%"
    }
    
    for col in feature_cols:
        stats[f'Rata-rata {col}'] = f"{cluster_data[col].mean():.2f}"
    
    cluster_stats.append(stats)

df_stats = pd.DataFrame(cluster_stats)

# Tampilkan dalam tabel
st.dataframe(
    df_stats,
    use_container_width=True,
    column_config={
        'Klaster': st.column_config.NumberColumn('Klaster', format='%d'),
        'Jumlah Grid': st.column_config.NumberColumn('Jumlah Grid', format='%d'),
        'Persen Area': st.column_config.TextColumn('Persen Area')
    }
)

st.markdown("---")

# ============================================================================
# ROW 4: BAR CHART KARAKTERISTIK
# ============================================================================
st.markdown("### 📈 Perbandingan Karakteristik Klaster")

# Siapkan data untuk bar chart
chart_data = []
for k in range(n_clusters):
    cluster_data = df_cluster[df_cluster['Klaster'] == k]
    
    for col in feature_cols:
        chart_data.append({
            'Klaster': f'Klaster {k}',
            'Parameter': col,
            'Nilai': cluster_data[col].mean()
        })

df_chart = pd.DataFrame(chart_data)

try:
    fig_bar = px.bar(
        df_chart,
        x='Klaster',
        y='Nilai',
        color='Parameter',
        barmode='group',
        title='Rata-rata Parameter per Klaster',
        labels={'Nilai': 'Nilai Rata-rata', 'Parameter': 'Parameter'},
        height=400
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
except Exception as e:
    st.error(f"❌ Error membuat bar chart: {e}")

st.markdown("---")

# ============================================================================
# ROW 5: INTERPRETASI KLASTER
# ============================================================================
st.markdown("### 🔍 Interpretasi Zona Spasial")

for k in range(n_clusters):
    cluster_data = df_cluster[df_cluster['Klaster'] == k]
    avg_ch = cluster_data['CH'].mean()
    
    # Definisikan karakteristik berdasarkan CH
    if avg_ch < df_cluster['CH'].quantile(0.33):
        karakteristik = "🔵 **Zona Kering** - Curah hujan rendah, minimal"
    elif avg_ch < df_cluster['CH'].quantile(0.67):
        karakteristik = "🟡 **Zona Normal** - Curah hujan sedang, rata-rata"
    else:
        karakteristik = "🔴 **Zona Basah** - Curah hujan tinggi, signifikan"
    
    with st.expander(f"📍 Klaster {k} - {karakteristik}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Jumlah Grid:** {len(cluster_data)}")
            st.write(f"**Persentase Area:** {(len(cluster_data) / len(df_cluster) * 100):.1f}%")
        
        with col2:
            for col in feature_cols:
                st.write(f"**Rata-rata {col}:** {cluster_data[col].mean():.2f}")

st.markdown("---")

# ============================================================================
# ROW 6: TABEL DETAIL DATA CLUSTER
# ============================================================================
st.markdown("### 📋 Data Detail per Klaster")

selected_cluster = st.selectbox(
    "Pilih Klaster untuk Melihat Detail:",
    options=range(n_clusters),
    format_func=lambda x: f"Klaster {x}"
)

df_selected = df_cluster[df_cluster['Klaster'] == selected_cluster][['LON', 'LAT', 'CH', 'Klaster']].copy()

# Tambah kolom sifat hujan jika ada
if sh_col in df_selected.columns:
    df_selected[sh_col] = df_selected[sh_col]

df_selected['LON'] = df_selected['LON'].round(4)
df_selected['LAT'] = df_selected['LAT'].round(4)
df_selected['CH'] = df_selected['CH'].round(2)

st.dataframe(
    df_selected,
    use_container_width=True,
    height=400,
    column_config={
        'LON': st.column_config.NumberColumn('Longitude', format='%.4f'),
        'LAT': st.column_config.NumberColumn('Latitude', format='%.4f'),
        'CH': st.column_config.NumberColumn('Curah Hujan (mm)', format='%.2f'),
        'Klaster': st.column_config.NumberColumn('Klaster', format='%d')
    }
)

# Download
csv = df_selected.to_csv(index=False)
st.download_button(
    label=f"Download CSV - Klaster {selected_cluster}",
    data=csv,
    file_name=f"klaster_{selected_cluster}_data.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown("""
<div style='text-align: center; font-size: 12px; color: #888;'>
    Halaman Klastering & Zonasi | K-Means Clustering untuk Identifikasi Zona Spasial
</div>
""", unsafe_allow_html=True)
