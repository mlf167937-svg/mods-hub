from flask import Flask, render_template, abort, send_from_directory
import os

app = Flask(__name__)

BASE_UPLOAD = "static/uploads"
JAVA_FOLDER = os.path.join(BASE_UPLOAD, "java")
MCPE_FOLDER = os.path.join(BASE_UPLOAD, "mcpe")

os.makedirs(JAVA_FOLDER, exist_ok=True)
os.makedirs(MCPE_FOLDER, exist_ok=True)

def format_size(file_path):
    try:
        size = os.path.getsize(file_path)
        if size < 1024: return f"{size} B"
        elif size < 1024 * 1024: return f"{size / 1024:.1f} KB"
        else: return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "0 MB"

def get_file_info(filename, folder_path, category_name):
    """Fungsi pembaca detail file (Versi & Loader) berdasarkan nama filenya"""
    filename_lower = filename.lower()
    
    # 1. Deteksi Loader
    loader = "Vanilla/Custom"
    if "forge" in filename_lower: loader = "Forge"
    elif "fabric" in filename_lower: loader = "Fabric"
    elif "quilt" in filename_lower: loader = "Quilt"
    elif "geyser" in filename_lower: loader = "Geyser"

    # 2. Deteksi Versi Game (mencari pola teks '1.xx')
    version = "All Version"
    if "1." in filename:
        parts = filename_lower.replace('-', '_').split('_')
        for part in parts:
            if "1." in part:
                version = part.replace('.jar', '').replace('.zip', '').replace('.mcpack', '')
                break

    return {
        "filename": filename,
        "version": version,
        "loader": loader,
        "size": format_size(os.path.join(folder_path, filename))
    }

@app.route("/")
def home():
    """Menampilkan daftar MOD berdasarkan FOLDER, bukan lagi berdasarkan FILE"""
    all_mods = []
    
    for category_path, cat_name in [(JAVA_FOLDER, "java"), (MCPE_FOLDER, "mcpe")]:
        if os.path.exists(category_path):
            folders = [f for f in os.listdir(category_path) if os.path.isdir(os.path.join(category_path, f))]
            folders.sort()
            
            for folder_name in folders:
                mod_path = os.path.join(category_path, folder_name)
                files = [f for f in os.listdir(mod_path) if not f.startswith('.')]
                
                if not files: continue # Lewati jika folder kosong
                
                # Judul kartu diambil dari nama folder (ganti strip/garis bawah jadi spasi)
                clean_title = folder_name.replace('_', ' ').replace('-', ' ').title()
                
                all_mods.append({
                    "id": folder_name,
                    "title": clean_title,
                    "category": cat_name,
                    "desc": f"Update berkas {cat_name.upper()} terbaru. Dioptimalkan khusus agar lancar, estetik, dan anti-lag saat dimainkan.",
                    "total_files": len(files)
                })
                
    return render_template("index.html", mods=all_mods)

@app.route("/mod/<category>/<mod_id>")
def mod_page(category, mod_id):
    """Halaman Detail ala Modrinth: Membaca seluruh file di dalam folder mod"""
    base_folder = JAVA_FOLDER if category == "java" else MCPE_FOLDER
    mod_path = os.path.join(base_folder, mod_id)
    
    if not os.path.exists(mod_path) or not os.path.isdir(mod_path):
        abort(404)
        
    clean_title = mod_id.replace('_', ' ').replace('-', ' ').title()
    files = [f for f in os.listdir(mod_path) if not f.startswith('.')]
    
    # Ambil data spesifik dari setiap file di dalam folder
    file_list = []
    versions_set = set()
    loaders_set = set()
    
    for f in files:
        info = get_file_info(f, mod_path, category)
        file_list.append(info)
        versions_set.add(info["version"])
        loaders_set.add(info["loader"])

    # Urutkan versi agar dari yang terbaru
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

@app.route("/download/<category>/<mod_id>/<filename>")
def download(category, mod_id, filename):
    base_folder = JAVA_FOLDER if category == "java" else MCPE_FOLDER
    mod_path = os.path.join(base_folder, mod_id)
    return send_from_directory(mod_path, filename, as_attachment=True)

if __name__ == "__main__":
    app.run()
