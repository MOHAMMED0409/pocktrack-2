from flask import Flask, render_template, request, redirect, url_for, flash
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Google Sheets Setup
def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

# Fetch the Google Sheet
def get_employee_data(sheet_name):
    client = setup_google_sheets()
    sheet = client.open(sheet_name).sheet1
    return sheet.get_all_records(), sheet

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_employee():
    emp_number = request.form['emp_number']
    try:
        employee_list_data, _ = get_employee_data("Employee List")
        employee_data, _ = get_employee_data("Employee Data")
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'error')
        return redirect(url_for('index'))

    employee_found = False
    employee_details = {}
    for row in employee_list_data:
        if str(row['Employee No']) == emp_number:
            employee_details = {
                'name': row['Name'],
                'dept': row['Department'],
                'mobile': str(row['Mobile'])
            }
            employee_found = True
            break

    if employee_found:
        for row in employee_data:
            if str(row['Employee No']) == emp_number:
                medical_options = ["General Physician", "Cardiologist", "Ophthalmologist", "Gynecologist", "Dietician"]
                for option in medical_options:
                    employee_details[option] = row.get(option, "No") == "Yes"
                break
    else:
        flash('Employee not found!', 'error')
        return redirect(url_for('index'))

    return render_template('search_result.html', employee_details=employee_details, emp_number=emp_number)

@app.route('/submit', methods=['POST'])
def submit_employee():
    emp_number = request.form['emp_number']
    name = request.form['name']
    dept = request.form['dept']
    mobile = request.form['mobile']
    medical_options = ["General Physician", "Cardiologist", "Ophthalmologist", "Gynecologist", "Dietician"]
    options = ["Yes" if request.form.get(option) == 'on' else "No" for option in medical_options]

    if not (emp_number and name and dept and mobile):
        flash('All fields must be filled!', 'error')
        return redirect(url_for('index'))

    employee_details = [emp_number, name, dept, mobile] + options

    try:
        client = setup_google_sheets()
        sheet = client.open("Employee Data").sheet1

        cell = sheet.find(emp_number)
        col_count = len(employee_details)
        if cell:
            sheet.update(f'A{cell.row}:{chr(64+col_count)}{cell.row}', [employee_details])
        else:
            sheet.append_row(employee_details)
        flash('Employee details saved successfully!', 'success')
    except Exception as e:
        flash(f'Error saving data to Google Sheets: {str(e)}', 'error')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
