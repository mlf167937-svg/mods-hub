from flask import Flask, render_template, abort, send_from_directory
import os

app = Flask(__name__)

# Folder penyimpanan utama
BASE_UPLOAD = "static/uploads"
JAVA_FOLDER = os.path.join(BASE_UPLOAD, "java")
MCPE_FOLDER = os.path.join(BASE_UPLOAD, "mcpe")

# Otomatis bikin folder di komputer lokal saat dijalankan
os.makedirs(JAVA_FOLDER, exist_ok=True)
os.makedirs(MCPE_FOLDER, exist_ok=True)

def scan_mods_by_category(folder_path, category_name):
    """Fungsi mendeteksi file di dalam folder spesifik (java/mcpe)"""
    mods_list = []
    if os.path.exists(folder_path):
        files = os.listdir(folder_path)
        files.sort()
        for filename in files:
            if filename.startswith('.') or filename == 'test.txt':
                continue
                
            clean_title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
            
            version = "All Version"
            if "1." in filename:
                parts = filename.split('_')
                for part in parts:
                    if part.startswith('1.') or '1.' in part:
                        version = os.path.splitext(part)[0]

            mods_list.append({
                "title": clean_title,
                "version": version,
                "desc": f"Modifikasi resmi {category_name} dari RexCraft Mods. Unduh dan pasang ke Minecraft kamu.",
                "file": filename,
                "category": category_name.lower() # 'java' atau 'mcpe'
            })
    return mods_list

@app.route("/")
def home():
    # Scan masing-masing folder
    java_mods = scan_mods_by_category(JAVA_FOLDER, "Java")
    mcpe_mods = scan_mods_by_category(MCPE_FOLDER, "MCPE")
    
    # Gabungkan semua mod untuk dikirim ke template
    all_mods = java_mods + mcpe_mods
    return render_template("index.html", mods=all_mods)

@app.route("/mod/<category>/<filename>")
def mod_page(category, filename):
    folder = JAVA_FOLDER if category == "java" else MCPE_FOLDER
    
    # Validasi apakah file memang ada
    if not os.path.exists(os.path.join(folder, filename)):
        abort(404)
        
    clean_title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
    mod = {
        "title": clean_title,
        "version": "Sesuai Nama File",
        "desc": f"Modifikasi resmi Berjenis {category.upper()} dari RexCraft Mods.",
        "file": filename,
        "category": category
    }
    return render_template("mod.html", mod=mod)

@app.route("/download/<category>/<filename>")
def download(category, filename):
    folder = JAVA_FOLDER if category == "java" else MCPE_FOLDER
    return send_from_directory(folder, filename, as_attachment=True)

if __name__ == "__main__":
    app.run()
