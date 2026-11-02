import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).with_name("drainsafe.db")

st.set_page_config(
    page_title="DrainSafe | Monitoring Drainase",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Database: tetap menggunakan struktur database sebelumnya ----------
def connect_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            reporter TEXT,
            issue TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            photo_name TEXT,
            status TEXT NOT NULL DEFAULT 'Belum Ditangani',
            officer_note TEXT DEFAULT ''
        )
    """)
    conn.commit()
    return conn


conn = connect_db()


def add_report(reporter, issue, location, description, photo_name):
    conn.execute(
        """INSERT INTO reports
        (created_at, reporter, issue, location, description, photo_name, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.now().strftime("%d-%m-%Y %H:%M"), reporter, issue,
            location, description, photo_name, "Belum Ditangani",
        ),
    )
    conn.commit()


def load_reports():
    return pd.read_sql_query("SELECT * FROM reports ORDER BY id DESC", conn)


def update_report(report_id, status, note):
    conn.execute(
        "UPDATE reports SET status = ?, officer_note = ? WHERE id = ?",
        (status, note, int(report_id)),
    )
    conn.commit()


# ---------- Styling ----------
st.markdown("""
<style>
    :root {
        --navy: #14213d;
        --navy2: #1d3557;
        --blue: #1976d2;
        --blue2: #2f8bea;
        --page: #f3f6fc;
        --ink: #17243b;
        --muted: #718096;
    }
    .stApp { background: var(--page); color: var(--ink); }
    .block-container { padding-top: 1.35rem; padding-bottom: 2.5rem; max-width: 1500px; }
    h1, h2, h3 { color: var(--ink); letter-spacing: -.45px; }

    /* Sidebar navy seperti panel petugas pada referensi */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #14213d 0%, #1d3557 58%, #10213d 100%);
        border-right: 1px solid rgba(255,255,255,.08);
    }
    section[data-testid="stSidebar"] > div { background: transparent; }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stSidebar"] small { color: #d4e0f1 !important; }
    .brand-card {
        padding: 18px 15px 17px; margin: 4px 0 23px;
        border: 1px solid rgba(255,255,255,.13); border-radius: 17px;
        background: rgba(255,255,255,.075);
    }
    .brand-title { color: white; font-size: 1.55rem; font-weight: 850; letter-spacing: -.6px; margin: 0; }
    .brand-subtitle { color: #c5d8ee; font-size: .77rem; margin: 5px 0 0; line-height: 1.5; }
    .menu-caption { color: #91abc9; font-size: .68rem; font-weight: 800; letter-spacing: 1.6px; text-transform: uppercase; margin: 0 0 10px 4px; }
    section[data-testid="stSidebar"] div[role="radiogroup"] { gap: 8px; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        background: rgba(255,255,255,.045); border: 1px solid rgba(255,255,255,.06);
        border-radius: 11px; padding: 10px 12px; transition: all .18s ease;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,.13); border-color: rgba(255,255,255,.2);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(100deg, #2588e8, #1768b8);
        border: 1px solid rgba(255,255,255,.22); box-shadow: 0 5px 15px rgba(0,0,0,.18);
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label p { color: #e7f0fc !important; font-weight: 600; font-size: .9rem; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { color: white !important; font-weight: 750; }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
    .sidebar-note { padding: 12px 13px; border-radius: 12px; background: rgba(255,255,255,.075); color: #d4e0f1; font-size: .75rem; line-height: 1.55; border: 1px solid rgba(255,255,255,.09); }
    .sidebar-footer { color: #9bb0ca; font-size: .71rem; line-height: 1.6; margin-top: 15px; }

    /* Header dan kartu dashboard */
    .topline { display:flex; justify-content:space-between; align-items:center; gap:12px; margin: 0 0 1rem; color:#718096; font-size:.83rem; }
    .welcome {
        background: linear-gradient(110deg, #ffffff 0%, #eaf3ff 100%);
        border: 1px solid #e0eaf7; border-radius: 18px; padding: 22px 25px;
        margin-bottom: 18px; box-shadow: 0 7px 22px rgba(25,55,90,.045);
    }
    .welcome h1 { margin:0; font-size:1.9rem; color:#172b4d; }
    .welcome p { margin:.35rem 0 0; color:#667892; font-size:.94rem; }
    .stat-card {
        min-height: 112px; padding: 16px 17px; border-radius: 15px;
        border: 1px solid #e4eaf3; box-shadow: 0 5px 16px rgba(30,55,90,.045);
        background:#fff; display:flex; align-items:center; gap:13px;
    }
    .stat-icon { width:48px; height:48px; flex:0 0 48px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:1.45rem; }
    .stat-label { color:#6b7890; font-size:.78rem; font-weight:650; margin-bottom:5px; }
    .stat-value { color:#172b4d; font-size:1.75rem; line-height:1.1; font-weight:850; }
    .stat-foot { color:#8a96a8; font-size:.68rem; margin-top:5px; }
    .panel { background:white; border:1px solid #e4eaf3; border-radius:16px; padding:18px; box-shadow:0 5px 18px rgba(30,55,90,.04); height:100%; }
    .panel-title { color:#1b2b46; font-size:1.02rem; font-weight:800; margin:0 0 13px; }
    .water-number { font-size:2rem; font-weight:850; color:#172b4d; margin:3px 0 0; }
    .water-status { font-size:1.25rem; font-weight:850; margin-top:4px; }
    .water-track { height:12px; border-radius:20px; background:#e9eef6; overflow:hidden; margin:15px 0 9px; }
    .water-fill { height:100%; border-radius:20px; }
    .threshold { color:#718096; font-size:.72rem; line-height:1.55; }
    .report-item { padding:11px 0; border-bottom:1px solid #edf1f6; }
    .report-item:last-child { border-bottom:0; padding-bottom:0; }
    .report-id { color:#1c3558; font-size:.82rem; font-weight:800; }
    .report-detail { color:#718096; font-size:.75rem; margin-top:3px; }
    .status-pill { display:inline-block; padding:5px 9px; border-radius:20px; font-size:.68rem; font-weight:750; white-space:nowrap; }
    .pill-wait { color:#8a5a00; background:#fff2d9; }
    .pill-work { color:#1558a6; background:#e3f0ff; }
    .pill-done { color:#08764c; background:#dcf8eb; }

    /* Form, tombol, tabel */
    div[data-testid="stMetric"] { background:white; border:1px solid #e4eaf3; padding:15px; border-radius:14px; box-shadow:0 4px 13px rgba(25,55,90,.035); }
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button { border-radius:10px; font-weight:700; padding:.55rem 1rem; }
    div[data-testid="stDataFrame"] { border:1px solid #e1e8f0; border-radius:12px; overflow:hidden; }
    div[data-testid="stForm"] { background:white; padding:18px; border:1px solid #e4eaf3; border-radius:15px; }
    @media (max-width: 700px) {
        .block-container { padding-top: .8rem; }
        .welcome { padding:17px; }
        .welcome h1 { font-size:1.5rem; }
        .stat-card { min-height:95px; padding:12px; }
    }
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.markdown("""
<div class="brand-card">
    <div class="brand-title">💧 DrainSafe</div>
    <div class="brand-subtitle">Sistem Pengaduan & Monitoring Drainase</div>
</div>
<div class="menu-caption">Menu utama</div>
""", unsafe_allow_html=True)

menu_items = {
    "Dashboard": "🏠  Dashboard",
    "Buat Pengaduan": "📝  Buat Pengaduan",
    "Cek Status Laporan": "🔎  Cek Status Laporan",
    "Monitoring Air": "🌊  Monitoring Air",
    "Kelola Laporan (Petugas)": "🧰  Kelola Laporan (Petugas)",
}
page = st.sidebar.radio(
    "Navigasi", list(menu_items.keys()),
    format_func=lambda item: menu_items[item], label_visibility="collapsed",
)
st.sidebar.markdown("""
<div class="sidebar-note">
    <b>💡 Informasi Prototype</b><br>
    Data pengaduan tersimpan secara lokal menggunakan SQLite. Pembacaan ketinggian air masih berupa simulasi.
</div>
<div class="sidebar-footer"><b>DrainSafe</b> · Prototype aplikasi monitoring drainase<br>Membantu lingkungan lebih tanggap terhadap masalah drainase.</div>
""", unsafe_allow_html=True)

reports = load_reports()
if "water_level" not in st.session_state:
    st.session_state.water_level = 35


def status_pill(status):
    if status == "Selesai":
        return '<span class="status-pill pill-done">Selesai</span>'
    if status == "Sedang Ditangani":
        return '<span class="status-pill pill-work">Sedang Ditangani</span>'
    return '<span class="status-pill pill-wait">Belum Ditangani</span>'


# ---------- Dashboard ----------
if page == "Dashboard":
    total = len(reports)
    waiting = int((reports["status"] == "Belum Ditangani").sum()) if total else 0
    process = int((reports["status"] == "Sedang Ditangani").sum()) if total else 0
    done = int((reports["status"] == "Selesai").sum()) if total else 0
    level = int(st.session_state.water_level)
    water_status = "Bahaya" if level >= 90 else "Waspada" if level >= 70 else "Siaga"
    water_color = "#dc3e45" if water_status == "Bahaya" else "#e59a22" if water_status == "Waspada" else "#159b70"
    water_bg = "#fff0f0" if water_status == "Bahaya" else "#fff6e7" if water_status == "Waspada" else "#e8f8f0"
    fill_width = min(100, max(3, level / 120 * 100))

    st.markdown(f"""
    <div class="topline"><span>DrainSafe / Dashboard</span><span>🛡️ Panel Petugas</span></div>
    <div class="welcome">
        <h1>Selamat Datang di DrainSafe!</h1>
        <p>Pantau kondisi drainase, kelola pengaduan warga, dan lihat peringatan kenaikan air dalam satu sistem.</p>
    </div>
    """, unsafe_allow_html=True)

    stat_cols = st.columns(4)
    stat_data = [
        ("📋", "Total Pengaduan", total, "Seluruh laporan masuk", "#e5f1ff", "#247bd1"),
        ("🕒", "Belum Ditangani", waiting, "Menunggu tindak lanjut", "#fff2df", "#e58a2b"),
        ("🔧", "Sedang Ditangani", process, "Dalam proses petugas", "#eaf2ff", "#477fd0"),
        ("✓", "Selesai", done, "Laporan terselesaikan", "#e3f8ee", "#1ca879"),
    ]
    for col, item in zip(stat_cols, stat_data):
        icon, label, value, foot, bg, color = item
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon" style="background:{bg};color:{color};">{icon}</div>
                <div><div class="stat-label">{label}</div><div class="stat-value">{value}</div><div class="stat-foot">{foot}</div></div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    water_col, threshold_col, latest_col = st.columns([1.05, 1.05, 1.35], gap="medium")
    with water_col:
        st.markdown(f"""
        <div class="panel">
            <div class="panel-title">💧 Status Ketinggian Air</div>
            <div style="display:flex;align-items:center;gap:12px;margin-top:18px;">
                <div style="font-size:2.5rem;">💧</div>
                <div><div class="water-status" style="color:{water_color};">{water_status}</div>
                <div class="water-number">{level} <span style="font-size:.9rem;font-weight:600;">cm</span></div></div>
            </div>
            <div class="water-track"><div class="water-fill" style="width:{fill_width}%;background:{water_color};"></div></div>
            <div class="threshold">Indikator visual berdasarkan nilai simulasi saat ini.</div>
            <div style="margin-top:13px;background:{water_bg};color:{water_color};padding:9px 10px;border-radius:9px;font-size:.75rem;font-weight:700;">
                {'🚨 Bahaya — petugas perlu segera memeriksa kondisi.' if water_status == 'Bahaya' else '⚠️ Waspada — pantau kenaikan air dan siapkan tindak lanjut.' if water_status == 'Waspada' else '✓ Siaga — ketinggian air masih di bawah ambang waspada.'}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with threshold_col:
        st.markdown("<div class='panel'><div class='panel-title'>📊 Ambang Peringatan Air</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin:14px 0 18px;padding:12px;border-radius:11px;background:#e8f8f0;'><b style='color:#159b70;'>● SIAGA</b><br><span style='color:#64748b;font-size:.82rem;'>Di bawah 70 cm</span></div>", unsafe_allow_html=True)
        st.markdown("<div style='margin:14px 0 18px;padding:12px;border-radius:11px;background:#fff5e5;'><b style='color:#d88a18;'>● WASPADA</b><br><span style='color:#64748b;font-size:.82rem;'>70–89 cm</span></div>", unsafe_allow_html=True)
        st.markdown("<div style='margin:14px 0 8px;padding:12px;border-radius:11px;background:#fff0f0;'><b style='color:#d83b45;'>● BAHAYA</b><br><span style='color:#64748b;font-size:.82rem;'>90 cm atau lebih</span></div>", unsafe_allow_html=True)
        st.caption("Batas ini masih berupa contoh dan perlu disesuaikan melalui pengujian lapangan.")
        st.markdown("</div>", unsafe_allow_html=True)
    with latest_col:
        st.markdown("<div class='panel'><div class='panel-title'>📝 Pengaduan Terbaru</div>", unsafe_allow_html=True)
        if reports.empty:
            st.info("Belum ada pengaduan. Buka menu **Buat Pengaduan** untuk menambahkan laporan.")
        else:
            for _, row in reports.head(5).iterrows():
                st.markdown(f"""
                <div class="report-item">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
                        <span class="report-id">#LP-{int(row['id']):04d} · {row['issue']}</span>
                        {status_pill(row['status'])}
                    </div>
                    <div class="report-detail">📍 {row['location']} · {row['created_at']}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Catatan: dashboard menampilkan data pengaduan dari SQLite dan nilai ketinggian air simulasi. Riwayat grafik sensor belum tersedia karena program saat ini hanya menyimpan nilai terakhir.")

# ---------- Create report ----------
elif page == "Buat Pengaduan":
    st.markdown("<div class='topline'>DrainSafe / Pengaduan</div>", unsafe_allow_html=True)
    st.title("📝 Buat Pengaduan Drainase")
    st.write("Isi formulir berikut untuk melaporkan drainase tersumbat atau rusak.")
    with st.form("report_form", clear_on_submit=True):
        reporter = st.text_input("Nama pelapor (opsional)")
        issue = st.selectbox("Jenis masalah", ["Drainase Tersumbat", "Drainase Rusak", "Air Meluap", "Masalah Lainnya"])
        location = st.text_input("Lokasi kejadian *", placeholder="Contoh: Jl. Melati, dekat nomor 12")
        description = st.text_area("Keterangan masalah", placeholder="Jelaskan kondisi drainase...")
        photo = st.file_uploader("Foto pendukung (opsional)", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("📨  Kirim Pengaduan", type="primary", use_container_width=True)
        if submitted:
            if not location.strip():
                st.error("Lokasi kejadian wajib diisi.")
            else:
                add_report(reporter.strip(), issue, location.strip(), description.strip(), photo.name if photo else "")
                latest_id = conn.execute("SELECT MAX(id) FROM reports").fetchone()[0]
                st.success("Pengaduan berhasil dicatat.")
                st.info(f"Nomor laporan Anda: **LP-{latest_id:04d}**. Simpan nomor ini untuk mengecek status laporan.")
    st.caption("Untuk prototipe ini, nama file foto dicatat, tetapi foto belum disimpan ke penyimpanan permanen.")

# ---------- Check report ----------
elif page == "Cek Status Laporan":
    st.markdown("<div class='topline'>DrainSafe / Pelacakan Laporan</div>", unsafe_allow_html=True)
    st.title("🔎 Cek Status Laporan")
    st.write("Masukkan ID angka laporan yang didapat setelah mengirim pengaduan.")
    report_id = st.number_input("ID laporan", min_value=1, step=1)
    if st.button("Cari Laporan", type="primary"):
        result = conn.execute(
            "SELECT id, created_at, issue, location, description, status, officer_note FROM reports WHERE id = ?",
            (int(report_id),),
        ).fetchone()
        if result:
            rid, created, issue, location, desc, status, note = result
            st.markdown(f"<div class='panel'><div class='panel-title'>Nomor Laporan: LP-{rid:04d}</div></div>", unsafe_allow_html=True)
            st.write(f"**Tanggal:** {created}")
            st.write(f"**Jenis masalah:** {issue}")
            st.write(f"**Lokasi:** {location}")
            st.write(f"**Keterangan:** {desc or '-'}")
            if status == "Selesai":
                st.success(f"Status: {status}")
            elif status == "Sedang Ditangani":
                st.warning(f"Status: {status}")
            else:
                st.info(f"Status: {status}")
            st.write(f"**Catatan petugas:** {note or 'Belum ada catatan.'}")
        else:
            st.error("Laporan tidak ditemukan. Periksa kembali ID laporan.")

# ---------- Water monitoring ----------
elif page == "Monitoring Air":
    st.markdown("<div class='topline'>DrainSafe / Monitoring Air</div>", unsafe_allow_html=True)
    st.title("🌊 Monitoring Ketinggian Air")
    st.write("Masukkan angka untuk simulasi sensor. Pada penerapan nyata, nilai dibaca langsung dari perangkat sensor.")
    level_input = st.number_input("Ketinggian air (cm)", min_value=0, max_value=300, value=int(st.session_state.get("water_level", 35)), step=1)
    if st.button("Perbarui Pembacaan", type="primary"):
        st.session_state.water_level = int(level_input)
        st.rerun()
    level = int(st.session_state.get("water_level", 35))
    status = "Bahaya" if level >= 90 else "Waspada" if level >= 70 else "Siaga"
    color = "#dc3e45" if status == "Bahaya" else "#e59a22" if status == "Waspada" else "#159b70"
    bg = "#fff0f0" if status == "Bahaya" else "#fff6e7" if status == "Waspada" else "#e8f8f0"
    st.markdown(f"""
    <div class="panel" style="max-width:650px;margin-top:15px;">
        <div class="panel-title">💧 Pembacaan Saat Ini</div>
        <div style="display:flex;align-items:center;gap:18px;"><div style="font-size:3rem;">💧</div>
        <div><div style="font-size:1.2rem;font-weight:800;color:{color};">{status.upper()}</div>
        <div class="water-number">{level} cm</div></div></div>
        <div style="margin-top:15px;padding:12px;border-radius:10px;background:{bg};color:{color};font-weight:700;font-size:.85rem;">
        {'🚨 Ketinggian air mencapai batas bahaya. Petugas perlu segera memeriksa lokasi.' if status == 'Bahaya' else '⚠️ Ketinggian air meningkat. Pantau kondisi dan siapkan tindak lanjut.' if status == 'Waspada' else '✓ Ketinggian air masih di bawah ambang waspada.'}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("Ambang Kategori Peringatan")
    threshold_df = pd.DataFrame({"Kategori": ["Siaga", "Waspada", "Bahaya"], "Ambang (cm)": [70, 90, 100]})
    st.bar_chart(threshold_df.set_index("Kategori"))
    st.caption("Angka ambang hanya contoh untuk demonstrasi. Sesuaikan melalui pengujian lapangan dan karakteristik selokan.")

# ---------- Officer admin ----------
elif page == "Kelola Laporan (Petugas)":
    st.markdown("<div class='topline'>DrainSafe / Panel Petugas</div>", unsafe_allow_html=True)
    st.title("🧰 Kelola Laporan — Petugas")
    st.warning("Demo tugas: halaman ini belum memakai login/otorisasi. Jangan gunakan untuk data masyarakat sungguhan sebelum keamanan ditambahkan.")
    reports = load_reports()
    if reports.empty:
        st.info("Belum ada laporan yang masuk.")
    else:
        st.dataframe(reports[["id", "created_at", "reporter", "issue", "location", "status"]], use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("Perbarui Status Laporan")
        selected_id = st.selectbox(
            "Pilih laporan", reports["id"].tolist(),
            format_func=lambda x: f"LP-{int(x):04d} — {reports.loc[reports['id'] == x, 'issue'].iloc[0]}",
        )
        current = reports.loc[reports["id"] == selected_id].iloc[0]
        status_options = ["Belum Ditangani", "Sedang Ditangani", "Selesai"]
        selected_status = st.selectbox("Status baru", status_options, index=status_options.index(current["status"]))
        note = st.text_area("Catatan petugas", value=str(current["officer_note"] or ""))
        if st.button("Simpan Perubahan", type="primary"):
            update_report(selected_id, selected_status, note.strip())
            st.success(f"Status laporan LP-{int(selected_id):04d} berhasil diperbarui.")
            st.rerun()

st.sidebar.divider()
st.sidebar.caption("DrainSafe • Prototype aplikasi monitoring drainase")
