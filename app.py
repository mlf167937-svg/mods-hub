import os
import re
from flask import Flask, render_template, abort, send_from_directory

app = Flask(__name__)

# Mengatur lokasi folder penyimpanan berkas (Directori static/uploads/)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_file_info(filepath, filename):
    """
    Fungsi pintar untuk membaca ukuran file dan membersihkan nama berkas 
    menjadi teks versi yang rapi di menu dropdown.
    """
    try:
        size_bytes = os.path.getsize(filepath)
        if size_bytes >= 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{size_bytes / 1024:.1f} KB"
    except OSError:
        size_str = "0 KB"

    # Proses ekstraksi angka versi game dari nama berkas asli
    clean_name = os.path.splitext(filename)[0]
    parts = re.split(r'[-_]', clean_name)
    
    version = "1.20 - 1.21+" # Fallback standar jika tidak ditemukan angka versi
    for part in parts:
        # Mendeteksi format angka versi seperti 1.21, 1.20.1, v1.26, dll.
        if re.search(r'\d+\.\d+', part):
            # Memotong ekstensi berkas MCPE/Java jika masih menempel di teks
            version = part.replace('.jar', '').replace('.zip', '').replace('.mcpack', '').replace('.mcaddon', '')
            if version.lower().startswith('v') and len(version) > 1:
                version = version[1:]
            break
            
    return {
        'filename': filename,
        'version': version,
        'size': size_str
    }

def get_all_mods():
    """
    Mesin utama web yang otomatis membaca seluruh struktur folder di GitHub 
    dan merangkumnya menjadi kartu-kartu mod di halaman utama.
    """
    mods_data = []
    categories = ['java', 'mcpe']
    
    if not os.path.exists(UPLOAD_FOLDER):
        return mods_data

    for category in categories:
        category_path = os.path.join(UPLOAD_FOLDER, category)
        if not os.path.exists(category_path):
            continue

        # Membaca folder judul mod (Tingkat 2)
        for folder_name in os.listdir(category_path):
            folder_path = os.path.join(category_path, folder_name)
            
            # Abaikan jika itu file sampah sistem atau bukan sebuah direktori/folder
            if folder_name.startswith('.') or not os.path.isdir(folder_path):
                continue

            files_list = []
            # Membaca berkas asli di dalam folder (Tingkat 3)
            for filename in os.listdir(folder_path):
                # Proteksi: Abaikan file tersembunyi sistem (.gitkeep, .DS_Store, dll)
                if filename.startswith('.'):
                    continue
                    
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    file_info = get_file_info(filepath, filename)
                    files_list.append(file_info)

            if files_list:
                # Mengurutkan versi dari yang paling baru ke versi lama di dropdown
                files_list.sort(key=lambda x: x['version'], reverse=True)
                
                # Menentukan rentang versi untuk dipajang di badge kartu depan
                if len(files_list) > 1:
                    version_range = f"{files_list[-1]['version']} - {files_list[0]['version']}"
                else:
                    version_range = files_list[0]['version']

                # Membuat format nama judul yang rapi (mengganti garis bawah menjadi spasi)
                display_title = folder_name.replace('_', ' ').title()

                mods_data.append({
                    'id': folder_name,
                    'title': display_title,
                    'category': category,
                    'version_range': version_range,
                    'total_files': len(files_list),
                    'desc': f"Update berkas {category.upper()} terbaru. Dioptimalkan khusus agar lancar, estetik, dan anti-lag saat dimainkan.",
                    'files': files_list
                })
                
    return mods_data

# ==================== RUTE / ROUTES FLASK ====================

@app.route("/")
def index():
    """Halaman Utama Web RexCraft Mods Hub"""
    mods = get_all_mods()
    return render_template("index.html", mods=mods)

@app.route("/tutorial")
def tutorial():
    """Halaman Resmi Panduan Cara Pasang Mod (SOLUSI FIX BUG 404)"""
    return render_template("tutorial.html")

@app.route("/mod/<category>/<mod_id>")
def mod_detail(category, mod_id):
    """Halaman Detail Pilih Versi & Download Mod"""
    mods = get_all_mods()
    # Mencari data mod yang spesifik sesuai ID folder yang diklik pengunjung
    current_mod = next((m for m in mods if m['category'] == category and m['id'] == mod_id), None)
    
    if not current_mod:
        abort(404)
        
    return render_template("mod_detail.html", mod=current_mod)

@app.route("/download/<category>/<mod_id>/<filename>")
def download_file(category, mod_id, filename):
    """Sistem Pengirim Berkas Aman (Mendukung .jar, .zip, .mcpack, .mcaddon)"""
    secure_dir = os.path.join(UPLOAD_FOLDER, category, mod_id)
    # Proteksi keamanan: pastikan folder tujuan benar-minded ada di sistem
    if not os.path.exists(os.path.join(secure_dir, filename)):
        abort(404)
        
    # Mengirim file secara utuh langsung ke browser pengunjung tanpa merubah format asli
    return send_from_directory(secure_dir, filename, as_attachment=True)

# Error Handler jika pengunjung nyasar ke alamat salah
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    # Menjalankan server Flask lokal
    app.run(debug=True, host="0.0.0.0", port=5000)
