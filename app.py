import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # Batas maksimum 500MB

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Tabel Utama Mod (Satu Mod punya satu folder tunggal)
    c.execute('''CREATE TABLE IF NOT EXISTS mods
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT UNIQUE, desc TEXT, platform TEXT, 
                  category TEXT, folder_name TEXT, icon_filename TEXT,
                  likes INTEGER DEFAULT 0)''')
    # Tabel Versi File (Numpuk di dalam folder mod yang sama)
    c.execute('''CREATE TABLE IF NOT EXISTS versions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  mod_id INTEGER, game_version TEXT, loader TEXT,
                  file_filename TEXT, downloads INTEGER DEFAULT 0,
                  FOREIGN KEY(mod_id) REFERENCES mods(id))''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db()
    # Ambil data mod beserta total download akumulasi dari semua filenya
    mods = conn.execute('''
        SELECT m.*, CAST(TOTAL(v.downloads) AS INTEGER) as total_downloads,
               GROUP_CONCAT(DISTINCT v.game_version) as app_versions
        FROM mods m
        LEFT JOIN versions v ON m.id = v.mod_id
        GROUP BY m.id
        ORDER BY m.id DESC
    ''').fetchall()
    conn.close()
    return render_template('index.html', mods=mods)

@app.route('/mod/<int:id>')
def mod_detail(id):
    conn = get_db()
    mod = conn.execute('SELECT * FROM mods WHERE id = ?', (id,)).fetchone()
    if mod is None:
        conn.close()
        return "Mod tidak ditemukan", 404
    # Ambil list semua file versi yang ada di dalam folder mod ini
    versions = conn.execute('SELECT * FROM versions WHERE mod_id = ? ORDER BY id DESC', (id,)).fetchall()
    conn.close()
    return render_template('mod.html', mod=mod, versions=versions)

@app.route('/download/<int:version_id>')
def download(version_id):
    conn = get_db()
    version = conn.execute('''
        SELECT v.*, m.platform, m.folder_name 
        FROM versions v 
        JOIN mods m ON v.mod_id = m.id 
        WHERE v.id = ?''', (version_id,)).fetchone()
    
    if version is None:
        conn.close()
        return "Berkas versi tidak ditemukan", 404
        
    conn.execute('UPDATE versions SET downloads = downloads + 1 WHERE id = ?', (version_id,))
    conn.commit()
    conn.close()
    
    # PATH BARU: static/uploads/<platform>/<folder_name>/<file_filename>
    directory = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], version['platform'], version['folder_name'])
    return send_from_directory(directory, version['file_filename'], as_attachment=True)

@app.route('/like/<int:id>', methods=['POST'])
def like_mod(id):
    conn = get_db()
    conn.execute('UPDATE mods SET likes = likes + 1 WHERE id = ?', (id,))
    conn.commit()
    mod = conn.execute('SELECT likes FROM mods WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify({'success': True, 'new_likes': mod['likes']})

@app.route('/ai')
def ai(): return render_template('ai.html')

@app.route('/tutorial')
def tutorial(): return render_template('tutorial.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']
        platform = request.form['platform']
        category = request.form['category']
        game_version = request.form['game_version'].strip()
        loader = request.form['loader']
        
        icon = request.files['icon']
        file = request.files['file']
        
        if icon and file:
            folder_name = secure_filename(title.lower().replace(' ', '_'))
            icon_name = secure_filename(icon.filename)
            file_name = secure_filename(file.filename)
            
            # Target Folder: static/uploads/<platform>/<folder_name>
            mod_folder = os.path.join(app.config['UPLOAD_FOLDER'], platform, folder_name)
            os.makedirs(mod_folder, exist_ok=True)
            
            # Simpan Icon & File langsung ke folder yang sama
            icon.save(os.path.join(mod_folder, icon_name))
            file.save(os.path.join(mod_folder, file_name))
            
            conn = get_db()
            cursor = conn.cursor()
            
            try:
                # Daftarkan induk mod baru jika belum ada
                cursor.execute('''INSERT INTO mods (title, desc, platform, category, folder_name, icon_filename) 
                                  VALUES (?, ?, ?, ?, ?, ?)''', 
                               (title, desc, platform, category, folder_name, icon_name))
                mod_id = cursor.lastrowid
            except sqlite3.IntegrityError:
                # Jika induk mod sudah terdaftar, ambil ID lamanya untuk numpang simpan file versi baru
                mod_data = cursor.execute('SELECT id FROM mods WHERE title = ?', (title,)).fetchone()
                mod_id = mod_data['id']
                cursor.execute('UPDATE mods SET desc = ?, category = ?, icon_filename = ? WHERE id = ?', 
                               (desc, category, icon_name, mod_id))
            
            # Masukkan berkas versi barunya ke dalam manifest database
            cursor.execute('''INSERT INTO versions (mod_id, game_version, loader, file_filename) 
                              VALUES (?, ?, ?, ?)''', 
                           (mod_id, game_version, loader, file_name))
            
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
            
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
