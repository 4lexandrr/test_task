from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
import os
import pandas as pd

auth = HTTPBasicAuth()
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth.verify_password
def verify_password(username, password):
    # Демонстрационная проверка
    if username == 'user' and password == 'password':
        return True
    return False

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file and allowed_file(file.filename):
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return jsonify({"message": "File uploaded successfully"})

    return jsonify({"error": "Invalid file type"})

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({"files": files})

@app.route('/data/<filename>', methods=['GET'])
def get_data(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"})

    df = pd.read_csv(file_path)

    # Опциональная фильтрация по столбцам
    filter_columns = request.args.getlist('filter_columns')
    for column in filter_columns:
        filter_value = request.args.get(column)
        if filter_value:
            df = df[df[column] == filter_value]

    # Опциональная сортировка по столбцам
    sort_columns = request.args.getlist('sort_columns')
    if sort_columns:
        df = df.sort_values(by=sort_columns)

    return df.to_json(orient='records')

@app.route('/delete/<filename>', methods=['DELETE'])
@auth.login_required
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"})

    os.remove(file_path)
    return jsonify({"message": f"File {filename} deleted successfully"})

if __name__ == '__main__':
    app.run(debug=True)
