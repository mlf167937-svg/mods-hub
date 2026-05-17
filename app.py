import os
from flask import Flask, render_template, abort

app = Flask(__name__)

BASE_UPLOAD_DIR = os.path.join('static', 'upload')

def parse_file_info(file_name):
    """
    Fungsi pintar untuk mendeteksi Loader dan Versi secara otomatis
    dari nama file (Contoh: mod_racikan_fabric_1.21.8)
    """
    name_lower = file_name.lower()
    loader = "Universal"
    version = "Unknown"
    
    # 1. Deteksi Mod Loader
    if "fabric" in name_lower:
        loader = "Fabric"
    elif "neoforge" in name_lower or "neo-forge" in name_lower:
        loader = "NeoForge"
    elif "forge" in name_lower:
        loader = "Forge"
    elif "quilt" in name_lower:
        loader = "Quilt"

    # 2. Deteksi Versi Game (Mencari pola angka versi seperti 1.21.8 atau 1.20)
    # Kita pecah string berdasarkan underscore '_' atau tanda strip '-'
    parts = name_lower.replace('-', '_').split('_')
    for part in parts:
        # Jika bagian string diawali dengan angka (misal: 1.21.8 atau 1.20)
        if part and part[0].isdigit() and '.' in part:
            # Bersihkan jika ada ekstensi file seperti .zip atau .jar
            version = part.split('.zip')[0].split('.jar')[0].split('.mcpack')[0]
            break
            
    return loader, version

def get_dynamic_mods():
    mods_list = []
    mod_id_counter = 1
    
    if not os.path.exists(BASE_UPLOAD_DIR):
        return mods_list

    for category in ['java', 'mcpe']:
        category_path = os.path.join(BASE_UPLOAD_DIR, category)
        if not os.path.exists(category_path):
            continue
            
        for mod_folder in os.listdir(category_path):
            mod_path = os.path.join(category_path, mod_folder)
            
            if os.path.isdir(mod_path):
                display_title = mod_folder.replace('-', ' ').title()
                
                # Setup Icon Path
                icon_url = f"/static/upload/{category}/{mod_folder}/icon.png"
                if not os.path.exists(os.path.join(mod_path, 'icon.png')):
                    icon_url = None
                
                versions = []
                game_versions_found = []
                
                # Scan semua file yang ada di dalam folder mod (Tanpa Sub-folder)
                for file_name in os.listdir(mod_path):
                    file_full_path = os.path.join(mod_path, file_name)
                    
                    # Abaikan file icon.png, hanya proses file mod/zip
                    if os.path.isfile(file_full_path) and file_name != 'icon.png' and not file_name.startswith('.'):
                        
                        # Ekstrak otomatis Loader dan Versi Game
                        loader, game_version = parse_file_info(file_name)
                        
                        if game_version != "Unknown":
                            game_versions_found.append(game_version)
                        
                        # Hitung Ukuran File Otomatis
                        try:
                            size_bytes = os.path.getsize(file_full_path)
                            if size_bytes < 1024 * 1024:
                                file_size = f"{round(size_bytes / 1024, 1)} KB"
                            else:
                                file_size = f"{round(size_bytes / (1024 * 1024), 1)} MB"
                        except:
                            file_size = "Unknown"
                        
                        # Bersihkan nama tampilan file agar rapi di tabel
                        clean_display_name = file_name.split('.zip')[0].split('.jar')[0].split('.mcpack')[0].replace('_', ' ').title()

                        versions.append({
                            "version_name": clean_display_name,
                            "loader": loader,
                            "game_version": game_version,
                            "file_size": file_size,
                            "download_url": f"/static/upload/{category}/{mod_folder}/{file_name}"
                        })

                # Urutkan file berdasarkan versi game terbaru
                versions.sort(key=lambda x: x['game_version'], reverse=True)
                
                # Tentukan range versi untuk card di dashboard
                if game_versions_found:
                    # Filter versi unik dan urutkan
                    unique_versions = sorted(list(set(game_versions_found)))
                    if len(unique_versions) > 1:
                        version_range = f"{unique_versions[0]} - {unique_versions[-1]}"
                    else:
                        version_range = unique_versions[0]
                else:
                    version_range = "Muti-Version"

                mods_list.append({
                    "id": mod_id_counter,
                    "category": category,
                    "name": mod_folder,
                    "title": display_title,
                    "desc": f"Berkas resmi kustom {display_title} untuk kategori Minecraft {category.upper()} Edition.",
                    "version_range": version_range,
                    "icon_url": icon_url,
                    "project_type": "Texture Pack" if category == 'mcpe' else "Mod / Optimization",
                    "versions": versions
                })
                mod_id_counter += 1
                
    return mods_list

@app.route('/')
def home_dashboard():
    return render_template('index.html', mods=get_dynamic_mods())

@app.route('/mod/<int:mod_id>')
def mod_detail_page(mod_id):
    all_mods = get_dynamic_mods()
    selected_mod = next((item for item in all_mods if item["id"] == mod_id), None)
            
    if selected_mod is None:
        abort(404)
        
    return render_template('mod.html', mod=selected_mod)

@app.errorhandler(404)
def page_not_found(error):
    return "<h1>404 - Berkas Tidak Ditemukan!</h1><p>Kembali ke <a href='/'>Dashboard RexCraft</a></p>", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
