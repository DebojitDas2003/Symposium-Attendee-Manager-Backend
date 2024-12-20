# Documentation for Flask Application

## Overview

This application is a **Flask-based API** that manages attendee data. It allows uploading data from an Excel file, storing it in memory, and supports the following operations:

- Adding or updating attendees
- Downloading attendees as **XLSX** or **PDF**
- Serving and retrieving attendee data via **JSON**

It uses the following key modules:

- `Flask`: Web framework for API routes.
- `pandas`: For data manipulation and reading/writing Excel files.
- `FPDF`: For generating PDF reports.

---

## Code Structure and Functionality

### 1. **Setup and Configuration**

```python
import os
from flask import Flask, request, jsonify, send_file
import pandas as pd
from fpdf import FPDF
```

- **os**: Used to handle file paths and locations.
- **Flask**: Core framework used to build the web server and routes.
- **pandas**: For reading Excel files and data transformation.
- **FPDF**: For generating PDF files.

```python
app = Flask(__name__)
attendees = []  # In-memory storage
DOWNLOADS_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads')
```

- **app**: Creates a Flask web server instance.
- **attendees**: Stores attendee data in memory as a list of dictionaries.
- **DOWNLOADS_FOLDER**: Sets the download location to the user’s Downloads directory.

---

### 2. **Routes and Endpoints**

#### **2.1 Hello World Route**

```python
@app.route("/")
def hello():
    return "Hello, World!"
```

- **GET** request to the root (`/`) returns a greeting message.

---

#### **2.2 Upload Attendees from Excel File**

```python
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
            "items_received": items
        })
    return jsonify({"message": "Data uploaded", "count": len(attendees)})
```

- **POST** to `/upload` allows uploading an Excel (`.xlsx`) file.
- Reads the file, extracts attendee information, and clears the previous data.
- Converts comma-separated items into a list.
- Returns the **number of attendees** uploaded.

---

#### **2.3 Download Attendees as Excel (XLSX)**

```python
@app.route('/download/xlsx', methods=['GET'])
def download_xlsx():
    df = pd.DataFrame(attendees)
    df['Items'] = df['items_received'].apply(lambda x: ', '.join(x))
    filepath = os.path.join(DOWNLOADS_FOLDER, 'attendees.xlsx')
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)
```

- **GET** request to `/download/xlsx` creates an **Excel file** with attendee data.
- **Returns** the generated file for download.

---

#### **2.4 Download Attendees as PDF**

```python
@app.route('/download/pdf', methods=['GET'])
def download_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Attendee List", ln=True, align='C')
    for attendee in attendees:
        items = ', '.join(attendee['items_received'])
        pdf.cell(200, 10, txt=f"{attendee['name']} - {attendee['designation']} - {items}", ln=True)
    filepath = os.path.join(DOWNLOADS_FOLDER, 'attendees.pdf')
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)
```

- **GET** request to `/download/pdf` generates a **PDF file** listing all attendees.
- Each attendee is represented by:
  - **Name**
  - **Designation**
  - **Items received**
- Returns the PDF for download.

---

#### **2.5 Get or Update Attendee Data (JSON)**

```python
@app.route('/attendees', methods=['GET', 'POST'])
def attendees_data():
    if request.method == 'POST':
        data = request.json
        attendees[data['index']]['items_received'] = data['items_received']
        return jsonify({"message": "Attendee updated"})
    return jsonify(attendees)
```

- **GET**: Retrieves the list of attendees in JSON format.
- **POST**: Updates an attendee's `items_received` field based on the provided index.

---

#### **2.6 Add a New Attendee**

```python
@app.route('/add', methods=['POST'])
def add_attendee():
    data = request.json
    attendees.append(data)  # Add new guest to the list.
    return jsonify({"message": "Attendee added", "count": len(attendees)})
```

- **POST** request to `/add` allows adding a **new attendee** to the list.
- **JSON body** should include attendee details.

---

### 3. **Main Application Execution**

```python
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
```

- Runs the Flask app on port **5000** (default) or a port specified in the `PORT` environment variable.
- **Debug mode** is enabled for easier development and testing.

---

## Example Usage

1. **Start the Flask Server**:

   ```bash
   python app.py
   ```

2. **Upload Excel File** (POST `/upload`):

   ```bash
   curl -F 'file=@attendees.xlsx' http://localhost:5000/upload
   ```

3. **Download Attendees as XLSX**:

   - Open: [http://localhost:5000/download/xlsx](http://localhost:5000/download/xlsx)

4. **Download Attendees as PDF**:

   - Open: [http://localhost:5000/download/pdf](http://localhost:5000/download/pdf)

5. **Add a New Attendee** (POST `/add`):

   ```bash
   curl -X POST http://localhost:5000/add -H "Content-Type: application/json" \
   -d '{"name": "John Doe", "designation": "Manager", "items_received": ["Notebook", "Pen"]}'
   ```

6. **Get Attendee List** (GET `/attendees`):
   ```bash
   curl http://localhost:5000/attendees
   ```

---

## Dependencies

Install the required packages using:

```bash
pip install Flask pandas fpdf
```

---

## Error Handling

- Ensure that the uploaded file is a **valid Excel file**; otherwise, `pandas` will raise an error.
- Data is **stored in memory** and will be lost when the server restarts.

---

## Known Issues

- Duplicate definitions for the `download_xlsx` and `download_pdf` routes cause **errors**. Remove one of each duplicate to avoid conflicts.
- This application stores data **in-memory**, which makes it unsuitable for production unless integrated with a **database**.

---

## Improvements

1. **Database Integration**: Use a database (like **SQLite** or **MongoDB**) to persist attendee data.
2. **File Validation**: Add file type checks during upload.
3. **Authentication**: Secure endpoints with **authentication/authorization**.

---

## Conclusion

This Flask application provides a simple interface for managing attendees using Excel uploads and JSON interactions. With both **PDF and Excel exports**, it offers versatile reporting options, though improvements are needed for scalability and security.
