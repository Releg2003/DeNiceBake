from flask import Flask, render_template, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("custom.html")

@app.route("/submit", methods=["POST"])
def submit_order():
    size = request.form.get("size")
    flavor = request.form.get("flavor")

    
    shape = request.form.get("shape")
    message = request.form.get("message")
    toppings = request.form.getlist("toppings")

    img_file = request.files.get("cakeImage")
    img_filename = None
    if img_file and img_file.filename:
        img_filename = os.path.join(UPLOAD_FOLDER, img_file.filename)
        img_file.save(img_filename)

    # For simplicity we just return JSON
    return {
        "status": "success",
        "size": size,
        "flavor": flavor,
        "shape": shape,
        "message": message,
        "toppings": toppings,
        "image": img_file.filename if img_file else None
    }

if __name__ == "__main__":
    app.run(debug=True)
