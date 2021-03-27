from flask import Flask, render_template,request, redirect,url_for
import pymysql
import cv2
import qrcode
import datetime
import string
import re

host = "remotemysql.com"
user = "BrRG0FGAdO"
password = "m6PQEFhHS6"
database="BrRG0FGAdO"
'''
Username: BrRG0FGAdO

Database name: BrRG0FGAdO

Password: m6PQEFhHS6

Server: remotemysql.com

Port: 3306

'''

app = Flask(__name__)

cur = None
connection = None
html_data={}
ep="^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$" #Email regex
np="^[A-Za-z ']*$" #name regex
mp="^[7-9]{1}[0-9]{9}$" #mobile regex

def connectToDB():#CONNECTION TO DATABASE
    global cur,connection
    connection = pymysql.connect(host = host,user = user,password = password, database = database)
    cur = connection.cursor()


def disconnectDB():#DISCONNECT DATABASE
    cur.close()
    connection.close()

def getStudentData():#FETCHING ALL STUDENT INFORMATION FROM DATABASE
    select_query = "SELECT * FROM student;"
    cur.execute(select_query)
    return cur.fetchall()

def InsertToStudent(name,email,mobile,dob,AdDate,branch):#INSERTING ALL STUDENT INFORMATION FROM HTML FORM TO DATABASE
    try:
        select_query = "INSERT INTO student(name,email,mobileNumber,dob,AdDate,branch) VALUES(%s,%s,%s,%s,%s,%s)"
        cur.execute(select_query,(name,email,mobile,dob,AdDate,branch))
        connection.commit()
        html_data['message'] = "QR code generated successfully!!"
        return render_template("form.html",data = html_data)
        html_data['message'] = ""

    except:
        html_data['message'] = "Email exists add another!"
        return render_template("form.html",data = html_data)
        html_data['message'] = ""

@app.route("/index", methods = ['GET','POST'])
@app.route("/", methods = ['GET','POST'])
def index():
    return render_template("index.html")

@app.route("/studentList",methods = ["GET",'POST'])
def studentRecord():#GETTING DATA FROM DATABASE AND PASSING TO FLASK 
    connectToDB()
    html_data['allstudents'] = getStudentData()
    return render_template("studentList.html",data = html_data)
    disconnectDB()

@app.route("/attendance",methods = ["GET",'POST'])
def showPresenty():#SCANNER OPERATION

    if request.method == 'POST':
        cap = cv2.VideoCapture(0)
        # initialize the cv2 QRCode detector
        detector = cv2.QRCodeDetector()
        while True:
            _, img = cap.read()
            # detect and decode
            s, bbox, _ = detector.detectAndDecode(img)
            # check if there is a QRCode in the image
            if bbox is not None:
                # display the image with lines
                if s:
                    if len(str(s)) > 1:
                        s = int(s[1:-2])
                    else:
                        s = int(s[1])
                    # display the result
                    connectToDB()
                    select_query = "select roll_no from student;"
                    cur.execute(select_query)
                    rollList = cur.fetchall()
                    for i in rollList:
                        if i[0] == s:
                            select_query = "SELECT * FROM student where roll_no = %s"
                            cur.execute(select_query,s)
                            data = cur.fetchone()
                            name = data[1]
                            rollNumber = data[0]
                            branch = data[6]
                            da = datetime.datetime.now()
                            da= da.strftime("%d-%m-%Y")
                            sa = datetime.datetime.now().strftime("%Y_%m_%d")
                            now = datetime.datetime.now()
                            current_time = now.strftime("%I:%M:%p")

                            p = "Present"
                            connectToDB()
                            try:
                                select_query ="INSERT INTO attendance(roll_no,name,entryDate,entryTime,presenty,branch) VALUES(%s,%s,%s,%s,%s,%s)"
                                values=(rollNumber,name,sa,current_time,p,branch)
                                cur.execute(select_query,values)
                                connection.commit()
                                disconnectDB()
                                html_data['atten'] = "Student attendance marked successfully!!"
                                return render_template("attendance.html",data = html_data)

                            except Exception as e:
                                print(e)
                                 
                # else:
                    #     html_data['message'] = "Invalid QRcode"
                    #     return render_template("attendance.html", data = html_data)
                    break
            cv2.imshow("img", img)    
            cv2.waitKey(1)
        cap.release()
        cv2.destroyAllWindows()
    return render_template("attendance.html")
@app.route("/closeCamera",methods = ["GET",'POST'])
def closeCamera():
    cap.release()
    cv2.destroyAllWindows()
    return render_template("attendance.html")
     #close camera


def presentData():
    connectToDB()
    select_query = "SELECT * FROM attendance;"
    cur.execute(select_query)
    return cur.fetchall()
    disconnectDB()

def getSingleStudent(dateRecord):
    connectToDB()
    select_query = "SELECT * FROM attendance where entryDate = '{}';".format(dateRecord)
    cur.execute(select_query)
    datedata = cur.fetchall()
    connection.commit()
    disconnectDB()
    return datedata



@app.route('/presentStudents',methods=["GET","POST"])
def present_students():
    if request.method == "POST":
        data = request.form
        datep = data['txtDate']
        html_data['dateWiseRecord'] = getSingleStudent(datep)
        return render_template("presentStudents.html",data = html_data)
    else:
        html_data['dateWiseRecord'] = presentData()
        return render_template("presentStudents.html",data = html_data)
    

    
#@app.route('/datewisedata',methods = ['GET','POST'])
# def date_wise_recode():
#     if request.method == "GET":

#         dateRecord = request.args.get('rn',type=str)
#         html_data['dateWiseData'] = getSingleStudent(dateRecord)
#     return render_template("presentStudents.html",data = html_data)




@app.route("/form",methods = ["GET",'POST'])
def register():    
    connectToDB()
    if request.method == "POST":
        data = request.form
    
        name = data['txtName']
        if not re.match(np, name):
            html_data["error_name"] = "Invalid Name"
            return render_template("form.html",data = html_data)

        email = data['txtEmail']
        if not re.match(ep, email):
            html_data["error_email"] = "Invalid email address"
            return render_template("form.html",data = html_data)
                            
        
        mobile = data['txtMobile']
        if not re.match(mp, mobile):
            html_data["error_mobile"] = "Enter valid Mobile number"
            return render_template("form.html",data = html_data)


        dob = data['txtDOB']
        branch = data['branch']
        AdDate = datetime.datetime.now().strftime("%d-%m-%Y")

        InsertToStudent(name,email,mobile,dob,AdDate,branch)
        select_query = "select roll_no from student where mobileNumber = %s"
        cur.execute(select_query,mobile)
        qrNumber = cur.fetchone()

        qr=qrcode.QRCode(version=1, box_size=5, border=5)
        qr.add_data(qrNumber)
        qr.make(fit=True)
        img=qr.make_image(fill="black", back_color="skyblue")
        try:
            img.save(r"qrcode\%s.png"%(name+str(qrNumber[0])))
            print("Image of qr generated")
        except:
            print("datttaaaaa is invaaaaliiidddd already exisssttsss")


    html_data['allstudents'] = getStudentData()
    
    disconnectDB()
    return render_template("form.html",data = html_data)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()