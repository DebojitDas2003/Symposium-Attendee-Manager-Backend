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


# Download XLSX with attendees' data, including collected items
@app.route('/download/xlsx', methods=['GET'])
def download_attendees_xlsx():
    df = pd.DataFrame(attendees)
    df['Items'] = df['items_received'].apply(lambda x: ', '.join(x))
    filepath = os.path.join(DOWNLOADS_FOLDER, 'attendees.xlsx')
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    df = pd.read_excel(file)
    attendees.clear()
    for _, row in df.iterrows():
        attendees.append({
            "name": row["Name"],
            "mobile_no": row["Mobile No"],
            "email_id": row["Email ID"],
            "organisation": row["Company / Organisation"],
            "items_received": [],  # Initialize as empty if no items
        })
    return jsonify({"message": "Data uploaded", "count": len(attendees)})



# Add new attendee or update items collected
@app.route('/attendees', methods=['GET', 'POST'])
def attendees_data():
    if request.method == 'POST':
        data = request.json
        attendees[data['index']]['items_received'] = data['items_received']
        return jsonify({"message": "Attendee updated"})
    return jsonify(attendees)


# Add new attendee
@app.route('/add', methods=['POST'])
def add_attendee():
    data = request.json
    attendees.append(data)
    return jsonify({"message": "Attendee added", "count": len(attendees)})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
