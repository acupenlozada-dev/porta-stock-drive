import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection
import unicodedata

# ══════════════════════════════════════════════
# CONFIGURACIÓN DE LA FUENTE DE DATOS
# ══════════════════════════════════════════════
GDRIVE_URL = "https://docs.google.com/spreadsheets/d/1jCAE3PbADPc7gz16UOvlpby5VzpfR3b8gLNy_4ROEe8/edit#gid=0"
SHEET_NAME = "Report"

R1="#C8102E"; R2="#E8394A"; R3="#FF6B7A"; RD="#8B0000"
BG="#FDF2F3"; W="#FFFFFF"; G2="#64748b"

st.set_page_config(page_title="Porta · Stock", page_icon="🎒",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'Inter',sans-serif!important;}}
.main .block-container{{background:{BG};padding-top:1rem;padding-bottom:2rem;}}
[data-testid="stSidebar"]{{background:linear-gradient(180deg,{RD} 0%,{R1} 60%,{R2} 100%)!important;}}
[data-testid="stSidebar"] section[data-testid="stSidebarContent"]{{background:transparent!important;}}
[data-testid="stSidebar"] *{{color:white!important;}}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p{{color:rgba(255,255,255,0.7)!important;font-size:.7rem!important;font-weight:700!important;text-transform:uppercase;letter-spacing:.5px;}}
[data-testid="stSidebar"] [data-baseweb="select"]>div{{background:rgba(255,255,255,0.13)!important;border:1px solid rgba(255,255,255,0.25)!important;border-radius:8px!important;}}
[data-testid="stSidebar"] [data-baseweb="select"] *{{color:white!important;background:transparent!important;}}
[data-testid="stSidebar"] [data-baseweb="tag"]{{background:rgba(255,255,255,0.28)!important;border-radius:5px!important;}}
[data-testid="stSidebar"] input{{color:white!important;caret-color:white!important;}}
[data-testid="stSidebar"] input::placeholder{{color:rgba(255,255,255,0.45)!important;}}
[data-baseweb="popover"] ul{{background:{R1}!important;}}
[data-baseweb="popover"] li{{color:white!important;background:{R1}!important;}}
[data-baseweb="popover"] li:hover{{background:{RD}!important;}}
[data-testid="stSidebar"] .stButton>button{{background:rgba(255,255,255,0.18)!important;color:white!important;border:1px solid rgba(255,255,255,0.35)!important;border-radius:8px!important;font-weight:700!important;width:100%;}}
[data-testid="stSidebar"] hr{{border-color:rgba(255,255,255,0.2)!important;margin:10px 0!important;}}
.ph{{background:linear-gradient(90deg,{RD} 0%,{R1} 100%);padding:18px 26px;border-radius:14px;display:flex;align-items:center;gap:16px;margin-bottom:20px;box-shadow:0 4px 18px rgba(200,16,46,0.28);}}
.ph h1{{color:white;margin:0;font-size:1.55rem;font-weight:800;}}
.ph p{{color:rgba(255,255,255,.7);margin:3px 0 0 0;font-size:.8rem;}}
.kpi{{background:white;border-radius:12px;padding:16px 18px;border-left:4px solid {R1};box-shadow:0 2px 10px rgba(0,0,0,.07);}}
.kpi.d{{border-left-color:{RD};}} .kpi.g{{border-left-color:#059669;}}
.kpi.o{{border-left-color:#f97316;}} .kpi.s{{border-left-color:#64748b;}}
.kpi-l{{font-size:.68rem;font-weight:700;color:{G2};text-transform:uppercase;letter-spacing:.5px;margin:0;}}
.kpi-v{{font-size:1.8rem;font-weight:800;color:#0f172a;margin:4px 0 0 0;line-height:1;}}
.stTabs [data-baseweb="tab-list"]{{background:white;border-radius:12px;padding:5px;box-shadow:0 2px 8px rgba(0,0,0,.08);gap:3px;}}
.stTabs [data-baseweb="tab"]{{font-weight:600;font-size:.82rem;border-radius:9px;padding:7px 16px;color:{G2}!important;}}
.stTabs [aria-selected="true"]{{background:{R1}!important;color:white!important;}}
.bsi{{background:#dcfce7;color:#166534;border-radius:5px;padding:2px 8px;font-size:.7rem;font-weight:600;margin:2px;display:inline-block;}}
.bno{{background:#fee2e2;color:#991b1b;border-radius:5px;padding:2px 8px;font-size:.7rem;font-weight:600;margin:2px;display:inline-block;}}
div[data-testid="stDataFrame"]{{border-radius:12px;overflow:hidden;}}
.stDownloadButton>button{{background:{R1}!important;color:white!important;border:none!important;border-radius:8px!important;font-weight:700!important;}}
.stTextInput input{{border-radius:8px!important;border:2px solid #fecdd3!important;}}
.stTextInput input:focus{{border-color:{R1}!important;}}
[data-testid="stStatusWidget"]{{display:none!important;}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# MAPEADO DE COLUMNAS
# ══════════════════════════════════════════════
C = {
    "item":         "ITEM",
    "almacencod":   "ALMACENCODIGO",
    "stock":        "STOCKACTUAL",
    "desc":         "ITEM_DESCRIPCION",
    "marca":        "MARCA",
    "licencia":     "LICENCIA",
    "linea":        "LINEA",
    "familia":      "FAMILIA",
    "subfamilia":   "SUBFAMILIA",
    "color":        "COLOR",
    "temporada":    "TEMPORADA",
    "sucursal":     "SUCURSAL",
    "canal":        "CANAL_VENTAS",
    "ubi":          "UBI_RESUMEN",
    "ubicacion":    "UBICACION",
    "region":       "REGION",
    "cluster":      "CLUSTER",
    "metraje":      "METRAJE",
    "pvp":          "PVP",
    "cod_prom":     "COD_PROM",
    "promo":        "PROMO",
    "dsct":         "DSCT",
    "campana":      "CAMPANA",
    "vigencia":     "VIGENCIA"
}

TIENDAS_UBI = ["TIENDAS", "TIENDAS TOGO"]
ALMA_PRINC  = "ALMA. PRINCIPAL"
ALMA_ESP    = "ALMA. ESPERA"

# ══════════════════════════════════════════════
# CARGA DE DATOS
# ══════════════════════════════════════════════
@st.cache_data(show_spinner=False, ttl=86400)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(spreadsheet=GDRIVE_URL, worksheet=SHEET_NAME, dtype=str)
    
    def norm_col(s):
        s = str(s).strip()
        s = unicodedata.normalize("NFD", s)
        s = "".join(c for c in s if unicodedata.category(c) != "Mn")
        return s.upper().replace(" ","_").replace(".","_").replace("/","_")
    df.columns = [norm_col(c) for c in df.columns]

    for col in [C["stock"], C["pvp"], C["metraje"], C["dsct"]]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",",".",regex=False)
                       .str.replace(r"[^\d.\-]","",regex=True),
                errors="coerce").fillna(0)

    text_cols = [C["item"], C["almacencod"], C["desc"], C["marca"], C["licencia"], 
                 C["linea"], C["familia"], C["subfamilia"], C["color"], C["temporada"], 
                 C["sucursal"], C["canal"], C["ubi"], C["ubicacion"], C["region"], 
                 C["cluster"], C["cod_prom"], C["promo"], C["campana"], C["vigencia"]]
                 
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Sin dato").astype(str).str.strip()
            df.loc[df[col]=="", col] = "Sin dato"

    if C["item"] in df.columns:
        df[C["item"]] = df[C["item"]].str.split('.').str[0]
        df[C["item"]] = df[C["item"]].apply(lambda x: x.zfill(6) if x != "Sin dato" else x)

    df = df[df[C["item"]].notna() & (df[C["item"]] != "Sin dato")].copy()

    if C["canal"] in df.columns:
        df = df[df[C["canal"]] != "NO CONSIDERAR"].copy()

    cat_cols = [C["ubi"], C["region"], C["sucursal"], C["linea"], C["familia"], 
                C["marca"], C["temporada"], C["campana"], C["licencia"], C["promo"], C["vigencia"]]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df

with st.spinner("Estableciendo canal seguro con Google Drive y procesando inventario…"):
    df_raw = load_data()

# ══════════════════════════════════════════════
# HELPERS GRÁFICOS Y DE INTERFAZ
# ══════════════════════════════════════════════
PC = dict(paper_bgcolor=W, plot_bgcolor=W,
          margin=dict(l=0,r=0,t=10,b=0),
          font=dict(family="Inter", color="#0f172a"))

def kpi(col, lbl, val, cls=""):
    with col:
        st.markdown(f'<div class="kpi {cls}"><p class="kpi-l">{lbl}</p>'
                    f'<p class="kpi-v">{val}</p></div>', unsafe_allow_html=True)

def bar_h(data, y, x, cs, height=320, key=None):
    fig = px.bar(data, y=y, x=x, orientation="h", color=x,
                 color_continuous_scale=cs, height=height,
                 template="plotly_white", labels={x:"Unidades", y:""})
    fig.update_layout(**PC, coloraxis_showscale=False)
    if key:
        fig.update_layout(meta=key)
    return fig

def pie_chart(data, names, values, height=300):
    fig = px.pie(data, names=names, values=values, height=height,
                 color_discrete_sequence=[R1,RD,R2,R3,"#fca5a5","#f97316","#64748b"])
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
    fig.update_layout(**PC, showlegend=False)
    return fig

def tabla_detalle(df_in, cols_extra=None):
    base = [C["item"], C["desc"], C["marca"], C["linea"], C["familia"],
            C["color"], C["temporada"], C["stock"], C["pvp"]]
    if cols_extra:
        base += cols_extra
    cols = [c for c in base if c in df_in.columns]
    out  = df_in[cols].sort_values(C["stock"], ascending=False).copy()
    out[C["stock"]] = out[C["stock"]].astype(int)
    return out

def det(col, lbl, val):
    with col:
        st.markdown(f"""<div style='background:{BG};border-radius:8px;
            padding:10px 12px;text-align:center;'>
            <div style='font-size:.65rem;font-weight:700;color:{G2};
            text-transform:uppercase;letter-spacing:.4px;'>{lbl}</div>
            <div style='font-size:.95rem;font-weight:700;color:#0f172a;
            margin-top:3px;'>{val}</div></div>""",
            unsafe_allow_html=True)

# ══════════════════════════════════════════════
# SIDEBAR (FILTROS INTERACTIVOS SINCRONIZADOS)
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:22px 0 14px 0;'>
        <div style='font-size:2.8rem;'>🎒</div>
        <div style='font-weight:800;font-size:1.25rem;color:white;letter-spacing:1px;margin-top:4px;'>PORTA</div>
        <div style='font-size:.7rem;color:rgba(255,255,255,.55);letter-spacing:.3px;margin-top:3px;'>CONTROL DE STOCK</div>
    </div><hr>""", unsafe_allow_html=True)

    if st.button("🔄 Actualizar datos", use_container_width=True):
        st.cache_data.clear()
        # Limpiamos también el estado de filtros para un reseteo total y limpio
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)

    # Definición de las dimensiones clave mapeadas para la automatización del bucle
    FILTROS_CONFIG = [
        {"label": "Ubicación / Canal", "col": C["ubi"], "key": "sf_ubi"},
        {"label": "Región",             "col": C["region"], "key": "sf_region"},
        {"label": "Sucursal / Tienda",  "col": C["sucursal"], "key": "sf_sucursal"},
        {"label": "Línea",              "col": C["linea"], "key": "sf_linea"},
        {"label": "Familia",            "col": C["familia"], "key": "sf_familia"},
        {"label": "Marca",              "col": C["marca"], "key": "sf_marca"},
        {"label": "Licencia",           "col": C["licencia"], "key": "sf_licencia"},
        {"label": "Temporada",          "col": C["temporada"], "key": "sf_temporada"},
        {"label": "Campaña",            "col": C["campana"], "key": "sf_campana"},
        {"label": "Promo",              "col": C["promo"], "key": "sf_promo"},
    ]

    # Inicializamos las variables de control en session_state si no existen
    for f in FILTROS_CONFIG:
        if f["key"] not in st.session_state:
            st.session_state[f["key"]] = []

    # Construcción dinámica de las opciones respetando la exclusión de su propio filtro (Cross-Filtering)
    for i, f in enumerate(FILTROS_CONFIG):
        if i == 3:  # Separador visual entre estructura comercial y atributos de producto
            st.markdown("<hr>", unsafe_allow_html=True)
            
        # Calculamos la máscara combinando todos los filtros ACTIVOS excepto el actual
        sub_mask = pd.Series(True, index=df_raw.index)
        for f_other in FILTROS_CONFIG:
            if f_other["key"] != f["key"] and st.session_state[f_other["key"]]:
                sub_mask &= df_raw[f_other["col"]].isin(st.session_state[f_other["key"]])
        
        # Extraemos las opciones válidas basadas en la exclusión cruzada
        opciones = sorted(df_raw.loc[sub_mask, f["col"]].dropna().unique().tolist())
        
        # El widget lee y escribe directamente en el session_state de forma síncrona
        st.multiselect(
            label=f["label"],
            options=opciones,
            key=f["key"],
            placeholder="Todas"
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    solo_stock = st.checkbox("Solo con stock > 0", key="sf_solo_stock")

    # Construcción de la máscara final global para filtrar todo el set de datos
    m_global = pd.Series(True, index=df_raw.index)
    for f in FILTROS_CONFIG:
        if st.session_state[f["key"]]:
            m_global &= df_raw[f["col"]].isin(st.session_state[f["key"]])
            
    if solo_stock:
        m_global &= (df_raw[C["stock"]] > 0)

    st.markdown(f"""
    <div style='text-align:center;margin-top:10px;background:rgba(255,255,255,.14);
                border-radius:10px;padding:10px 8px;'>
        <div style='font-size:1.4rem;font-weight:800;color:white;'>{m_global.sum():,}</div>
        <div style='font-size:.68rem;color:rgba(255,255,255,.65);'>de {len(df_raw):,} registros</div>
    </div>""", unsafe_allow_html=True)

# Asignación del DataFrame global filtrado
df = df_raw[m_global]

# ══════════════════════════════════════════════
# HEADER + PANELES DE KPIs GENERALES
# ══════════════════════════════════════════════
st.markdown(f"""
<div class="ph">
    <div style='font-size:2.4rem;'>🎒</div>
    <div>
        <h1>Porta · Control de Stock (Cloud Secure DB)</h1>
        <p>{m_global.sum():,} registros &nbsp;·&nbsp;
           {df[C['sucursal']].nunique()} ubicaciones &nbsp;·&nbsp;
           {df[C['item']].nunique():,} SKUs &nbsp;·&nbsp;
           {int(df[C['stock']].sum()):,} unidades</p>
    </div>
</div>""", unsafe_allow_html=True)

c1,c2,c3,c4,c5 = st.columns(5)
kpi(c1, "Stock Tiendas", f"{int(df[df[C['ubi']].isin(TIENDAS_UBI)][C['stock']].sum()):,}")
kpi(c2, "Almacén Principal", f"{int(df[df[C['ubi']]==ALMA_PRINC][C['stock']].sum()):,}", "d")
kpi(c3, "Almacén Espera", f"{int(df[df[C['ubi']]==ALMA_ESP][C['stock']].sum()):,}", "o")
kpi(c4, "En Ruta", f"{int(df[df[C['ubi']]=='EN RUTA'][C['stock']].sum()):,}", "s")
kpi(c5, "SKUs únicos", f"{df[C['item']].nunique():,}", "g")

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# VISTAS DE PESTAÑAS (TABS)
# ══════════════════════════════════════════════
tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "🔍 Buscar Producto",
    "🏪 Vista por Tienda",
    "📦 Almacén Principal",
    "🏷️ Promos",
    "📅 Temporada",
    "📋 Tabla Completa",
])

# TAB 1 — BUSCAR PRODUCTO
with tab1:
    buscar = st.text_input("Buscar", placeholder="🔎  Escribe código, nombre, color o marca…", label_visibility="collapsed")

    if not buscar:
        df_t0   = df[df[C["ubi"]].isin(TIENDAS_UBI)]
        todas0  = sorted(df_t0[C["sucursal"]].astype(str).unique())
        n0      = len(todas0)
        if n0 > 0:
            pos0 = df_t0[df_t0[C["stock"]]>0].groupby(C["item"])[C["sucursal"]].nunique()
            pa,pb,pc2 = st.columns(3)
            kpi(pa, "SKUs en TODAS las tiendas",  f"{int((pos0==n0).sum()):,}", "g")
            kpi(pb, "SKUs en ALGUNAS tiendas",    f"{int(((pos0>0)&(pos0<n0)).sum()):,}", "o")
            kpi(pc2,"SKUs sin stock en tiendas",  f"{int(df_t0[df_t0[C['stock']]==0][C['item']].nunique()):,}")
            st.markdown("<br>", unsafe_allow_html=True)
            st.info("👆 Escribe en el buscador para ver el detalle de un producto.")
    else:
        b = buscar.strip().lower()
        mask_b = (df[C["item"]].str.lower().str.contains(b, na=False) |
                  df[C["desc"]].str.lower().str.contains(b, na=False) |
                  df[C["color"]].str.lower().str.contains(b, na=False) |
                  df[C["marca"]].str.lower().str.contains(b, na=False))
        res = df[mask_b]

        if res.empty:
            st.warning(f"No se encontró: **{buscar}**")
        else:
            items_f = res[[C["item"],C["desc"]]].drop_duplicates()
            st.caption(f"{len(items_f)} SKU(s) encontrados")

            for _, ir in items_f.head(10).iterrows():
                idf = res[res[C["item"]]==ir[C["item"]]]
                with st.expander(f"**{ir[C['item']]}** — {ir[C['desc']]}  ·  🗂️ {int(idf[C['stock']].sum()):,} uds totales", expanded=len(items_f)==1):
                    r0 = idf.iloc[0]
                    d1,d2,d3,d4,d5 = st.columns(5)
                    det(d1,"Marca",     r0.get(C["marca"],"—"))
                    det(d2,"Línea",     r0.get(C["linea"],"—"))
                    det(d3,"Familia",   r0.get(C["familia"],"—"))
                    det(d4,"Color",     r0.get(C["color"],"—"))
                    det(d5,"Temporada", r0.get(C["temporada"],"—"))

                    st.markdown("<br>", unsafe_allow_html=True)
                    cl,cr = st.columns([3,2])
                    with cl:
                        st.markdown("**Stock por Sucursal**")
                        tbl = (idf.groupby([C["sucursal"],C["ubi"],C["region"]])
                                  [C["stock"]].sum().reset_index()
                                  .sort_values(C["stock"], ascending=False))
                        tbl.columns = ["Sucursal","Canal","Región","Stock"]
                        tbl["Stock"] = tbl["Stock"].astype(int)
                        def cs2(v):
                            if v==0:  return "background:#fee2e2"
                            elif v<5: return "background:#fef9c3"
                            else:     return "background:#dcfce7"
                        st.dataframe(
                            tbl.style.map(cs2, subset=["Stock"]),
                            use_container_width=True,
                            height=min(400,len(tbl)*38+40), hide_index=True)
                    with cr:
                        tc = tbl[tbl["Stock"]>0].sort_values("Stock", ascending=True)
                        if not tc.empty:
                            fig = px.bar(tc, y="Sucursal", x="Stock", orientation="h",
                                         color="Stock",
                                         color_continuous_scale=[[0,"#fecdd3"],[1,R1]],
                                         height=min(380,len(tc)*38+40),
                                         template="plotly_white",
                                         labels={"Stock":"Unidades","Sucursal":""})
                            fig.update_layout(**PC, coloraxis_showscale=False)
                            st.plotly_chart(fig, use_container_width=True)

                    df_ti   = idf[idf[C["ubi"]].isin(TIENDAS_UBI)]
                    todas_t = sorted(df[df[C["ubi"]].isin(TIENDAS_UBI)][C["sucursal"]].astype(str).unique())
                    con_s   = sorted(df_ti[df_ti[C["stock"]]>0][C["sucursal"]].astype(str).unique())
                    sin_s   = [t for t in todas_t if t not in con_s]
                    cob     = int(len(con_s)/len(todas_t)*100) if todas_t else 0
                    cob_c   = "#059669" if cob==100 else ("#f97316" if cob>=50 else R1)

                    st.markdown(f"""
                    <div style='margin-top:10px;background:white;border-radius:10px;
                                padding:14px 18px;box-shadow:0 1px 6px rgba(0,0,0,.07);'>
                        <div style='display:flex;justify-content:space-between;
                                    align-items:center;margin-bottom:8px;'>
                            <span style='font-weight:700;'>Presencia en tiendas</span>
                            <span style='font-weight:800;font-size:1.1rem;color:{cob_c};'>
                                {cob}%
                                <span style='font-size:.75rem;color:{G2};font-weight:500;'>
                                    ({len(con_s)}/{len(todas_t)})</span></span>
                        </div>
                        <div style='margin-bottom:5px;'>
                            {''.join(f'<span class="bsi">✓ {t}</span>' for t in con_s) or '<span style="color:#64748b;font-size:.8rem;">Sin stock en tiendas</span>'}
                        </div>
                        <div>
                            {''.join(f'<span class="bno">✗ {t}</span>' for t in sin_s) or f'<span style="color:#059669;font-weight:700;">✅ En todas las tiendas</span>'}
                        </div>
                    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — VISTA POR TIENDA
# ══════════════════════════════════════════════
with tab2:
    TEMPORADAS_VIGENTES = ["TEM - 2026 (3)", "TEM - 2026 (2)", "TEM - 2026 (1)", "TEM - 2025 (4)"]

    df_solo_tiendas = df[df[C["ubi"]].isin(TIENDAS_UBI)]
    tiendas_disp = sorted(df_solo_tiendas[C["sucursal"]].astype(str).unique())
    
    sel_t = st.selectbox(
        "Tienda", 
        tiendas_disp, 
        key="sel_tienda_tab2", 
        label_visibility="collapsed", 
        placeholder="Selecciona una tienda…"
    )
    
    if sel_t:
        dt = df_solo_tiendas[df_solo_tiendas[C["sucursal"]].astype(str) == sel_t]
        
        mask_obsoleto = ~dt[C["temporada"]].isin(TEMPORADAS_VIGENTES)
        
        stock_total = int(dt[C["stock"]].sum())
        skus_unicos = dt[C["item"]].nunique()
        stock_obsoleto = int(dt[mask_obsoleto][C["stock"]].sum())
        porcentaje_obsoleto = (stock_obsoleto / stock_total * 100) if stock_total > 0 else 0
        
        ta, tb2, tc2, td2 = st.columns(4)
        kpi(ta,  "Stock Total",       f"{stock_total:,}")
        kpi(tb2, "SKUs Únicos",       f"{skus_unicos:,}", "d")
        kpi(tc2, "Stock Obsoleto",     f"{stock_obsoleto:,}", "o")
        kpi(td2, "% Obsolescencia",    f"{porcentaje_obsoleto:.1f}%", "s" if porcentaje_obsoleto < 30 else "d")
        
        st.markdown("<br>", unsafe_allow_html=True)

        ca2, cb3 = st.columns([2, 1])
        with ca2:
            st.markdown("**Por Familia**")
            bf = (dt.groupby(C["familia"])[C["stock"]].sum().reset_index().query(f"{C['stock']} > 0").sort_values(C["stock"], ascending=True))
            st.plotly_chart(bar_h(bf, C["familia"], C["stock"], [[0, "#fecdd3"], [1, R1]], max(280, len(bf) * 34), key="graph_bar_tab2"), use_container_width=True)
        with cb3:
            st.markdown("**Por Línea**")
            bl = (dt.groupby(C["linea"])[C["stock"]].sum().reset_index().sort_values(C["stock"], ascending=False))
            st.plotly_chart(pie_chart(bl, C["linea"], C["stock"]), use_container_width=True)

        st.markdown("**Productos con stock en tienda**")
        
        dt2 = tabla_detalle(dt[dt[C["stock"]] > 0], cols_extra=[C["promo"], C["dsct"]])
        
        df_styled = dt2.style.format({
            C["dsct"]: lambda x: f"{int(round(float(x) * 100))}%" if pd.notnull(x) and float(x) != 0 else "0%",
            C["pvp"]: "{:.2f}"
        })
        
        st.dataframe(df_styled, use_container_width=True, height=400, hide_index=True)
        st.download_button("⬇️ Exportar Tienda", dt2.to_csv(index=False).encode("utf-8-sig"), f"porta_{sel_t}.csv", "text/csv")

# TAB 3 — ALMACÉN PRINCIPAL
with tab3:
    dap = df[df[C["ubi"]]==ALMA_PRINC]
    st.markdown("#### Almacén Principal")

    if dap.empty:
        st.info("Sin registros en la selección actual.")
    else:
        a1,a2,a3 = st.columns(3)
        kpi(a1,"Stock total",  f"{int(dap[C['stock']].sum()):,}", "d")
        kpi(a2,"SKUs únicos",  f"{dap[C['item']].nunique():,}")
        kpi(a3,"Familias",     f"{dap[dap[C['stock']]>0][C['familia']].nunique()}")
        st.markdown("<br>", unsafe_allow_html=True)

        fam_stock = (dap.groupby(C["familia"])[C["stock"]].sum().reset_index().query(f"{C['stock']} > 0").sort_values(C["stock"], ascending=True))

        ca3,cb4 = st.columns(2)
        with ca3:
            st.markdown("**Familias con stock**")
            if not fam_stock.empty:
                st.plotly_chart(bar_h(fam_stock, C["familia"], C["stock"], [[0,"#fecdd3"],[1,RD]], max(280, len(fam_stock)*34), key="graph_bar_tab3"), use_container_width=True)
        with cb4:
            st.markdown("**Por Línea**")
            al = (dap[dap[C["stock"]]>0].groupby(C["linea"])[C["stock"]].sum().reset_index().sort_values(C["stock"], ascending=False))
            if not al.empty:
                st.plotly_chart(pie_chart(al, C["linea"], C["stock"]), use_container_width=True)

        st.markdown("**Detalle**")
        dap2 = tabla_detalle(dap[dap[C["stock"]]>0])
        st.dataframe(dap2, use_container_width=True, height=420, hide_index=True)
        st.download_button("⬇️ Exportar Almacén", dap2.to_csv(index=False).encode("utf-8-sig"), "porta_alma_principal.csv","text/csv")

# TAB 4 — PROMOS
with tab4:
    st.markdown("#### Detalle por Promoción")

    promos_disp = sorted(df[df[C["promo"]] != "SIN DSCT"][C["promo"]].unique().tolist())
    sel_promo = st.selectbox(
        "Selecciona una promo", 
        promos_disp, 
        key="sel_promo_tab4", 
        label_visibility="collapsed", 
        placeholder="Selecciona una promoción…"
    )
    
    if sel_promo:
        dp = df[df[C["promo"]] == sel_promo]

        p1, p2, p3 = st.columns(3)
        kpi(p1, "Stock total",      f"{int(dp[C['stock']].sum()):,}")
        kpi(p2, "SKUs en promo",    f"{dp[C['item']].nunique():,}", "d")
        kpi(p3, "Unidades s/stock", f"{int((dp.groupby(C['item'])[C['stock']].sum() == 0).sum()):,}", "s")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("**Ítems incluidos en la promo**")
        
        dp2 = tabla_detalle(dp, cols_extra=[C["cod_prom"], C["dsct"]])
        
        dp2_styled = dp2.style.format({
            C["dsct"]: lambda x: f"{int(round(float(x) * 100))}%" if pd.notnull(x) and float(x) != 0 else "0%",
            C["pvp"]: "{:.2f}"
        })
        
        st.dataframe(dp2_styled, use_container_width=True, height=500, hide_index=True)
        st.download_button("⬇️ Exportar promo", dp2.to_csv(index=False).encode("utf-8-sig"), f"porta_promo.csv", "text/csv")
      
# TAB 5 — TEMPORADA
with tab5:
    st.markdown("#### Stock por Temporada")

    ca5,cb5 = st.columns([2,1])
    with ca5:
        bt = (df.groupby(C["temporada"])[C["stock"]].sum().reset_index().sort_values(C["stock"], ascending=False).head(16))
        fig_t = px.bar(bt, x=C["temporada"], y=C["stock"], color=C["stock"], color_continuous_scale=[[0,"#fecdd3"],[1,R1]], height=340, template="plotly_white", labels={C["stock"]:"Unidades", C["temporada"]:""})
        fig_t.update_layout(**PC, coloraxis_showscale=False, xaxis_tickangle=-35)
        st.plotly_chart(fig_t, use_container_width=True)

    with cb5:
        bc = (df.groupby(C["campana"])[C["stock"]].sum().reset_index().sort_values(C["stock"], ascending=False))
        st.plotly_chart(pie_chart(bc, C["campana"], C["stock"], height=340), use_container_width=True)

    st.markdown("---")
    st.markdown("#### Detalle por Temporada")
    temps_disp = sorted(df[C["temporada"]].unique().tolist())
    sel_temp   = st.selectbox("Selecciona temporada", temps_disp, key="sel_temp_tab5", label_visibility="collapsed", placeholder="Selecciona una temporada…")
    if sel_temp:
        dtemp = df[df[C["temporada"]]==sel_temp]
        t1,t2,t3 = st.columns(3)
        kpi(t1,"Stock total",  f"{int(dtemp[C['stock']].sum()):,}")
        kpi(t2,"SKUs únicos",  f"{dtemp[C['item']].nunique():,}","d")
        kpi(t3,"Familias",     f"{dtemp[dtemp[C['stock']]>0][C['familia']].nunique()}","g")
        st.markdown("<br>", unsafe_allow_html=True)

        cta,ctb = st.columns([2,1])
        with cta:
            bf_t = (dtemp.groupby(C["familia"])[C["stock"]].sum().reset_index().query(f"{C['stock']} > 0").sort_values(C["stock"], ascending=True))
            if not bf_t.empty:
                st.plotly_chart(bar_h(bf_t, C["familia"], C["stock"], [[0,"#fecdd3"],[1,R1]], max(280,len(bf_t)*34), key="graph_bar_tab5"), use_container_width=True)
        with ctb:
            bl_t = (dtemp.groupby(C["linea"])[C["stock"]].sum().reset_index().sort_values(C["stock"], ascending=False))
            if not bl_t.empty:
                st.plotly_chart(pie_chart(bl_t, C["linea"], C["stock"]), use_container_width=True)

        dtemp2 = tabla_detalle(dtemp[dtemp[C["stock"]]>0])
        st.dataframe(dtemp2, use_container_width=True, height=380, hide_index=True)
        st.download_button("⬇️ Exportar temporada", dtemp2.to_csv(index=False).encode("utf-8-sig"), f"porta_temp.csv","text/csv")

# TAB 6 — TABLA COMPLETA
with tab6:
    show = [c for c in C.values() if c in df.columns]
    ds = df[show].sort_values(C["stock"], ascending=False).copy()
    ds[C["stock"]] = ds[C["stock"]].astype(int)
    st.dataframe(ds, use_container_width=True, height=560, hide_index=True)
    st.download_button("⬇️ Exportar todo", ds.to_csv(index=False).encode("utf-8-sig"), "porta_stock.csv","text/csv")
