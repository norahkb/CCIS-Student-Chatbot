import datetime
from flask import render_template, request, jsonify, redirect, url_for, Flask, current_app, Response, abort
import requests
from flask_login import LoginManager, login_required, logout_user, login_user
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, jsonify, redirect, url_for, Blueprint, send_file, Flask
from sqlalchemy import or_
from CreateVectorsStore import ceate_db
from importCSV import uploadToDB
from models import *
from processor import get_answer
import os
import random
# from routes import *
import json

# Specify the path to your JSON file
json_file_path = 'sample_intents.json'

# Read the JSON file
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///university.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.app_context()
db.init_app(app)
os.makedirs('data', exist_ok=True)
os.makedirs("dp_faiss", exist_ok=True)
ceate_db()
# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

with app.app_context():
    # within this block, current_app points to app.
    # db.drop_all()
    db.create_all()


class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = str(id)
        self.password = self.name + "_pwd"

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)


# create some users with ids 1 to 20
# users = [User(id) for id in range(1, 21)]
users = [User("admin")]


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if password == "admin_pwd":
            id = username
            user = User(id)
            login_user(user)
            if request.args.get("next"):
                return redirect(request.args.get("next"))
            return  render_template('adminpage.html')
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User(userid)


prev_response = []


@app.post("/chatbot_api/")
def normal_chat():
    start_time = datetime.datetime.now()
    msg = request.get_json().get('message')
    for intent in data["intents"]:
        if msg.lower() in intent['patterns']:
            response = random.choice(intent['responses'])
            return jsonify({'response': response, 'tag': "tag"})
    response,ms = get_answer(msg)
    final_res = ms



    return jsonify({'response': final_res, 'tag': "tag"})




@app.route("/")
@login_required
def hello_world():
    return render_template('home.html')

@app.route("/admin/")
@login_required
def home():
    return render_template('adminpage.html')

@app.route("/course/", methods=['POST', 'GET'])
@login_required
def course():
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_number = request.form['course_number']
        course_description = request.form['course_description']
        course_requirements = request.form['course_requirements']
        course_dependent = request.form['course_dependent']
        major = request.form['major']
        expected_term = request.form['expected_term']
        no_of_hours = request.form['no_of_hours']
        course_type = request.form['course_type']
        no_of_available_sections = request.form['no_of_available_sections']

        new_object = Course(course_name=course_name, course_number=course_number, course_description=course_description, course_requirements=course_requirements, course_dependent=course_dependent, major=major, expected_term=expected_term, no_of_hours=no_of_hours, course_type=course_type, no_of_available_sections=no_of_available_sections)
        db.session.add(new_object)
        db.session.commit()
        course = Course.query.all()
        return redirect(url_for('course'))

    course = Course.query.all()
    return render_template('course.html', course=course)


@app.route("/course/delete/<int:id>/")
@login_required
def coursedelete(id):
    course = Course().query.get(id)
    db.session.delete(course)
    db.session.commit()

    course = Course.query.all()
    return redirect(url_for('course'))


@app.route('/courseBulkUpload', methods = ['POST'])
@login_required
def coursesuccess():
    if request.method == 'POST':
        f = request.files['file']
        f.save('fileupload/'+f.filename)
        uploadToDB('fileupload/'+f.filename,'course')
        return render_template("fileUploadAcknowledgement.html", name = f.filename)


@app.route("/instructor/", methods=['POST', 'GET'])
@login_required
def instructor():
    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        position = request.form['position']
        course_number = request.form['course_number']
        section_number = request.form['section_number']
        email = request.form['email']
        office_telephone_number = request.form['office_telephone_number']
        office_floor = request.form['office_floor']
        office_number = request.form['office_number']

        new_object = Instructor(first_name=first_name, middle_name=middle_name, last_name=last_name, position=position, course_number=course_number, section_number=section_number, email=email, office_telephone_number=office_telephone_number, office_floor=office_floor, office_number=office_number)
        db.session.add(new_object)
        db.session.commit()
        instructor = Instructor.query.all()
        return redirect(url_for('instructor'))

    instructor = Instructor.query.all()
    return render_template('instructor.html', instructor=instructor)


@app.route("/instructor/delete/<int:id>/")
@login_required
def instructordelete(id):
    instructor = Instructor().query.get(id)
    db.session.delete(instructor)
    db.session.commit()

    instructor = Instructor.query.all()
    return redirect(url_for('instructor'))


@app.route('/instructorBulkUpload', methods = ['POST'])
@login_required
def instructorsuccess():
    if request.method == 'POST':
        f = request.files['file']
        f.save('fileupload/'+f.filename)
        uploadToDB('fileupload/'+f.filename,'instructor')
        return render_template("fileUploadAcknowledgement.html", name = f.filename)


@app.route("/level/", methods=['POST', 'GET'])
@login_required
def level():
    if request.method == 'POST':
        level_code = request.form['level_code']
        level_number = request.form['level_number']
        level_major = request.form['level_major']
        no_of_optional_courses = request.form['no_of_optional_courses']
        no_of_mandatory_courses = request.form['no_of_mandatory_courses']
        leve_courses_names = request.form['leve_courses_names']
        leve_courses_numbers = request.form['leve_courses_numbers']
        min_term_hours = request.form['min_term_hours']
        max_term_hours = request.form['max_term_hours']

        new_object = Level(level_code=level_code, level_number=level_number, level_major=level_major, no_of_optional_courses=no_of_optional_courses, no_of_mandatory_courses=no_of_mandatory_courses, leve_courses_names=leve_courses_names, leve_courses_numbers=leve_courses_numbers, min_term_hours=min_term_hours, max_term_hours=max_term_hours)
        db.session.add(new_object)
        db.session.commit()
        level = Level.query.all()
        return redirect(url_for('level'))

    level = Level.query.all()
    return render_template('level.html', level=level)


@app.route("/level/delete/<int:id>/")
@login_required
def leveldelete(id):
    level = Level().query.get(id)
    db.session.delete(level)
    db.session.commit()

    level = Level.query.all()
    return redirect(url_for('level'))


@app.route('/levelBulkUpload', methods = ['POST'])
@login_required
def levelsuccess():
    if request.method == 'POST':
        f = request.files['file']
        f.save('fileupload/'+f.filename)
        uploadToDB('fileupload/'+f.filename,'level')
        return render_template("fileUploadAcknowledgement.html", name = f.filename)


@app.route("/majorplan/", methods=['POST', 'GET'])
@login_required
def majorplan():
    if request.method == 'POST':
        name = request.form['name']
        courses_names = request.form['courses_names']
        courses_numbers = request.form['courses_numbers']
        total_courses = request.form['total_courses']
        total_hours = request.form['total_hours']
        name_acronym = request.form['name_acronym']
        total_levels = request.form['total_levels']

        new_object = MajorPlan(name=name, courses_names=courses_names, courses_numbers=courses_numbers, total_courses=total_courses, total_hours=total_hours, name_acronym=name_acronym, total_levels=total_levels)
        db.session.add(new_object)
        db.session.commit()
        majorplan = MajorPlan.query.all()
        return redirect(url_for('majorplan'))

    majorplan = MajorPlan.query.all()
    return render_template('majorplan.html', majorplan=majorplan)


@app.route("/majorplan/delete/<int:id>/")
@login_required
def majorplandelete(id):
    majorplan = MajorPlan().query.get(id)
    db.session.delete(majorplan)
    db.session.commit()

    majorplan = MajorPlan.query.all()
    return redirect(url_for('majorplan'))


@app.route('/majorplanBulkUpload', methods = ['POST'])
@login_required
def majorplansuccess():
    if request.method == 'POST':
        f = request.files['file']
        f.save('fileupload/'+f.filename)
        uploadToDB('fileupload/'+f.filename,'majorplan')
        return render_template("fileUploadAcknowledgement.html", name = f.filename)


@app.route("/section/", methods=['POST', 'GET'])
@login_required
def section():
    if request.method == 'POST':
        course_name = request.form['course_name']
        course_number = request.form['course_number']
        section_number = request.form['section_number']
        major = request.form['major']
        no_of_hours = request.form['no_of_hours']
        reference_number = request.form['reference_number']
        seats = request.form['seats']
        classroom = request.form['classroom']
        daytime_days = request.form['daytime_days']
        daytime_time = request.form['daytime_time']

        new_object = Section(course_name=course_name, course_number=course_number, section_number=section_number, major=major, no_of_hours=no_of_hours, reference_number=reference_number, seats=seats, classroom=classroom, daytime_days=daytime_days, daytime_time=daytime_time)
        db.session.add(new_object)
        db.session.commit()
        section = Section.query.all()
        return redirect(url_for('section'))

    section = Section.query.all()
    return render_template('section.html', section=section)


@app.route("/section/delete/<int:id>/")
@login_required
def sectiondelete(id):
    section = Section().query.get(id)
    db.session.delete(section)
    db.session.commit()

    section = Section.query.all()
    return redirect(url_for('section'))

@login_required
@app.route('/sectionBulkUpload', methods = ['POST'])
def sectionsuccess():
    if request.method == 'POST':
        f = request.files['file']
        f.save('fileupload/'+f.filename)
        uploadToDB('fileupload/'+f.filename,'section')
        return render_template("fileUploadAcknowledgement.html", name = f.filename)


@app.route("/technicalsupport/", methods=['POST', 'GET'])
@login_required
def technicalsupport():
    if request.method == 'POST':
        name = request.form['name']
        telephone_number = request.form['telephone_number']
        email = request.form['email']
        description = request.form['description']

        new_object = TechnicalSupport(name=name, telephone_number=telephone_number, email=email, description=description)
        db.session.add(new_object)
        db.session.commit()
        technicalsupport = TechnicalSupport.query.all()
        return redirect(url_for('technicalsupport'))

    technicalsupport = TechnicalSupport.query.all()
    return render_template('technicalsupport.html', technicalsupport=technicalsupport)


@app.route("/technicalsupport/delete/<int:id>/")
@login_required
def technicalsupportdelete(id):
    technicalsupport = TechnicalSupport().query.get(id)
    db.session.delete(technicalsupport)
    db.session.commit()

    technicalsupport = TechnicalSupport.query.all()
    return redirect(url_for('technicalsupport'))


@app.route('/technicalsupportBulkUpload', methods = ['POST'])
@login_required
def technicalsupportsuccess():
    if request.method == 'POST':
        f = request.files['file']
        f.save('fileupload/'+f.filename)
        uploadToDB('fileupload/'+f.filename,'technicalsupport')
        return render_template("fileUploadAcknowledgement.html", name = f.filename)


@app.route("/stats/", methods=['POST', 'GET'])
@login_required
def stats():
    if request.method == 'POST':
        req = request.form['req']
        res = request.form['res']
        time_start = request.form['time_start']
        time_end = request.form['time_end']
        tag = request.form['tag']

        new_object = Stats(req=req, res=res, time_start=time_start, time_end=time_end, tag=tag)
        db.session.add(new_object)
        db.session.commit()
        stats = Stats.query.all()
        return redirect(url_for('stats'))

    stats = Stats.query.all()
    return render_template('stats.html', stats=stats)


@app.route("/stats/delete/<int:id>/")
@login_required
def statsdelete(id):
    stats = Stats().query.get(id)
    db.session.delete(stats)
    db.session.commit()

    stats = Stats.query.all()
    return redirect(url_for('stats'))


@app.route("/intents/", methods=['POST', 'GET'])
@login_required
def intensts():
    if request.method == 'POST':
        req = request.form['req']
        res = request.form['res']
        time_start = request.form['time_start']
        time_end = request.form['time_end']
        tag = request.form['tag']

        new_object = Stats(req=req, res=res, time_start=time_start, time_end=time_end, tag=tag)
        db.session.add(new_object)
        db.session.commit()

        return redirect(url_for('intents'))


    with open("sample_intents.json", "r") as f:
        content = f.read()
        intents = content
        return render_template('intents.html', intents=content)

    return render_template('intents.html', intentsV=content)


@app.route('/intentUpload', methods = ['POST'])
@login_required
def intentUpload():
    if request.method == 'POST':
        f = request.files['file']
        f.save('sample_intents.json')
        return render_template("fileUploadAcknowledgement.html", name = f.filename)

if __name__ == '__main__':
    app.run()
