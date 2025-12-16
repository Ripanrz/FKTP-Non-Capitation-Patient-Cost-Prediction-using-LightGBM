from flask import Flask, render_template, request
import pandas as pd
import joblib

app = Flask(__name__)

# --- 1. LOAD MODEL KAMU DI SINI ---
model = joblib.load('final_best_model_LGBMRegressor.pkl') 

# --- 2. DATA OPSI (HARDCODED DARI DATA KAMU) ---
# Simpan data opsi ini agar HTML tinggal meloop-nya
OPTIONS = {
    'tingkat_layanan': ['RJTP', 'RITP', 'PROMOTIF'],
    
    'gender': ['LAKI-LAKI', 'PEREMPUAN'],
    
    'tipe_faskes': [
        'KLINIK RAWAT INAP', 'DOKTER PRAKTER PERORANGAN', 'RAWAT INAP', 
        'NON RAWAT INAP', 'LABORATORIUM', 'KLINIK NON RAWAT INAP', 
        'PPK LAIN-LAIN', 'RS KELAS D PRATAMA', 'FASKES IVA/PAP SMEAR', 
        'TIDAK TERDEFINISI'
    ],
    
    'provinsi': [ # Digunakan untuk PROV_FASKES dan PROV_PESERTA (Datanya sama)
        'RIAU', 'SULAWESI SELATAN', 'KEPULAUAN BANGKA BELITUNG', 'JAWA BARAT', 'ACEH', 
        'JAWA TIMUR', 'JAWA TENGAH', 'NUSA TENGGARA BARAT', 'LAMPUNG', 'SUMATERA BARAT', 
        'BENGKULU', 'SUMATERA SELATAN', 'PAPUA', 'SULAWESI TENGGARA', 'SULAWESI UTARA', 
        'SULAWESI BARAT', 'KALIMANTAN BARAT', 'KALIMANTAN TENGAH', 'SULAWESI TENGAH', 
        'BANTEN', 'SUMATERA UTARA', 'KALIMANTAN SELATAN', 'KEPULAUAN RIAU', 
        'NUSA TENGGARA TIMUR', 'GORONTALO', 'BALI', 'KALIMANTAN TIMUR', 'JAMBI', 
        'MALUKU UTARA', 'DKI JAKARTA', 'DAERAH ISTIMEWA YOGYAKARTA', 'KALIMANTAN UTARA', 
        'PAPUA BARAT', 'MALUKU'
    ],

    'nama_tindakan': [
        'Evakuasi medis / Ambulans Darat', 'Pelayanan PNC 2 (Dua)', 'Paket Persalinan per Vaginam normal (oleh Bidan)', 
        'Pelayanan PNC 1 (Satu)', 'Pelayanan PNC 4 (Empat)', 'Pelayanan pra-rujukan pada komplikasi kebidanan dan neonatal', 
        'Rawat Inap di R. Perawatan Biasa', 'Kolesterol Trigliserida', 'Kolesterol Total', 'Kolesterol LDL', 
        'HbA1c', 'Ureum', 'Gula Darah Puasa (GDP) - PRB/Prolanis', 'Kolesterol HDL', 'Kreatinin', 'Microalbuminaria', 
        'Pelayanan KB : Pemasangan IUD / Implant', 'Pelayanan ANC 4 (Empat)', 'Pelayanan ANC 2 (Dua)', 'Pelayanan ANC 1 (Satu)', 
        'Pelayanan ANC 3 (Tiga)', 'Pelayanan PNC 3 (Tiga)', 'Pelayanan KB : Suntik', 
        'Koreksi Paket Persalinan per Vaginam normal (oleh Bidan), Sesuai PMK 52/2016', 'Paket persalinan per vaginam normal', 
        'Gula Darah Post Prandial (GDPP) - PRB/Prolanis', 'Evakuasi medis / Ambulans Air', 
        'Koreksi Paket Rawat Inap di R. Perawatan Biasa Sesuai PMK 52/2016', 'Paket Persalinan per Vaginam dengan tindakan emergensi dasar', 
        'Pelayanan ANC (FFS)', 'Pelayanan PNC (FFS)', 'Paket Persalinan per Vaginam normal (oleh Dokter)', 
        'Gula Darah Sewaktu (GDS) - PRB/Prolanis', 'Pelayanan KB : Cabut IUD / Implant', 
        'Pelayanan KB : Cabut & Pemasangan IUD / Implant', 'Pelayanan tindakan pasca persalinan', 
        'Koreksi Paket Persalinan per Vaginam dengan tindakan emergensi dasar, Sesuai PMK 52/2016', 'Rontgen Periapikal'
    ],

    # CATATAN: Untuk Diagnosis & Kab/Kota, saya masukkan sampel 10 data saja dari output kamu.
    # Nanti kamu harus ganti list ini dengan load dari file CSV/Excel full data agar lengkap 1103 data.
    'nama_diagnosis': [
        'Tuberculosis of lung, confirmed by sputum microscopy with or without culture', 'Acute abdomen', 
        'Other retinal detachments', 'Abdominal and pelvic pain', 'Iron deficiency anaemia, unspecified', 
        'Routine postpartum follow-up', 'Other single spontaneous delivery', 
        'False labour at or after 37 completed weeks of gestation', 'Secondary hypertension', 
        'Non-insulin-dependent diabetes mellitus without complications'
    ],
    
    'kab_kota_faskes': [
        'PELALAWAN','INDRAGIRI HULU', 'SINJAI', 'BANGKA TENGAH', 'SUMEDANG', 'BENER MERIAH', 
        'MALANG', 'REMBANG', 'LUWU UTARA', 'DOMPU', 'SIAK'
    ]
}

@app.route('/')
def index():
    # Kirim data opsi ke HTML
    return render_template('index.html', options=OPTIONS)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Ambil data dari Form
        input_data = {
            'tingkat_layanan': request.form['tingkat_layanan'],
            'nama_tindakan': request.form['nama_tindakan'],
            'durasi_rawat': float(request.form['durasi_rawat']),
            'prov_faskes': request.form['prov_faskes'],
            'gender': request.form['gender'],
            'prov_peserta': request.form['prov_peserta'],
            'tipe_faskes': request.form['tipe_faskes'],
            'bobot': float(request.form['bobot']),
            'nama_diagnosis': request.form['nama_diagnosis'],
            'kab_kota_faskes': request.form['kab_kota_faskes']
        }
        
        # 2. Buat DataFrame
        df = pd.DataFrame([input_data])

        # 3. Handling Categorical Data (PENTING UNTUK LGBM)
        # Pastikan kolom ini diubah jadi tipe 'category' agar LGBM mau membacanya
        cat_cols = ['tingkat_layanan', 'nama_tindakan', 'prov_faskes', 'gender', 
                    'prov_peserta', 'tipe_faskes', 'nama_diagnosis', 'kab_kota_faskes']
        
        for col in cat_cols:
            df[col] = df[col].astype('category')

        # 4. Prediksi (Uncomment ini!)
        hasil_prediksi = model.predict(df)[0]
        
        # Format Rupiah
        formatted_hasil = "Rp {:,.2f}".format(hasil_prediksi)

        return render_template('index.html', options=OPTIONS, prediction_text=f"Prediksi Tagihan: {formatted_hasil}")

    except Exception as e:
        return render_template('index.html', options=OPTIONS, prediction_text=f"Error: {e}")
if __name__ == '__main__':
    app.run(debug=True)