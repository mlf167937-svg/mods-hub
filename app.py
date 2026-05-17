# =========================================================================
# REXCRAFT MODS HUB - CORE ENGINE REVISION ULTIMATE (ANTI-CRASH DEPLOY)
# =========================================================================
import os
import re
from flask import Flask, render_template, abort

app = Flask(__name__)

BASE_UPLOAD_DIR = os.path.join('static', 'uploads')

# FUNGSI PINTAR UNTUK MENYORTIR VERSI MINECRAFT SECARA ALFABET DAN ANGKA (Menggantikan LooseVersion)
def version_key(version_str):
    if version_str == "Unknown" or not version_str:
        return [0]
    # Memecah string '1.21.11' menjadi list angka [1, 21, 11] supaya sorting matematika-nya akurat
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', version_str)]

def parse_file_info(file_name):
    name_lower = file_name.lower()
    loader = "Universal"
    version = "Unknown"
    
    if "fabric" in name_lower:
        loader = "Fabric"
    elif "neoforge" in name_lower or "neo-forge" in name_lower:
        loader = "NeoForge"
    elif "forge" in name_lower:
        loader = "Forge"
    elif "quilt" in name_lower:
        loader = "Quilt"

    # Mencari pola versi seperti 1.21.9 atau 1.20.4
    match = re.search(r'\d+\.\d+(?:\.\d+)?', name_lower)
    if match:
        version = match.group(0)
            
    return loader, version

def get_dynamic_mods():
    mods_list = []
    mod_id_counter = 1
    
    if not os.path.exists(BASE_UPLOAD_DIR):
        return mods_list

    # Mendukung folder dengan underscore (_) maupun dash (-)
    for category in ['java', 'mcpe']:
        category_path = os.path.join(BASE_UPLOAD_DIR, category)
        if not os.path.exists(category_path):
            continue
            
        for mod_folder in os.listdir(category_path):
            mod_path = os.path.join(category_path, mod_folder)
            
            if os.path.isdir(mod_path):
                # Mengubah mods_racikan atau mods-racikan menjadi "Mods Racikan"
                display_title = mod_folder.replace('-', ' ').replace('_', ' ').title()
                
                icon_url = f"/static/uploads/{category}/{mod_folder}/icon.png"
                if not os.path.exists(os.path.join(mod_path, 'icon.png')):
                    icon_url = None
                
                versions = []
                game_versions_found = []
                
                for file_name in os.listdir(mod_path):
                    file_full_path = os.path.join(mod_path, file_name)
                    
                    if os.path.isfile(file_full_path) and file_name != 'icon.png' and not file_name.startswith('.'):
                        loader, game_version = parse_file_info(file_name)
                        
                        if game_version != "Unknown":
                            game_versions_found.append(game_version)
                        
                        try:
                            size_bytes = os.path.getsize(file_full_path)
                            if size_bytes < 1024 * 1024:
                                file_size = f"{round(size_bytes / 1024, 1)} KB"
                            else:
                                file_size = f"{round(size_bytes / (1024 * 1024), 1)} MB"
                        except:
                            file_size = "Unknown"
                        
                        clean_display_name = file_name.split('.zip')[0].split('.jar')[0].split('.mcpack')[0].replace('_', ' ').title()

                        versions.append({
                            "version_name": clean_display_name,
                            "loader": loader,
                            "game_version": game_version,
                            "file_size": file_size,
                            "download_url": f"/static/uploads/{category}/{mod_folder}/{file_name}"
                        })

                # URUTKAN VERSI BERKAS INTERNAL (Menggunakan fungsi buatan sendiri yang aman)
                versions.sort(key=lambda x: version_key(x['game_version']), reverse=True)
                
                # JALUR PENGURUTAN RANGE VERSI DI HALAMAN DEPAN
                if game_versions_found:
                    unique_versions = sorted(list(set(game_versions_found)), key=version_key)
                    if len(unique_versions) > 1:
                        version_range = f"{unique_versions[0]} - {unique_versions[-1]}"
                    else:
                        version_range = unique_versions[0]
                else:
                    version_range = "Multi-Version"

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

# =========================================================================
# ROUTING CONTROLLER
# =========================================================================
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

@app.route('/tutorial')
def tutorial_page():
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panduan Tutorial - RexCraft</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght=400;600;800&display=swap" rel="stylesheet">
        <style>
            body { background-color: #07080b; color: #f1f5f9; font-family: 'Inter', sans-serif; padding: 40px 20px; text-align: center; }
            .box { max-width: 600px; margin: 60px auto; background: #111217; padding: 30px; border-radius: 12px; border: 1px solid #242836; }
            h1 { color: #00af9c; margin-bottom: 16px; }
            p { color: #94a3b8; font-size: 15px; line-height: 1.6; margin-bottom: 24px; }
            .btn { background: #00af9c; color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: 600; display: inline-block; }
            .btn:hover { background: #00d4bd; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>📖 Panduan Instalasi Berkas</h1>
            <p>Halaman tutorial RexCraft sedang dalam masa penyusunan asset gambar. Untuk memasang Mod / Texture Pack, silakan ekstrak berkas .zip atau .jar yang telah diunduh ke dalam folder internal direktori game Minecraft Anda (.minecraft/mods atau games/com.mojang/).</p>
            <a href="/" class="btn">Kembali ke Beranda</a>
        </div>
    </body>
    </html>
    """

@app.errorhandler(404)
def page_not_found(error):
    return "<h1>404 - Berkas Tidak Ditemukan!</h1><p>Kembali ke <a href='/'>Dashboard RexCraft</a></p>", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
