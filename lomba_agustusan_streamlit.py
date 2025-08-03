import streamlit as st
import pandas as pd
import gspread
import matplotlib.pyplot as plt
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- Koneksi ke Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key = os.environ.get("GOOGLE_SERVICE_ACCOUNT")
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(json_key), scope)
client = gspread.authorize(creds)
sheet = client.open("Pendaftaran_Lomba").sheet1

CSV_FILE = "data_peserta.csv"

st.title("📋 Pendaftaran Lomba Agustusan Desa")

# --- FORM PENDAFTARAN ---
with st.form("form_pendaftaran"):
    nama = st.text_input("Nama")
    umur = st.number_input("Umur", 5, 100)
    rt = st.text_input("RT")
    rw = st.text_input("RW")
    lomba = st.selectbox("Pilih Lomba", ["Balap Karung", "Makan Kerupuk", "Tarik Tambang", "Panjat Pinang"])
    submit = st.form_submit_button("Simpan")

    if submit and nama:
        row = [nama, umur, f"{rt}/{rw}", lomba, 0]
        sheet.append_row(row)  # Simpan ke Google Sheets

        try:
            df = pd.read_csv(CSV_FILE)
            df.loc[len(df)] = row
        except:
            df = pd.DataFrame([row], columns=["Nama", "Umur", "RT/RW", "Lomba", "Nilai"])
        df.to_csv(CSV_FILE, index=False)
        st.success("✅ Data berhasil disimpan!")

# --- TAMPILKAN PESERTA ---
if st.button("📑 Tampilkan Semua Peserta"):
    try:
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df)
    except:
        st.warning("⚠️ Belum ada data peserta.")

# --- INPUT NILAI ---
st.header("🏅 Input Nilai Peserta")
try:
    df = pd.read_csv(CSV_FILE)
    nama_pilih = st.selectbox("Pilih Peserta", df["Nama"].unique())
    nilai = st.slider("Nilai", 0, 100)
    if st.button("💾 Simpan Nilai"):
        df.loc[df["Nama"] == nama_pilih, "Nilai"] = nilai
        df.to_csv(CSV_FILE, index=False)
        st.success("✅ Nilai berhasil disimpan!")
except:
    st.info("Belum ada data untuk dinilai.")

# --- PEMILIHAN JUARA ---
st.header("🏆 Juara per Lomba")
if st.button("🎉 Tampilkan Juara"):
    try:
        df = pd.read_csv(CSV_FILE)
        juara_df = df.sort_values(by=["Lomba", "Nilai"], ascending=[True, False])
        juara_per_lomba = juara_df.groupby("Lomba").head(3)
        st.dataframe(juara_per_lomba)
    except:
        st.warning("⚠️ Data belum lengkap.")

# --- GRAFIK JUMLAH PESERTA PER LOMBA ---
st.header("📊 Grafik Jumlah Peserta per Lomba")
try:
    df = pd.read_csv(CSV_FILE)
    peserta_per_lomba = df["Lomba"].value_counts()
    fig, ax = plt.subplots()
    peserta_per_lomba.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_xlabel("Lomba")
    ax.set_ylabel("Jumlah Peserta")
    ax.set_title("Jumlah Peserta per Lomba")
    st.pyplot(fig)
except:
    st.info("Belum ada data untuk digrafikkan.")
