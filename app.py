# =========================================================================
# REXCRAFT MODS HUB - CORE ENGINE REVISION V2 (POPUP & LOADER TAG)
# =========================================================================
import os
import re
from flask import Flask, render_template, abort

app = Flask(__name__)

BASE_UPLOAD_DIR = os.path.join('static', 'uploads')

def version_key(version_str):
    if version_str == "Unknown" or not version_str:
        return [0]
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

    match = re.search(r'\d+\.\d+(?:\.\d+)?', name_lower)
    if match:
        version = match.group(0)
            
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
                display_title = mod_folder.replace('-', ' ').replace('_', ' ').title()
                
                icon_url = f"/static/uploads/{category}/{mod_folder}/icon.png"
                if not os.path.exists(os.path.join(mod_path, 'icon.png')):
                    icon_url = None
                
                versions = []
                game_versions_found = []
                loaders_found = []
                
                for file_name in os.listdir(mod_path):
                    file_full_path = os.path.join(mod_path, file_name)
                    
                    if os.path.isfile(file_full_path) and file_name != 'icon.png' and not file_name.startswith('.'):
                        loader, game_version = parse_file_info(file_name)
                        
                        if game_version != "Unknown":
                            game_versions_found.append(game_version)
                        if loader:
                            loaders_found.append(loader)
                        
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

                versions.sort(key=lambda x: version_key(x['game_version']), reverse=True)
                
                if game_versions_found:
                    unique_versions = sorted(list(set(game_versions_found)), key=version_key)
                    if len(unique_versions) > 1:
                        version_range = f"{unique_versions[0]} - {unique_versions[-1]}"
                    else:
                        version_range = unique_versions[0]
                else:
                    version_range = "Multi-Version"

                # Ambil daftar loader unik untuk ditampilkan di beranda
                unique_loaders = list(set(loaders_found)) if loaders_found else ["Universal"]

                mods_list.append({
                    "id": mod_id_counter,
                    "category": category,
                    "name": mod_folder,
                    "title": display_title,
                    "desc": f"Berkas resmi kustom {display_title} untuk kategori Minecraft {category.upper()} Edition.",
                    "version_range": version_range,
                    "loaders": unique_loaders, # Mengirim list loader ke index.html
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

# SOLUSI KELUHAN 2: PANDUAN PASANG MOD YANG LENGKAP & RAPI
@app.route('/tutorial')
def tutorial_page():
    return """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panduan Pemasangan - RexCraft</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root { --bg: #07080b; --surface: #111217; --border: #242836; --text: #f1f5f9; --muted: #94a3b8; --green: #00af9c; }
            body { background-color: var(--bg); color: var(--text); font-family: 'Inter', sans-serif; padding: 30px 15px; }
            .wrapper { max-width: 750px; margin: 0 auto; background: var(--surface); padding: 30px; border-radius: 12px; border: 1px solid var(--border); }
            h1 { color: var(--green); font-size: 24px; margin-bottom: 20px; text-align: center; font-weight: 800; }
            h2 { font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px; margin: 24px 0 12px 0; color: #fff; border-left: 4px solid var(--green); padding-left: 10px; }
            p { color: var(--muted); font-size: 14.5px; line-height: 1.6; margin-bottom: 12px; }
            ol { margin-left: 20px; color: #cbd5e1; font-size: 14px; }
            li { margin-bottom: 10px; line-height: 1.5; }
            .code-box { background: #161920; padding: 10px 14px; border-radius: 6px; border: 1px solid var(--border); font-family: monospace; font-size: 13px; color: #e2e8f0; display: block; margin: 8px 0; }
            .btn { display: inline-block; background: var(--green); color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; font-size: 14px; margin-top: 25px; text-align: center; width: 100%; box-sizing: border-box; }
            .btn:hover { background: #00d4bd; }
        </style>
    </head>
    <body>
        <div class="wrapper">
            <h1><i class="fas fa-book-open"></i> Panduan Lengkap Pemasangan Berkas</h1>
            <p>Ikuti instruksi di bawah ini untuk memasang berkas optimasi RexCraft ke dalam game Minecraft Anda dengan aman tanpa menimbulkan sirkuit putus data.</p>
            
            <h2>1. Kategori Minecraft Java Edition (PC)</h2>
            <ol>
                <li>Pastikan Anda telah memasang Mod Loader yang sesuai (seperti <b>Fabric</b> atau <b>Forge</b>) pada launcher game Anda.</li>
                <li>Unduh berkas mod berformat <code>.jar</code> atau <code>.zip</code> dari web RexCraft.</li>
                <li>Buka Windows Run dengan menekan tombol kombinasi <kbd>Win + R</kbd> di keyboard Anda.</li>
                <li>Ketik perintah berikut lalu tekan Enter: <span class="code-box">%appdata%\.minecraft\mods</span></li>
                <li>Pindahkan berkas mod yang baru saja Anda unduh ke dalam folder <b>mods</b> tersebut.</li>
                <li>Jalankan Minecraft Anda sesuai dengan profil Mod Loader-nya. Selesai!</li>
            </ol>

            <h2>2. Kategori Minecraft Bedrock / MCPE (Android & iOS)</h2>
            <ol>
                <li>Unduh berkas Texture Pack atau Addon dari RexCraft yang berformat <code>.mcpack</code> atau <code>.zip</code>.</li>
                <li>Jika berkas berupa <b>.mcpack</b>, cukup klik berkas tersebut menggunakan file manager, lalu pilih buka dengan aplikasi game <b>Minecraft</b>. Game akan otomatis mengimpor berkas tersebut.</li>
                <li>Jika berkas berupa <b>.zip</b>, ekstrak folder tersebut lalu pindahkan folders hasil ekstrak secara manual ke direktori internal:
                    <span class="code-box">Android/data/com.mojang.minecraftpe/files/games/com.mojang/resource_packs</span>
                </li>
                <li>Masuk ke dalam game Minecraft, buka menu Pengaturan (Settings) &gt; Global Resources, lalu aktifkan pack tersebut.</li>
            </ol>

            <a href="/" class="btn"><i class="fas fa-chevron-left"></i> Kembali ke Dashboard Utama</a>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
