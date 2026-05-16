from flask import Flask, render_template
import os

app = Flask(__name__)

# FOLDER

JAVA_FOLDER = "static/uploads/java"
MCPE_FOLDER = "static/uploads/mcpe"

# FORMAT SIZE

def ukuran_file(path):

    size = os.path.getsize(path)

    if size < 1024:
        return f"{size} B"

    elif size < 1024 * 1024:
        return f"{size/1024:.1f} KB"

    elif size < 1024 * 1024 * 1024:
        return f"{size/(1024*1024):.1f} MB"

    else:
        return f"{size/(1024*1024*1024):.1f} GB"

# AMBIL FILE

def ambil_file(folder, kategori):

    hasil = []

    if os.path.exists(folder):

        for file in os.listdir(folder):

            filepath = os.path.join(folder, file)

            if os.path.isfile(filepath):

                hasil.append({

                    "name": file,

                    "category": kategori,

                    "size": ukuran_file(filepath),

                    "path": filepath.replace("static/", "")

                })

    return hasil

# HOME

@app.route("/")
def home():

    java = ambil_file(
        JAVA_FOLDER,
        "Java"
    )

    mcpe = ambil_file(
        MCPE_FOLDER,
        "MCPE"
    )

    mods = java + mcpe

    return render_template(
        "index.html",
        mods=mods
    )

# RUN

if __name__ == "__main__":
    app.run()
