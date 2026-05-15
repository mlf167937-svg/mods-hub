from flask import Flask, render_template, request, redirect, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

mods = []


@app.route("/")
def home():
    return render_template("index.html", mods=mods)


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        title = request.form["title"]
        version = request.form["version"]
        desc = request.form["desc"]

        file = request.files["file"]

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)

        file.save(filepath)

        mods.append({
            "title": title,
            "version": version,
            "desc": desc,
            "file": file.filename
        })

        return redirect("/")

    return render_template("upload.html")


@app.route("/mod/<filename>")
def mod_page(filename):

    mod = None

    for m in mods:
        if m["file"] == filename:
            mod = m

    return render_template("mod.html", mod=mod)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run()
