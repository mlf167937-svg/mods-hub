import os
import re
from flask import Flask, render_template, abort, send_from_directory

app = Flask(__name__)
BASE_UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')

def extract_version(filename):
    match = re.search(r'(\d+[\._]\d+(?:[\._]\d+)?)', filename)
    if match:
        clean_ver = match.group(1).replace('_', '.')
        return f"v{clean_ver}"
    return os.path.splitext(filename)[0]

def parse_info_file(folder_path):
    info = {
        'title': 'Mod Tanpa Judul',
        'category': 'Utility',
        'desc': 'Belum ada deskripsi untuk mod ini.'
    }
    info_path = os.path.join(folder_path, 'info.txt')
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                desc_lines = []
                inside_desc = False
                for line in lines:
                    if line.startswith('Judul:'):
                        info['title'] = line.replace('Judul:', '').strip()
                    elif line.startswith('Kategori:'):
                        info['category'] = line.replace('Kategori:', '').strip()
                    elif line.startswith('Deskripsi:'):
                        info['desc'] = line.replace('Deskripsi:', '').strip()
                        inside_desc = True
                    elif inside_desc:
                        desc_lines.append(line)
                if desc_lines:
                    info['desc'] += "\n" + "".join(desc_lines).strip()
        except Exception:
            pass
    return info

def find_mod_components(files, folder_path):
    icon_file = None
    mod_files = []
    gallery_map = {}
    gallery_items = []
    icon_keywords = ['icon.jpg', 'icon.png', 'icon.jpeg', 'icon.webp', 'logo.png', 'logo.jpg']
    
    for f in files:
        lower_f = f.lower()
        if lower_f == 'info.txt':
            continue
        elif lower_f in icon_keywords:
            icon_file = f
        elif lower_f.startswith('galery') or lower_f.startswith('gallery'):
            match = re.match(r'galer[yi](\d+)\.(png|jpg|jpeg|webp|txt)', lower_f)
            if match:
                num = int(match.group(1))
                ext = match.group(2)
                if num not in gallery_map:
                    gallery_map[num] = {'image': None, 'text': ''}
                if ext == 'txt':
                    txt_path = os.path.join(folder_path, f)
                    try:
                        with open(txt_path, 'r', encoding='utf-8') as txt_f:
                            gallery_map[num]['text'] = txt_f.read().strip()
                    except:
                        pass
                else:
                    gallery_map[num]['image'] = f
        else:
            version_display = extract_version(f)
            mod_files.append({
                'filename': f,
                'version': version_display
            })
            
    for num in sorted(gallery_map.keys()):
        if gallery_map[num]['image']:
            gallery_items.append(gallery_map[num])
            
    mod_files.sort(key=lambda x: x['version'], reverse=True)
    return icon_file, mod_files, gallery_items

def scan_mods():
    all_mods = []
    platforms = ['java', 'mcpe']
    mod_id_counter = 1
    for platform in platforms:
        platform_path = os.path.join(BASE_UPLOAD_FOLDER, platform)
        if not os.path.exists(platform_path):
            continue
        for folder_name in os.listdir(platform_path):
            folder_path = os.path.join(platform_path, folder_name)
            if os.path.isdir(folder_path):
                meta = parse_info_file(folder_path)
                files = os.listdir(folder_path)
                icon_file, mod_files, gallery_items = find_mod_components(files, folder_path)
                all_mods.append({
                    'id': mod_id_counter,
                    'folder_name': folder_name,
                    'platform': platform,
                    'title': meta['title'],
                    'category': meta['category'],
                    'desc': meta['desc'],
                    'icon': icon_file,
                    'files': mod_files,
                    'gallery': gallery_items
                })
                mod_id_counter += 1
    return all_mods

@app.route('/')
def index():
    mods = scan_mods()
    return render_template('index.html', mods=mods)

@app.route('/mod/<platform>/<folder_name>')
def mod_detail(platform, folder_name):
    folder_path = os.path.join(BASE_UPLOAD_FOLDER, platform, folder_name)
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        abort(404, "Folder mod tidak ditemukan di repositori")
    meta = parse_info_file(folder_path)
    files = os.listdir(folder_path)
    icon_file, mod_files, gallery_items = find_mod_components(files, folder_path)
    mod_data = {
        'folder_name': folder_name,
        'platform': platform,
        'title': meta['title'],
        'category': meta['category'],
        'desc': meta['desc'],
        'icon': icon_file,
        'files': mod_files,
        'gallery': gallery_items
    }
    return render_template('mod.html', mod=mod_data)

@app.route('/download/<platform>/<folder_name>/<filename>')
def download_file(platform, folder_name, filename):
    directory = os.path.join(BASE_UPLOAD_FOLDER, platform, folder_name)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/ai')
def ai(): return render_template('ai.html')

@app.route('/tutorial')
def tutorial(): return render_template('tutorial.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
