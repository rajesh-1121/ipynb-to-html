from flask import Flask, request, jsonify, send_file, render_template
import nbformat
from nbconvert import HTMLExporter
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    file = request.files['file']
    if file:
        try:
            notebook = nbformat.reads(file.read(), as_version=4)
            html_exporter = HTMLExporter()
            html_exporter.template_name = 'classic'
            (body, _) = html_exporter.from_notebook_node(notebook)
            
            tmpdir = tempfile.mkdtemp()  # Create a temporary directory
            html_path = os.path.join(tmpdir, 'converted.html')
            with open(html_path, 'w') as f:
                f.write(body)

            # Store only the basename of the temporary directory in the session or pass to the client
            view_path = '/view/' + os.path.basename(tmpdir)
            download_path = '/download/' + os.path.basename(tmpdir)
            return jsonify({'viewPath': view_path, 'downloadPath': download_path})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'No file uploaded'}), 400

@app.route('/view/<path>')
def view_html(path):
    # Construct the full path to the file using the basename
    file_path = os.path.join(tempfile.gettempdir(), path, 'converted.html')
    return send_file(file_path)

@app.route('/download/<path>')
def download_html(path):
    # Construct the full path to the file using the basename
    file_path = os.path.join(tempfile.gettempdir(), path, 'converted.html')
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
