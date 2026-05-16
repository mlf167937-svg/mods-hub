from flask import Flask, render_template, abort, send_from_directory
import os

app = Flask(__name__)

# Folder penyimpanan utama
BASE_UPLOAD = "static/uploads"
JAVA_FOLDER = os.path.join(BASE_UPLOAD, "java")
MCPE_FOLDER = os.path.join(BASE_UPLOAD, "mcpe")

# Otomatis bikin folder jika belum ada
os.makedirs(JAVA_FOLDER, exist_ok=True)
os.makedirs(MCPE_FOLDER, exist_ok=True)

def format_size(file_path):
    """Menghitung ukuran file dengan aman agar tidak memicu eror jika file corrupt"""
    try:
        size = os.path.getsize(file_path)
        if size < 1024: 
            return f"{size} B"
        elif size < 1024 * 1024: 
            return f"{size / 1024:.1f} KB"
        else: 
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "0 MB"

def get_file_info(filename, folder_path, category_name):
    """Mendeteksi Loader dan Versi secara pintar dari nama file berkas"""
    filename_lower = filename.lower()
    
    # 1. Deteksi Mod Loader / Platform
    loader = "Vanilla/Custom"
    if "forge" in filename_lower: 
        loader = "Forge"
    elif "fabric" in filename_lower: 
        loader = "Fabric"
    elif "quilt" in filename_lower: 
        loader = "Quilt"
    elif "geyser" in filename_lower: 
        loader = "Geyser"

    # 2. Deteksi Versi Game (Mencari teks angka dengan pola '1.xx')
    version = "All Version"
    if "1." in filename:
        # Pisahkan nama file berdasarkan simbol agar pembacaan teks angka lebih akurat
        parts = filename_lower.replace('-', '_').replace('+', '_').split('_')
        for part in parts:
            if "1." in part:
                version = part.replace('.jar', '').replace('.zip', '').replace('.mcpack', '').replace('.mcaddon', '')
                break

    return {
        "filename": filename,
        "version": version,
        "loader": loader,
        "size": format_size(os.path.join(folder_path, filename))
    }

@app.route("/")
def home():
    """Halaman Utama: Membaca daftar folder mod dengan proteksi kebal bug"""
    all_mods = []
    
    for category_path, cat_name in [(JAVA_FOLDER, "java"), (MCPE_FOLDER, "mcpe")]:
        if os.path.exists(category_path):
            try:
                # Ambil semua item berjenis folder di dalam direktori
                folders = [f for f in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, f))]
                folders.sort()
            except:
                continue
            
            for folder_name in folders:
                mod_path = os.path.join(category_path, folder_name)
                
                try:
                    # Ambil semua file asli (abaikan file sistem tersembunyi seperti .DS_Store)
                    files = [f for f in os.listdir(mod_path) if not f.startswith('.')]
                except:
                    continue
                
                if not files: 
                    continue # Lewati kartu jika di dalam foldernya benar-benar kosong kosong kosong
                
                # Mengubah nama folder menjadi judul yang rapi (Contoh: mod_booster -> Mod Booster)
                clean_title = folder_name.replace('_', ' ').replace('-', ' ').title()
                
                # Proses scan versi file di dalam folder dengan proteksi try-except
                versions_found = []
                for f in files:
                    try:
                        info = get_file_info(f, mod_path, cat_name)
                        if info["version"] != "All Version":
                            versions_found.append(info["version"])
                    except:
                        pass

                # Menentukan teks range versi yang akan dipajang di halaman depan web
                try:
                    unique_versions = sorted(list(set(versions_found)))
                    if len(unique_versions) == 1:
                        version_range = unique_versions[0]
                    elif len(unique_versions) > 1:
                        version_range = f"{unique_versions[0]} - {unique_versions[-1]}"
                    else:
                        # Fallback otomatis khusus MCPE atau file berkarakter unik (+) agar badge tetap terisi indah
                        version_range = "1.20 - 1.21+" if cat_name == "mcpe" else "Multi Version"
                except:
                    version_range = "Multi Version"
                
                all_mods.append({
                    "id": folder_name,
                    "title": clean_title,
                    "category": cat_name,
                    "version_range": version_range,
                    "desc": f"Update berkas {cat_name.upper()} terbaru. Dioptimalkan khusus agar lancar, estetik, dan anti-lag saat dimainkan.",
                    "total_files": len(files)
                })
                
    return render_template("index.html", mods=all_mods)

@app.route("/mod/<category>/<path:mod_id>")
def mod_page(category, mod_id):
    """Halaman Detail Dropdown: Menggunakan tipe rute <path:> agar kebal eror simbol unik"""
    base_folder = JAVA_FOLDER if category == "java" else MCPE_FOLDER
    mod_path = os.path.join(base_folder, mod_id)
    
    if not os.path.exists(mod_path) or not os.path.isdir(mod_path):
        abort(404)
        
    clean_title = mod_id.replace('_', ' ').replace('-', ' ').title()
    files = [f for f in os.listdir(mod_path) if not f.startswith('.')]
    
    file_list = []
    versions_set = set()
    loaders_set = set()
    
    for f in files:
        try:
            info = get_file_info(f, mod_path, category)
            file_list.append(info)
            versions_set.add(info["version"])
            loaders_set.add(info["loader"])
        except:
            pass

    # Urutkan opsi dropdown versi (dari versi paling baru di paling atas)
    sorted_versions = sorted(list(versions_set), reverse=True)
    sorted_loaders = sorted(list(loaders_set))

    mod_data = {
        "id": mod_id,
        "title": clean_title,
        "category": category,
        "desc": f"Berkas resmi berjenis {category.upper()} dari RexCraft Mods. Sudah melewati uji coba agar aman dan lancar di Minecraft kamu.",
        "files": file_list,
        "available_versions": sorted_versions,
        "available_loaders": sorted_loaders
    }
    
    return render_template("mod.html", mod=mod_data)

@app.route("/download/<category>/<path:mod_id>/<filename>")
def download(category, mod_id, filename):
    """Rute pengunduhan file instan dan aman"""
    base_folder = JAVA_FOLDER if category == "java" else MCPE_FOLDER
    mod_path = os.path.join(base_folder, mod_id)
    return send_from_directory(mod_path, filename, as_attachment=True)

if __name__ == "__main__":
    app.run()
