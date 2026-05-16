import os
import re
from flask import Flask, render_template, abort, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_file_info(filepath, filename):
    """
    Fungsi untuk membaca ukuran file, versi, 
    serta otomatis mendeteksi apakah mod ini untuk Fabric atau Forge.
    """
    try:
        size_bytes = os.path.getsize(filepath)
        if size_bytes >= 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{size_bytes / 1024:.1f} KB"
    except OSError:
        size_str = "0 KB"

    # Deteksi otomatis Mod Loader dari nama file
    name_lower = filename.lower()
    if 'fabric' in name_lower:
        loader = "Fabric"
    elif 'forge' in name_lower:
        loader = "Forge"
    else:
        loader = "Universal"

    clean_name = os.path.splitext(filename)[0]
    parts = re.split(r'[-_]', clean_name)
    
    version = "1.20 - 1.21+"
    for part in parts:
        if re.search(r'\d+\.\d+', part):
            version = part.replace('.jar', '').replace('.zip', '').replace('.mcpack', '').replace('.mcaddon', '')
            if version.lower().startswith('v') and len(version) > 1:
                version = version[1:]
            break
            
    return {
        'filename': filename,
        'version': version,
        'size': size_str,
        'loader': loader
    }

def get_all_mods():
    """
    Membaca seluruh struktur folder, mengumpulkan daftar file,
    dan mendeteksi loader apa saja yang tersedia untuk halaman utama.
    """
    mods_data = []
    categories = ['java', 'mcpe']
    
    if not os.path.exists(UPLOAD_FOLDER):
        return mods_data

    for category in categories:
        category_path = os.path.join(UPLOAD_FOLDER, category)
        if not os.path.exists(category_path):
            continue

        for folder_name in os.listdir(category_path):
            folder_path = os.path.join(category_path, folder_name)
            
            if folder_name.startswith('.') or not os.path.isdir(folder_path):
                continue

            files_list = []
            icon_file = None
            detected_loaders = set()
            
            for filename in os.listdir(folder_path):
                if filename.startswith('.'):
                    continue
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    icon_file = filename
                    continue
                    
                filepath = os.path.join(folder_path, filename)
                if os.path.isfile(filepath):
                    file_info = get_file_info(filepath, filename)
                    files_list.append(file_info)
                    detected_loaders.add(file_info['loader'])

            if files_list:
                files_list.sort(key=lambda x: x['version'], reverse=True)
                
                if len(files_list) > 1:
                    version_range = f"{files_list[-1]['version']} - {files_list[0]['version']}"
                else:
                    version_range = files_list[0]['version']

                display_title = folder_name.replace('_', ' ').replace('-', ' ').title()
                icon_url = f"/static/uploads/{category}/{folder_name}/{icon_file}" if icon_file else None

                mods_data.append({
                    'id': folder_name,
                    'title': display_title,
                    'category': category,
                    'version_range': version_range,
                    'total_files': len(files_list),
                    'desc': f"Update berkas {category.upper()} terbaru. Dioptimalkan khusus agar lancar, estetik, dan anti-lag saat dimainkan.",
                    'files': files_list,
                    'icon_url': icon_url,
                    'loaders': list(detected_loaders)
                })
                
    return mods_data

@app.route("/")
def index():
    mods = get_all_mods()
    return render_template("index.html", mods=mods)

@app.route("/tutorial")
def tutorial():
    return render_template("tutorial.html")

@app.route("/mod/<category>/<mod_id>")
def mod_detail(category, mod_id):
    if category not in ['java', 'mcpe']:
        abort(404)
        
    target_folder = os.path.join(UPLOAD_FOLDER, category, mod_id)
    if not os.path.exists(target_folder) or not os.path.isdir(target_folder):
        abort(404)
        
    files_list = []
    icon_file = None
    
    try:
        for filename in os.listdir(target_folder):
            if filename.startswith('.'):
                continue
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                icon_file = filename
                continue
            filepath = os.path.join(target_folder, filename)
            if os.path.isfile(filepath):
                files_list.append(get_file_info(filepath, filename))
    except Exception:
        abort(500)

    if not files_list:
        abort(404)

    files_list.sort(key=lambda x: x['version'], reverse=True)
    
    if len(files_list) > 1:
        version_range = f"{files_list[-1]['version']} - {files_list[0]['version']}"
    else:
        version_range = files_list[0]['version']
        
    display_title = mod_id.replace('_', ' ').replace('-', ' ').title()
    icon_url = f"/static/uploads/{category}/{mod_id}/{icon_file}" if icon_file else None

    # DI SINI KATA PANGGILAN SUDAH DIUBAH MENJADI FORMAL DAN AMAN UNTUK PENGUNJUNG
    current_mod = {
        'id': mod_id,
        'title': display_title,
        'category': category,
        'version_range': version_range,
        'desc': f"Berkas resmi berjenis {category.upper()} dari RexCraft Mods. Sudah melewati uji coba agar aman dan lancar di Minecraft Anda.",
        'files': files_list,
        'icon_url': icon_url
    }
    
    return render_template("mod.html", mod=current_mod)

@app.route("/download/<category>/<mod_id>/<filename>")
def download_file(category, mod_id, filename):
    secure_dir = os.path.join(UPLOAD_FOLDER, category, mod_id)
    if not os.path.exists(os.path.join(secure_dir, filename)):
        abort(404)
    return send_from_directory(secure_dir, filename, as_attachment=True)

@app.route("/health")
def health_check():
    return "OK", 200

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
