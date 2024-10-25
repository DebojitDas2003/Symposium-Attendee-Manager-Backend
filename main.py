import os
from flask import Flask, request, jsonify, send_file
import pandas as pd
from fpdf import FPDF

app = Flask(__name__)
attendees = []  # In-memory storage

DOWNLOADS_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads')


@app.route("/")
def hello():
    return "Hello, World!"


# Convert XLSX to JSON and store in 'attendees'
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    df = pd.read_excel(file)
    attendees.clear()
    for _, row in df.iterrows():
        items = row["Items"].split(',') if pd.notna(row["Items"]) else []
        attendees.append({
            "name": row["Name"],
            "designation": row["Designation"],
            "items_received": items,
            "mobile": row.get("Mobile No", ""),
            "email": row.get("Email ID", ""),
            "organisation": row.get("Company / Organisation", ""),
        })
    return jsonify({"message": "Data uploaded", "count": len(attendees)})


@app.route('/download/xlsx', methods=['GET'])
def download_attendees_xlsx():
    df = pd.DataFrame(attendees)
    df['Items'] = df['items_received'].apply(lambda x: ', '.join(x))
    filepath = os.path.join(DOWNLOADS_FOLDER, 'attendees.xlsx')
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)


@app.route('/download/pdf', methods=['GET'])
def download_attendees_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Attendee List", ln=True, align='C')
    for attendee in attendees:
        items = ', '.join(attendee['items_received'])
        pdf.cell(
            200,
            10,
            txt=f"{attendee['name']} - {attendee['designation']} - {items}",
            ln=True,
        )
    filepath = os.path.join(DOWNLOADS_FOLDER, 'attendees.pdf')
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)


@app.route('/attendees', methods=['GET', 'POST'])
def attendees_data():
    if request.method == 'POST':
        data = request.json
        attendees[data['index']]['items_received'] = data['items_received']
        return jsonify({"message": "Attendee updated"})
    return jsonify(attendees)


@app.route('/add', methods=['POST'])
def add_attendee():
    data = request.json
    attendees.append(data)  # Add new guest to the list.
    return jsonify({"message": "Attendee added", "count": len(attendees)})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
