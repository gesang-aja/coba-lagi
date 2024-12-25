import streamlit as st
import joblib
import pandas as pd
import numpy as np



@st.cache_resource
def load_model():
    """
    Memuat model Random Forest yang telah dilatih dari file.

    Returns:
        RandomForest_krisjen: Model Random Forest yang dimuat.
    """
    loaded_model = joblib.load('model_random_forest.joblib')
    return loaded_model

# Fungsi untuk memuat CSS
def load_css(file_name):
    """
    Membaca file CSS dan menambahkan ke dalam aplikasi Streamlit.

    Args:
        file_name (str): Path ke file CSS.

    Returns:
        None
    """
    with open(file_name) as f:
        css = f.read()
        st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Memuat CSS
load_css('styles.css')

# Memuat label_encoders
label_encoders = joblib.load('label_encoders.joblib')

# Memuat model
model = load_model()

# 1. Memusatkan Judul dan Deskripsi

# Judul Aplikasi (Centered)
st.markdown("<h1>Cek Obesitas</h1>", unsafe_allow_html=True)

# Deskripsi (Centered)
st.markdown("""
<div class='description'>
Silakan isi pertanyaan di bawah ini. Setelah mengisi, klik tombol "Generate Hasil" untuk mendapatkan prediksi tingkat obesitas Anda berdasarkan input yang diberikan.
</div>
""", unsafe_allow_html=True)


# 2. Fungsi Validasi Input

def is_valid_input(gender, family_history_with_overweight, favc, caec, smoke, scc, calc, mtrans,fcvc,ncp,faf,tue,ch2o):
    """
    Memeriksa apakah semua input telah diisi dengan benar.

    Args:
        gender (str): Pilihan jenis kelamin.
        family_history_with_overweight (str): Riwayat keluarga dengan obesitas.
        favc (str): Konsumsi makanan tinggi kalori.
        caec (str): Konsumsi makanan di antara waktu makan utama.
        smoke (str): Kebiasaan merokok.
        scc (str): Pemantauan kalori.
        calc (str): Frekuensi konsumsi alkohol.
        mtrans (str): Mode transportasi.

    Returns:
        bool: True jika semua input valid, False jika tidak.
    """
    # Cek apakah semua radio/select box telah dipilih dengan benar
    radio_valid = all([
        family_history_with_overweight in ['Ya', 'Tidak'],
        favc in ['Ya', 'Tidak'],
        smoke in ['Ya', 'Tidak'],
        scc in ['Ya', 'Tidak']
    ])
    select_valid = all([
        gender in ['Laki-laki', 'Perempuan'],
        calc in ['Tidak pernah', 'Kadang-kadang','Sering',"Selalu"],
        caec in ['Tidak pernah', 'Kadang-kadang','Sering',"Selalu"],
        mtrans in ['Mobil pribadi', 'Sepeda', 'Sepeda motor', 'Transportasi umum', 'Berjalan kaki'],
        ncp in ['1—2','3','>3'],
        fcvc in ['Tidak pernah', 'Kadang-kadang','Selalu'],
        ch2o in['<1','0—2','>2' ], 
        faf in ['Tidak pernah','1—2 hari','2—4 hari', '4—5 hari'],
        tue in [ '0—2 jam 0','3—5 jam 1','>5 jam 2'],
    ])
    return radio_valid and select_valid


# 3. Fungsi Reset Form (Opsional)

def reset_form():
    """
    Mengosongkan semua input dalam session_state dan me-reload ulang aplikasi.
    """
    for key in list(st.session_state.keys()):
        if key.startswith('input_'):
            del st.session_state[key]
    st.experimental_rerun()


# 4. Membuat Formulir Kuisioner

with st.form(key='kuisioner_form'):
    # 1. Gender
    gender = st.selectbox(
        'Jenis Kelamin',
        ['Pilih...', 'Laki-laki', 'Perempuan'],
        index=0,  
        key='input_gender'
    )  

    # 2. Age
    age = st.text_input(
        'Umur (tahun)',
        value='',
        key='input_age',
        placeholder='Masukkan umur Anda'
    )

    # 3. Height
    height = st.text_input(
        'Tinggi Badan (cm)',
        value='',
        key='input_height',
        placeholder='Masukkan tinggi badan Anda dalam cm'
    )

    # 4. Weight
    weight = st.text_input(
        'Berat Badan (kg)',
        value='',
        key='input_weight',
        placeholder='Masukkan berat badan Anda dalam kg'
    )

    # 5. Family History with Overweight
    family_history_with_overweight = st.radio(
        'Apakah Anda memiliki anggota keluarga yang pernah atau sedang mengalami obesitas?',
        ['Ya', 'Tidak'],  
        key='input_family_history_with_overweight'
    )

    # 6. FAVC (Frequent Consumption of High Caloric Food)
    favc = st.radio(
        'Apakah Anda sering mengonsumsi makanan tinggi kalori?',
        ['Ya', 'Tidak'],  
        key='input_favc'
    )

    # 7. FCVC (Frequent Consumption of Vegetables)
    fcvc = st.selectbox(
        'Seberapa sering Anda makan sayuran dalam sekali makan?',
        ['Pilih...', 'Tidak pernah', 'Kadang-kadang','Selalu'], 
        index=0,
        key='input_fcvc'
    )

    # 8. NCP (Number of Main Meals per Day)
    ncp = st.selectbox(
        'Berapa kali makan utama yang Anda konsumsi setiap hari?',
        ['Pilih...', '1—2','3','>3'], 
        index=0,
        key='input_ncp',
    )

    # 9. CAEC (Consumption of Any Food Between Meals)
    caec = st.selectbox(
        'Apakah Anda makan makanan di antara waktu makan utama?',
        ['Pilih...', 'Tidak pernah', 'Kadang-kadang','Sering',"Selalu"], 
        index=0,
        key='input_caec'
    )

    # 10. SMOKE (Smoking Habit)
    smoke = st.radio(
        'Apakah Anda merokok?',
        ['Ya', 'Tidak'],  
        key='input_smoke'
    )

    # 11. CH2O (Daily Water Consumption in Liters)
    ch2o = st.selectbox(
        'Berapa banyak air yang Anda konsumsi setiap hari? (liter)',
        ['Pilih...', '<1','0—2','>2', ], 
        index=0,
        key='input_ch2o',
    )

    # 12. SCC (Calorie Monitoring)
    scc = st.radio(
        'Apakah Anda memantau kalori yang Anda konsumsi setiap hari?',
        ['Ya', 'Tidak'],  
        key='input_scc'
    )

    # 13. FAF (Frequency of Physical Activity)
    faf = st.selectbox(
        'Seberapa sering Anda melakukan aktivitas fisik? (1-10)',
        ['Pilih...', 'Tidak pernah','1—2 hari','2—4 hari', '4—5 hari'], 
        index=0,
        key='input_faf',
    )

    # 14. TUE (Time Using Technology Devices per Day)
    tue = st.selectbox(
        'Berapa jam Anda menggunakan perangkat teknologi (telepon seluler, video game, televisi, komputer, dll.) per hari?',
        ['Pilih...', '0—2 jam 0','3—5 jam 1','>5 jam 2'], 
        index=0,
        key='input_tue',
    )

    # 15. CALC (Alcohol Consumption Frequency)
    calc = st.selectbox(
        'Seberapa sering Anda minum alkohol?',
        ['Pilih...', 'Tidak pernah', 'Kadang-kadang','Sering',"Selalu"], 
        index=0,
        key='input_calc'
    )

    # 16. MTRANS (Mode of Transportation)
    mtrans = st.selectbox(
        'Jenis transportasi apa yang biasanya Anda gunakan?',
        ['Pilih...', 'Mobil pribadi', 'Sepeda', 'Sepeda motor', 'Transportasi umum', 'Berjalan kaki'], 
        index=0,
        key='input_mtrans'
    )

    # Tombol Submit
    submit_button = st.form_submit_button(label='Generate Hasil')


# 5. Fungsi Preprocessing Input

def preprocess_input(
    gender, age, height, weight,
    family_history_with_overweight, favc, fcvc, ncp,
    caec, smoke, ch2o, scc, faf, tue,
    calc, mtrans
):
    """
    Preprocesses the input data by encoding categorical variables.
    """
    # Mapping untuk kategori
    fcvc_mapping = {"Tidak pernah": 1, "Kadang-kadang": 2, "Selalu": 3}
    ncp_mapping = {'1—2': 1, '3': 2, '>3': 3}
    ch2o_mapping = {'<1': 1, '0—2': 2, '>2': 3}
    faf_mapping = {'Tidak pernah': 0, '1—2 hari': 1, '2—4 hari': 2, '4—5 hari': 3}
    tue_mapping = {'0—2 jam 0': 0, '3—5 jam 1': 1, '>5 jam 2': 2}

    gender_mapping = {"Laki-laki": 'Male', "Perempuan": 'Female'}
    family_history_with_overweight_mapping = {"Ya": 'yes', "Tidak": 'no'}
    favc_mapping = {"Ya": 'yes', "Tidak": 'no'}
    caec_mapping = {"Tidak pernah": "no", "Kadang-kadang": "Sometimes", "Sering": "Frequently", "Selalu": "Always"}
    smoke_mapping = {"Ya": 'yes', "Tidak": 'no'}
    scc_mapping = {"Ya": 'yes', "Tidak": 'no'}
    calc_mapping = {"Tidak pernah": "no", "Kadang-kadang": "Sometimes", "Sering": "Frequently", "Selalu": "Always"}
    mtrans_mapping = {
        "Mobil pribadi": 'Automobile',
        "Sepeda motor": 'Motorbike',
        "Sepeda": 'Bike',
        "Transportasi umum": 'Public_Transportation',
        "Berjalan kaki": 'Walking'
    }

    # Debugging sebelum mapping
    # st.write("Input sebelum mapping:")
    # st.write({
    #     'Gender': gender, 'Age': age, 'Height': height, 'Weight': weight,
    #     'Family History': family_history_with_overweight, 'FAVC': favc, 
    #     'FCVC': fcvc, 'NCP': ncp, 'CAEC': caec, 'SMOKE': smoke, 
    #     'CH2O': ch2o, 'SCC': scc, 'FAF': faf, 'TUE': tue, 
    #     'CALC': calc, 'MTRANS': mtrans
    # })

    try:
        # Konversi input text menjadi angka
        age = int(age)
        height = float(height) / 100  # Konversi ke meter
        weight = float(weight)

        # Debugging setelah konversi angka
        # st.write("Setelah konversi angka:", {"Age": age, "Height": height, "Weight": weight})

        # Mapping kategori
        gender = gender_mapping[gender]
        family_history_with_overweight = family_history_with_overweight_mapping[family_history_with_overweight]
        favc = favc_mapping[favc]
        fcvc = fcvc_mapping[fcvc]
        caec = caec_mapping[caec]
        calc = calc_mapping[calc]
        smoke = smoke_mapping[smoke]
        scc = scc_mapping[scc]
        mtrans = mtrans_mapping[mtrans]

        # Debugging setelah mapping kategori
        # st.write("Setelah mapping kategori:")
        # st.write({
        #     'Gender': gender, 'Family History': family_history_with_overweight, 
        #     'FAVC': favc, 'FCVC': fcvc, 'NCP': ncp_mapping[ncp], 
        #     'CAEC': caec, 'SMOKE': smoke, 'CH2O': ch2o_mapping[ch2o], 
        #     'SCC': scc, 'FAF': faf_mapping[faf], 'TUE': tue_mapping[tue], 
        #     'CALC': calc, 'MTRANS': mtrans
        # })

        # Buat dictionary untuk dataframe
        data = {
            'Gender': label_encoders['Gender'].transform([gender])[0],
            'Age': age,
            'Height': height,
            'Weight': weight,
            'family_history_with_overweight': label_encoders['family_history_with_overweight'].transform([family_history_with_overweight])[0],
            'FAVC': label_encoders['FAVC'].transform([favc])[0],
            'FCVC': fcvc,
            'NCP': ncp_mapping[ncp],
            'CAEC': label_encoders['CAEC'].transform([caec])[0],
            'SMOKE': label_encoders['SMOKE'].transform([smoke])[0],
            'CH2O': ch2o_mapping[ch2o],
            'SCC': label_encoders['SCC'].transform([scc])[0],
            'FAF': faf_mapping[faf],
            'TUE': tue_mapping[tue],
            'CALC': label_encoders['CALC'].transform([calc])[0],
            'MTRANS': label_encoders['MTRANS'].transform([mtrans])[0]
        }

        # Debugging setelah encoding
        # st.write("Setelah encoding ke dataframe:")
        # st.write(data)

    except Exception as e:
        st.error(f"Error saat preprocessing input: {e}")
        return None

    df = pd.DataFrame([data])
    return df


# 6. Ketika Button Submit Ditekan

if submit_button:
    # Memeriksa validitas input
    if is_valid_input(gender, family_history_with_overweight, favc, caec, smoke, scc, calc, mtrans,fcvc,ncp,faf,tue,ch2o) and all([
        age.strip() != '',
        height.strip() != '',
        weight.strip() != '',
    ]):
        # Preprocessing input
        input_data = preprocess_input(
            gender, age, height, weight,
            family_history_with_overweight, favc, fcvc, ncp,
            caec, smoke, ch2o, scc, faf, tue,
            calc, mtrans
        )
        if input_data is not None:
            # Melakukan prediksi
            try:
                prediction = model.predict(input_data)[0]
            except Exception as e:
                st.error(f"Error during prediction: {e}")
                prediction = None

            if prediction is not None:
                predicted_label = label_encoders['NObeyesdad'].inverse_transform([prediction])[0]
                print(predicted_label)
                  
                st.markdown("<h3 class='result'>Hasil Prediksi</h3>", unsafe_allow_html=True)
                st.markdown(f"<p class='result'>Tingkat Obesitas Anda: <b>{predicted_label}</b></p>", unsafe_allow_html=True)
    else:
        st.error("Silakan lengkapi semua pilihan dan isi semua bidang sebelum melakukan prediksi.")
