import streamlit as st
import pandas as pd
import gspread
import matplotlib.pyplot as plt
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- Konfigurasi kredensial Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if "google_service_account" in st.secrets:
    creds_dict = dict(st.secrets["google_service_account"])
else:
    creds_dict = {
        "type": "service_account",
        "project_id": "agustusanpkl",
        "private_key_id": "ee9d839111c388cdc3f331375c1df864e4f4f34a",
        "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC3SAWqXiGdatuL
... (isi disensor)
VrleKw==
-----END PRIVATE KEY-----""",
        "client_email": "streamlit-access@agustusanpkl.iam.gserviceaccount.com",
        "client_id": "108305191571808927807",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-access%40agustusanpkl.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
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
    lomba = st.text_input("Nama Perlombaan (bebas diisi)")

    submit = st.form_submit_button("Simpan")

    if submit and nama and lomba.strip():
        row = [nama, umur, f"{rt}/{rw}", lomba.strip(), 0]

        try:
            sheet.append_row(row)
        except Exception as e:
            st.error(f"Gagal menyimpan ke Google Sheets: {e}")

        try:
            df = pd.read_csv(CSV_FILE)
            df.loc[len(df)] = row
        except:
            df = pd.DataFrame([row], columns=["Nama", "Umur", "RT/RW", "Lomba", "Nilai"])
        df.to_csv(CSV_FILE, index=False)
        st.success("✅ Data berhasil disimpan!")

# --- TAMPILKAN & KELOLA PESERTA ---
st.subheader("📑 Data Peserta")
try:
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df)

    # Tombol Unduh CSV
    st.download_button(
        "⬇️ Unduh Data CSV",
        df.to_csv(index=False),
        file_name="data_peserta.csv",
        mime="text/csv"
    )

    # --- Fitur Edit ---
    st.markdown("### ✏️ Edit Data")
    selected_name = st.selectbox("Pilih Nama untuk Diedit", df["Nama"].unique())
    if selected_name:
        selected_data = df[df["Nama"] == selected_name].iloc[0]
        new_umur = st.number_input("Edit Umur", 5, 100, int(selected_data["Umur"]))
        new_rtrw = st.text_input("Edit RT/RW", selected_data["RT/RW"])
        new_lomba = st.text_input("Edit Lomba", selected_data["Lomba"])

        if st.button("💾 Simpan Perubahan"):
            df.loc[df["Nama"] == selected_name, ["Umur", "RT/RW", "Lomba"]] = [new_umur, new_rtrw, new_lomba]
            df.to_csv(CSV_FILE, index=False)

            try:
                sheet.clear()
                sheet.append_row(["Nama", "Umur", "RT/RW", "Lomba", "Nilai"])
                for i in df.values.tolist():
                    sheet.append_row(i)
            except Exception as e:
                st.error(f"Gagal update Google Sheets: {e}")

            st.success("✅ Data berhasil diubah!")

    # --- Fitur Hapus ---
    st.markdown("### 🗑️ Hapus Data")
    nama_hapus = st.selectbox("Pilih Nama untuk Dihapus", df["Nama"].unique(), key="hapus")
    if st.button("Hapus Peserta"):
        df = df[df["Nama"] != nama_hapus]
        df.to_csv(CSV_FILE, index=False)

        try:
            sheet.clear()
            sheet.append_row(["Nama", "Umur", "RT/RW", "Lomba", "Nilai"])
            for i in df.values.tolist():
                sheet.append_row(i)
        except Exception as e:
            st.error(f"Gagal update Google Sheets: {e}")

        st.success(f"✅ Data peserta '{nama_hapus}' telah dihapus!")

except:
    st.warning("⚠️ Belum ada data peserta.")

# --- INPUT NILAI ---
st.header("🏅 Input Nilai Peserta")
try:
    df = pd.read_csv(CSV_FILE)
    nama_pilih = st.selectbox("Pilih Peserta", df["Nama"].unique(), key="nilai")
    nilai = st.slider("Nilai", 0, 100)
    if st.button("💾 Simpan Nilai"):
        df.loc[df["Nama"] == nama_pilih, "Nilai"] = nilai
        df.to_csv(CSV_FILE, index=False)

        try:
            sheet.clear()
            sheet.append_row(["Nama", "Umur", "RT/RW", "Lomba", "Nilai"])
            for i in df.values.tolist():
                sheet.append_row(i)
        except Exception as e:
            st.error(f"Gagal update Google Sheets: {e}")

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
