import os
import sqlite3
from flask import Flask, render_template, abort, send_from_directory, jsonify

app = Flask(__name__)
BASE_UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
STATS_DB = os.path.join(app.root_path, 'stats.db')

def init_db():
    conn = sqlite3.connect(STATS_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats
                 (folder_name TEXT PRIMARY KEY, likes INTEGER DEFAULT 0, downloads INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def get_stats(folder_name):
    conn = sqlite3.connect(STATS_DB)
    c = conn.cursor()
    c.execute("SELECT likes, downloads FROM stats WHERE folder_name = ?", (folder_name,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'likes': row[0], 'downloads': row[1]}
    return {'likes': 0, 'downloads': 0}

def format_number(num):
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

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

def find_mod_components(files):
    icon_file = None
    mod_files = []
    icon_keywords = ['icon.jpg', 'icon.png', 'icon.jpeg', 'icon.webp', 'logo.png', 'logo.jpg']
    for f in files:
        if f.lower() == 'info.txt':
            continue
        elif f.lower() in icon_keywords:
            icon_file = f
        else:
            mod_files.append(f)
    return icon_file, sorted(mod_files, reverse=True)

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
                icon_file, mod_files = find_mod_components(files)
                stats = get_stats(folder_name)
                all_mods.append({
                    'id': mod_id_counter,
                    'folder_name': folder_name,
                    'platform': platform,
                    'title': meta['title'],
                    'category': meta['category'],
                    'desc': meta['desc'],
                    'icon': icon_file,
                    'files': mod_files,
                    'likes': stats['likes'],
                    'downloads': stats['downloads'],
                    'likes_fmt': format_number(stats['likes']),
                    'downloads_fmt': format_number(stats['downloads'])
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
    icon_file, mod_files = find_mod_components(files)
    stats = get_stats(folder_name)
    mod_data = {
        'folder_name': folder_name,
        'platform': platform,
        'title': meta['title'],
        'category': meta['category'],
        'desc': meta['desc'],
        'icon': icon_file,
        'files': mod_files,
        'likes': stats['likes'],
        'downloads': stats['downloads'],
        'likes_fmt': format_number(stats['likes']),
        'downloads_fmt': format_number(stats['downloads'])
    }
    return render_template('mod.html', mod=mod_data)

@app.route('/like/<folder_name>', methods=['POST'])
def like_mod(folder_name):
    conn = sqlite3.connect(STATS_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM stats WHERE folder_name = ?", (folder_name,))
    if c.fetchone():
        c.execute("UPDATE stats SET likes = likes + 1 WHERE folder_name = ?", (folder_name,))
    else:
        c.execute("INSERT INTO stats (folder_name, likes, downloads) VALUES (?, 1, 0)", (folder_name,))
    conn.commit()
    c.execute("SELECT likes FROM stats WHERE folder_name = ?", (folder_name,))
    new_likes = c.fetchone()[0]
    conn.close()
    return jsonify({'success': True, 'likes': new_likes, 'likes_fmt': format_number(new_likes)})

@app.route('/download/<platform>/<folder_name>/<filename>')
def download_file(platform, folder_name, filename):
    conn = sqlite3.connect(STATS_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM stats WHERE folder_name = ?", (folder_name,))
    if c.fetchone():
        c.execute("UPDATE stats SET downloads = downloads + 1 WHERE folder_name = ?", (folder_name,))
    else:
        c.execute("INSERT INTO stats (folder_name, likes, downloads) VALUES (?, 0, 1)", (folder_name,))
    conn.commit()
    conn.close()
    directory = os.path.join(BASE_UPLOAD_FOLDER, platform, folder_name)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/ai')
def ai(): return render_template('ai.html')

@app.route('/tutorial')
def tutorial(): return render_template('tutorial.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
