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

# FORMAT UKURAN FILE
def format_size(file_path):
    size = os.path.getsize(file_path)
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    else:
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

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
            
            # 1. Deteksi Versi Otomatis
            version = "All Version"
            if "1." in filename:
                parts = filename.split('_')
                for part in parts:
                    if part.startswith('1.') or '1.' in part:
                        version = os.path.splitext(part)[0]

            # 2. Deteksi Mod Loader (Forge / Fabric / Quilt)
            loader_tag = None
            filename_lower = filename.lower()
            if "forge" in filename_lower:
                loader_tag = "Forge"
            elif "fabric" in filename_lower:
                loader_tag = "Fabric"
            elif "quilt" in filename_lower:
                loader_tag = "Quilt"

            mods_list.append({
                "title": clean_title,
                "version": version,
                "loader": loader_tag,
                
                # =================================================================================
                # MODIFIKASI DESKRIPSI (OPSI 3): FOKUS PERFORMA, ESTETIK, DAN ANTI-LAG
                # =================================================================================
                "desc": f"Update berkas {category_name} terbaru. Dioptimalkan khusus agar lancar, estetik, dan anti-lag saat dimainkan.",
                # =================================================================================
                
                "file": filename,
                "category": category_name.lower(),
                "size": format_size(os.path.join(folder_path, filename))
            })
    return mods_list

@app.route("/")
def home():
    java_mods = scan_mods_by_category(JAVA_FOLDER, "Java")
    mcpe_mods = scan_mods_by_category(MCPE_FOLDER, "MCPE")
    all_mods = java_mods + mcpe_mods
    return render_template("index.html", mods=all_mods)

@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html")

@app.route("/mod/<category>/<filename>")
def mod_page(category, filename):
    folder = JAVA_FOLDER if category == "java" else MCPE_FOLDER
    if not os.path.exists(os.path.join(folder, filename)):
        abort(404)
        
    clean_title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ')
    
    # Deteksi Mod Loader untuk halaman detail
    loader_tag = None
    filename_lower = filename.lower()
    if "forge" in filename_lower:
        loader_tag = "Forge"
    elif "fabric" in filename_lower:
        loader_tag = "Fabric"
    elif "quilt" in filename_lower:
        loader_tag = "Quilt"

    mod = {
        "title": clean_title,
        "version": "Sesuai Nama File",
        "loader": loader_tag,
        
        # Deskripsi halaman detail disesuaikan juga agar serasi
        "desc": f"Berkas resmi berjenis {category.upper()} dari RexCraft Mods. Sudah melewati uji coba agar aman dan lancar di Minecraft kamu.",
        
        "file": filename,
        "category": category,
        "size": format_size(os.path.join(folder, filename))
    }
    return render_template("mod.html", mod=mod)

@app.route("/download/<category>/<filename>")
def download(category, filename):
    folder = JAVA_FOLDER if category == "java" else MCPE_FOLDER
    return send_from_directory(folder, filename, as_attachment=True)

if __name__ == "__main__":
    app.run()
