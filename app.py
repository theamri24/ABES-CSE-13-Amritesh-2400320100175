from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import io

app = Flask(__name__)

# Limit accepted extensions
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only .xls or .xlsx allowed'}), 400

    filename = secure_filename(file.filename)

    # Read Excel into DataFrame without saving to disk
    try:
        # Read first sheet by default
        bytes_buf = io.BytesIO(file.read())
        df = pd.read_excel(bytes_buf)  # supports xls/xlsx with appropriate engines
    except Exception as e:
        return jsonify({'error': f'Failed to read Excel: {str(e)}'}), 400

    if df.shape[1] < 2 or df.shape[0] < 1:
        return jsonify({'error': 'Excel must have at least two columns and one row'}), 400

    # Use first two columns generically
    col_x = df.columns[0]
    col_y = df.columns[1]

    # Drop rows where either is NaN
    plot_df = df[[col_x, col_y]].dropna()

    # Convert to plain Python lists (for JSON)
    x = plot_df[col_x].astype(object).tolist()
    y = plot_df[col_y].astype(float).tolist()

    return jsonify({
        'x': x,
        'y': y,
        'x_label': str(col_x),
        'y_label': str(col_y),
        'title': f'{col_y} vs {col_x}'
    })

if __name__ == '__main__':
    # For development purposes
    app.run(debug=True)
