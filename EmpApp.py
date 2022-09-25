from unittest import result
from flask import Flask, render_template, request, flash, send_file
from pymysql import connections
import os
import boto3
from config import *
# from tables import Results

app = Flask(__name__, static_folder="templates")
app.secret_key = "super secret key"

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

headings=("Employee ID","First Name","Last Name","Primary Skill","Location", "Image")

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select an image file"

    try:

        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''

            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

            cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, object_url))
            db_conn.commit()

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)


@app.route("/reademp", methods=['GET','POST'])
def ReadEmp():
    read_sql  = "SELECT * FROM employee"
    cursor = db_conn.cursor()

    try:
        cursor.execute(read_sql)
        db_conn.commit()
        data = cursor.fetchall()
        return render_template('GetEmpOutput.html', headings = headings, data = data)

    except Exception as e: 
        return str(e)
    finally:
        cursor.close()


@app.route("/removeemp", methods=['GET','POST'])
def RemoveEmp(empid):
    # emp_id = request.form['emp_id']
    emp_id = empid

    removeTarget = "" + emp_id
    search_sql =("SELECT image FROM employee WHERE emp_id = %s")
    cursor = db_conn.cursor()

    try:
        cursor.execute(search_sql,emp_id)
        db_conn.commit()
        row = cursor.fetchone()
        if row: 
            keypath = row.image

        s3 = boto3.resource('s3')
        s3.delete_object(Bucket= bucket, Key= keypath)

        remove_sql =("DELETE FROM employee WHERE emp_id= %s")
        cursor.execute(remove_sql,emp_id)
        db_conn.commit()

    except Exception as e: 
        return (e)
    finally:
        cursor.close()

    flash("Employee Successfully Removed")
    return render_template('RemoveEmpOutput.html', name = str(removeTarget))


@app.route("/searchemp", methods=['GET','POST'])
def SearchEmp():
    emp_id = request.form['emp_id']

    search_sql =("SELECT * FROM employee WHERE emp_id = %s")
    cursor = db_conn.cursor()

    if emp_id =="": 
        return "Please enter Employee ID"
        
    try: 
        cursor.execute(search_sql,emp_id)
        db_conn.commit()
        row = cursor.fetchone()
        if row: 
            return render_template('UpdateEmpOutput.html',row = row)
        else:
            return "ID Not Found"
    except Exception as e: 
        print(e)
    finally:
        cursor.close()


@app.route("/updateemp", methods=['GET','POST'])
def UpdateEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    if emp_id == "": 
        return "Please enter Employee ID"
    elif first_name == "":
        return "Please enter First Name"
    elif last_name =="":
        return "Please enter Last Name"
    elif pri_skill =="":
        return "Please enter Primary Skill"
    elif location =="":
        return "Please enter Location"
    elif emp_image_file == "":
        return "Please select an Image"

    insert_sql = ("UPDATE employee SET first_name=%s, last_name=%s, pri_skill=%s, location=%s, image=%s WHERE emp_id=%s")
    cursor = db_conn.cursor()

    try:
        emp_name = "" + first_name + " " + last_name

        try:
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
            s3 = boto3.resource('s3')
            s3.Bucket(custombucket).put_object(Key = emp_image_file_name_in_s3, Body = emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket = custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None: 
                s3_location = ''
            else: 
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

            cursor.execute(insert_sql, (first_name, last_name, pri_skill, location, emp_id, object_url))
            db_conn.commit()

        except Exception as e: 
            return str(e)


    except Exception as e:
        return str(e)
    finally:
        cursor.close()
    
    print("Update Succesfully")
    return render_template('UpResults.html', name = emp_name)


@app.route("/updateprofile/<empid>")
def updateprofile(empid):
    row = empid
    select_sql = "SELECT * from employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql, row)
    row = cursor.fetchone()
    return render_template('UpdateEmpOutput.html', row = row)

@app.route("/removeprofile/<empid>")
def removeprofile(empid):
    id = empid
    RemoveEmp(id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    app.debug = True
    app.run()