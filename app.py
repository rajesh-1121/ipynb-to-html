from flask import Flask, request, jsonify, send_file, render_template
import nbformat
from nbconvert import HTMLExporter
import os
import tempfile
from collections import Counter

app = Flask(__name__)

# Global counters for visits and file conversions
stats = Counter({'visits': 0, 'conversions': 0})

@app.route('/')
def index():
    # Increment the visit counter
    stats['visits'] += 1
    return render_template('index.html', visits=stats['visits'], conversions=stats['conversions'])

@app.route('/convert', methods=['POST'])
def convert():
    files = request.files.getlist('files')  # Get multiple files from the form
    if files:
        try:
            converted_files = []
            for file in files:
                notebook = nbformat.reads(file.read(), as_version=4)
                html_exporter = HTMLExporter()
                html_exporter.template_name = 'classic'
                (body, _) = html_exporter.from_notebook_node(notebook)
                
                # Create a temporary directory for each file
                tmpdir = tempfile.mkdtemp()
                html_path = os.path.join(tmpdir, 'converted.html')
                with open(html_path, 'w') as f:
                    f.write(body)

                # Store the view and download paths for this file
                converted_files.append({
                    'name': file.filename,
                    'viewPath': '/view/' + os.path.basename(tmpdir),
                    'downloadPath': '/download/' + os.path.basename(tmpdir)
                })

            # Increment the conversion counter by the number of files converted
            stats['conversions'] += len(files)

            return jsonify({'files': converted_files})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'error': 'No files uploaded'}), 400

@app.route('/view/<path>')
def view_html(path):
    file_path = os.path.join(tempfile.gettempdir(), path, 'converted.html')
    return send_file(file_path)

@app.route('/download/<path>')
def download_html(path):
    file_path = os.path.join(tempfile.gettempdir(), path, 'converted.html')
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
