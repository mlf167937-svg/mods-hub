import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 # Max 500MB

# Bikin folder otomatis biar gak error
for platform in ['java', 'mcpe']:
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], platform), exist_ok=True)

# Setup Database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mods
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  title TEXT, desc TEXT, platform TEXT, 
                  category TEXT, loader TEXT, version TEXT, 
                  icon_filename TEXT, file_filename TEXT, 
                  downloads INTEGER DEFAULT 0, likes INTEGER DEFAULT 0)''')
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
    mods = conn.execute('SELECT * FROM mods ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', mods=mods)

@app.route('/mod/<int:id>')
def mod_detail(id):
    conn = get_db()
    mod = conn.execute('SELECT * FROM mods WHERE id = ?', (id,)).fetchone()
    conn.close()
    if mod is None:
        return "Mod tidak ditemukan", 404
    return render_template('mod.html', mod=mod)

@app.route('/download/<int:id>')
def download(id):
    conn = get_db()
    conn.execute('UPDATE mods SET downloads = downloads + 1 WHERE id = ?', (id,))
    conn.commit()
    mod = conn.execute('SELECT * FROM mods WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    # Path ke file: static/uploads/<platform>/<folder_mod>/<file>
    directory = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], mod['platform'], str(mod['id']))
    return send_from_directory(directory, mod['file_filename'], as_attachment=True)

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
        loader = request.form['loader']
        version = request.form['version']
        
        icon = request.files['icon']
        file = request.files['file']
        
        if icon and file:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO mods (title, desc, platform, category, loader, version) VALUES (?, ?, ?, ?, ?, ?)',
                         (title, desc, platform, category, loader, version))
            mod_id = cursor.lastrowid
            
            # Buat folder khusus ID mod ini
            mod_folder = os.path.join(app.config['UPLOAD_FOLDER'], platform, str(mod_id))
            os.makedirs(mod_folder, exist_ok=True)
            
            icon_name = secure_filename(icon.filename)
            file_name = secure_filename(file.filename)
            
            icon.save(os.path.join(mod_folder, icon_name))
            file.save(os.path.join(mod_folder, file_name))
            
            cursor.execute('UPDATE mods SET icon_filename = ?, file_filename = ? WHERE id = ?', (icon_name, file_name, mod_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
            
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
