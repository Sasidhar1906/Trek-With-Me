from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask import session
from datetime import datetime,date


app = Flask(__name__)
app.secret_key = "trekwithme_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///trekking.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class User(db.Model) :
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(15), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)



class Trek(db.Model) :
    __tablename__="trek"

    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(500), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) # Easy / Moderate / Hard
    duration = db.Column(db.Integer, nullable=False)  # In Days
    available_slots = db.Column(db.Integer, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    desc = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
    assigned_staff_id = db.Column(db.Integer , db.ForeignKey("user.id"))
    bookings = db.relationship("Booking")
    staff = db.relationship("User",foreign_keys=[assigned_staff_id])



class Booking(db.Model) :
    __tablename__="booking"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    user = db.relationship('User')
    trek = db.relationship('Trek')



@app.route("/")
def home():
    return render_template('home.html')



@app.after_request  ##----->>>> for the website cache memory to be flused out
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/logout")
def logout() :
    session.clear()
    return redirect(url_for("login"))


@app.route("/login",methods=['GET','POST'])
def login():
    if(request.method=='POST') :
        email=request.form["email"]
        password=request.form["password"]   
        user=User.query.filter_by(email=email).first()
        if(user) :
            if(user.blacklisted) :
                return render_template('login.html', error="Your account has been blacklisted.")
            if(user.password==password) :                  
                session["user_id"]=user.id
                session["user_role"]=user.role
                if(user.role=='admin') :  
                    return redirect(url_for("admin_dashboard"))
                elif(user.role=='staff') :
                    if not user.approved :
                        return render_template('login.html', error="Your account is waiting for admin approval.")
                    return redirect(url_for("staff_dashboard"))
                else :
                    return redirect(url_for("user_dashboard"))
  
            else :
                return render_template('login.html', error="Incorrect Password.")
        else :
            return render_template('login.html', error="User not found.")
    return render_template('login.html') 



@app.route("/register",methods=['GET','POST'])
def register():
    if(request.method=="POST") :
        name=request.form['FullName']
        email=request.form['email']
        existing=User.query.filter_by(email=email).first()
        if(existing) :
            return render_template("register.html", error="Email Already Exists!")
        password=request.form['password']
        contact=request.form['contact']
        role=request.form['role']
        new_user=User(name=name,email=email,password=password,contact=contact,role=role,approved=(role=='user'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html') 


@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))   
    total_treks=Trek.query.count()
    total_users=User.query.filter_by(role='user', blacklisted=False).count()
    total_staff=User.query.filter_by(role='staff', approved=True, blacklisted=False).count()
    total_bookings=Booking.query.count()    
    return render_template('admin/admin_dashboard.html', total_treks=total_treks, total_users=total_users, total_staff=total_staff, total_bookings=total_bookings)
    


@app.route("/admin/manage_treks")
def manage_treks():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    search=request.args.get("search")
    if(search) :
        treks_all=Trek.query.filter(Trek.trek_name.ilike(f"%{search}%")).all()
    else :
        treks_all=Trek.query.all()
    return render_template('admin/manage_treks.html',treks_all=treks_all)


@app.route("/admin/add_trek", methods=["POST","GET"])
def add_trek():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    staff_all = User.query.filter_by(role='staff', approved=True, blacklisted=False).all()
    if(request.method=="POST") :
        trek_name = request.form['trek_name']
        location = request.form['location']
        difficulty = request.form['difficulty']
        duration = request.form['duration']
        total_slots = request.form['total_slots']
        start_date = datetime.strptime(request.form["start_date"],"%Y-%m-%d").date()
        end_date = datetime.strptime(request.form["end_date"],"%Y-%m-%d").date()
        desc = request.form['desc'] 
        assigned_staff_id = request.form['assigned_staff_id']
        new_trek = Trek(trek_name=trek_name, location=location, difficulty=difficulty, duration=duration, total_slots=total_slots, available_slots=total_slots, status="Open", start_date=start_date, end_date=end_date, desc=desc, assigned_staff_id = assigned_staff_id if assigned_staff_id else None)
        db.session.add(new_trek)
        db.session.commit()
        return redirect(url_for("manage_treks"))
    return render_template('admin/add_trek.html', staff_all=staff_all)



@app.route("/admin/edit_trek/<int:id>", methods=["POST", "GET"])
def edit_trek(id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    trek=Trek.query.filter_by(id=id).first()
    staff_all = User.query.filter_by(role='staff', approved=True, blacklisted=False).all()
    if(request.method=="POST") :
        trek.trek_name=request.form['trek_name']
        trek.location=request.form['location']
        trek.difficulty=request.form['difficulty']
        trek.duration=request.form['duration']
        new_total = int(request.form["total_slots"])
        booked = trek.total_slots - trek.available_slots
        if new_total < booked:
            return "Total slots cannot be less than booked users."
        trek.total_slots = new_total
        trek.available_slots = new_total - booked
        trek.assigned_staff_id = request.form['assigned_staff_id']
        trek.status = request.form['status']
        trek.start_date = datetime.strptime(request.form["start_date"],"%Y-%m-%d").date()
        trek.end_date = datetime.strptime(request.form["end_date"],"%Y-%m-%d").date()
        trek.desc=request.form['desc']
        db.session.commit()
        return redirect(url_for('manage_treks'))
    return render_template('admin/edit_trek.html', trek=trek, staff_all=staff_all)



@app.route("/admin/delete_trek/<int:id>")
def delete_trek(id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    trek = Trek.query.filter_by(id=id).first()
    bookings = Booking.query.filter_by(trek_id=id).first()
    if not trek :
        return redirect(url_for('manage_treks'))
    if bookings:
        return "Cannot delete this trek because users have already booked it."
    db.session.delete(trek)
    db.session.commit()
    return redirect(url_for("manage_treks"))



@app.route("/admin/delete_staff/<int:id>")
def delete_staff(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("manage_staff"))



@app.route("/admin/manage_staff")
def manage_staff():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    search=request.args.get("search")
    if(search) :
        staff_all=User.query.filter(User.name.ilike(f"%{search}%")).all()
    else :
        staff_all=User.query.filter_by(role="staff").all()
    return render_template('admin/manage_staff.html',staff_all=staff_all)



@app.route("/admin/approve_staff/<int:id>")
def approve_staff(id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    user=User.query.filter_by(id=id).first()
    user.approved=True
    db.session.commit()
    return redirect(url_for('manage_staff'))



@app.route("/admin/blacklist_staff/<int:id>")
def blacklist_staff(id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    user=User.query.filter_by(id=id).first()
    user.blacklisted = True
    db.session.commit()
    return redirect(url_for('manage_staff'))



@app.route("/admin/unblacklist_staff/<int:id>")
def unblacklist_staff(id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    user=User.query.filter_by(id=id).first()
    user.blacklisted=False
    db.session.commit()
    return redirect(url_for('manage_staff'))


@app.route("/admin/bookings")
def bookings():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    search = request.args.get("search")
    if search:
        bookings_all = Booking.query.all()
        filtered_bookings = []
        for booking in bookings_all :
            user = User.query.filter_by(id=booking.user_id).first()
            trek = Trek.query.filter_by(id=booking.trek_id).first()
            if (search.lower() in user.name.lower() or
                search.lower() in trek.trek_name.lower()):
                filtered_bookings.append(booking)
        bookings_all=filtered_bookings
    else:
        bookings_all=Booking.query.all()
    return render_template('admin/bookings.html', bookings_all=bookings_all, User=User, Trek=Trek)


@app.route("/admin/manage_users")
def manage_users():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    search = request.args.get("search")
    if search:
        users_all = User.query.filter(User.role == "user",User.name.ilike(f"%{search}%")).all()
    else:
        users_all = User.query.filter_by(role="user").all()
    return render_template("admin/manage_users.html", users_all=users_all)



@app.route("/admin/blacklist_user/<int:id>")
def blacklist_user(id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    user = User.query.filter_by(id=id).first()
    user.blacklisted = True
    db.session.commit()
    return redirect(url_for("manage_users"))


@app.route("/admin/unblacklist_user/<int:id>")
def unblacklist_user(id):
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    user = User.query.filter_by(id=id).first()
    user.blacklisted = False
    db.session.commit()
    return redirect(url_for("manage_users"))




@app.route("/admin/admin_history")
def admin_history():
    if "user_id" not in session or session.get("user_role") != "admin":
        return redirect(url_for("login"))
    search = request.args.get("search")
    query = Trek.query.filter_by(status="Completed")
    if search:
        query = query.filter(Trek.trek_name.ilike(f"%{search}%"))
    treks = query.all()
    history = []
    for trek in treks:
        participants = Booking.query.filter_by(trek_id=trek.id, status="Completed").count()
        history.append({"trek": trek, "participants": participants})
    return render_template("admin/admin_history.html", history=history)



@app.route("/staff/dashboard")
def staff_dashboard():
    if "user_id" not in session or session.get("user_role") != "staff":
        return redirect(url_for("login"))
    user = User.query.filter_by(id=session['user_id']).first()
    assigned_treks = Trek.query.filter_by(assigned_staff_id = session['user_id']).count()
    treks = Trek.query.filter_by(assigned_staff_id = session['user_id']).all()
    total_trekkers = 0
    for trek in treks :
        total_trekkers += Booking.query.filter_by(trek_id=trek.id).count()
    active_treks = Trek.query.filter_by(assigned_staff_id = session['user_id'], status = "Open").count()
    return render_template('staff/staff_dashboard.html', assigned_treks=assigned_treks, total_trekkers=total_trekkers, active_treks=active_treks, user=user)




@app.route("/staff/assigned_treks")
def assigned_treks():
    if "user_id" not in session or session.get("user_role") != "staff":
        return redirect(url_for("login"))
    search = request.args.get("search")
    if search:
        treks = Trek.query.filter(Trek.assigned_staff_id == session["user_id"],Trek.trek_name.ilike(f"%{search}%")).all()
    else:
        treks = Trek.query.filter_by(assigned_staff_id=session["user_id"]).all()
    return render_template("staff/assigned_treks.html",treks=treks)



@app.route("/staff/update_slots/<int:id>", methods=['POST','GET'])
def update_slots(id):
    if "user_id" not in session or session.get("user_role") != "staff":
        return redirect(url_for("login"))
    trek = Trek.query.filter_by(id=id, assigned_staff_id=session["user_id"]).first()
    if not trek:
        return redirect(url_for("assigned_treks"))
    if(request.method=='POST') :
        new_slots = int(request.form["available_slots"])
        if 0 <= new_slots <= trek.total_slots:
            trek.available_slots = new_slots
            db.session.commit()
        return redirect(url_for('assigned_treks'))
    return render_template("/staff/update_slots.html", trek=trek)


@app.route("/staff/close_trek/<int:id>")
def close_trek(id):
    if "user_id" not in session or session.get("user_role") != "staff":
        return redirect(url_for("login"))
    trek = Trek.query.filter_by(id=id, assigned_staff_id=session["user_id"]).first()
    if trek:
        trek.status = "Closed"
        db.session.commit()
    return redirect(url_for("assigned_treks"))



@app.route("/staff/complete_trek/<int:id>")
def complete_trek(id):
    if "user_id" not in session or session.get("user_role") != "staff":
        return redirect(url_for("login"))
    trek = Trek.query.filter_by(id=id, assigned_staff_id=session['user_id']).first()
    if trek:
        trek.status = "Completed"
        bookings = Booking.query.filter_by(trek_id=id).all()
        for booking in bookings:
            booking.status = "Completed"
        db.session.commit()
    return redirect(url_for("assigned_treks"))




@app.route("/staff/participants")
def participants():
    if "user_id" not in session or session.get("user_role") != "staff":
        return redirect(url_for("login"))
    treks = Trek.query.filter_by(assigned_staff_id=session['user_id']).all()
    participants = {}
    for trek in treks:
        participants[trek.id] = Booking.query.filter_by(trek_id=trek.id).all()
    return render_template('staff/participants.html', treks=treks, User=User, Booking=Booking)





@app.route("/user/dashboard")
def user_dashboard():
    if "user_id" not in session or session.get("user_role") != "user":
        return redirect(url_for("login"))
    user = User.query.filter_by(id=session["user_id"]).first()
    total_bookings = Booking.query.filter_by(user_id = session['user_id']).count()
    upcoming_treks = 0
    completed_treks = 0
    bookings = Booking.query.filter_by(user_id = session['user_id']).all()
    for booking in bookings :
        trek = Trek.query.filter_by(id=booking.trek_id).first()
        if trek.status == "Open" or trek.status == "Closed":
            upcoming_treks += 1
        elif (trek.status == 'Completed') :
            completed_treks += 1
    treks = Trek.query.filter(Trek.status != "Completed").limit(3).all()
    return render_template('user/user_dashboard.html', user=user, total_bookings=total_bookings, upcoming_treks=upcoming_treks, completed_treks=completed_treks, treks=treks)


@app.route("/user/book_trek/<int:id>", methods=['POST','GET'])
def book_trek(id) :
    if "user_id" not in session or session.get("user_role") != "user":
        return redirect(url_for("login"))
    trek = Trek.query.filter_by(id=id).first()
    if trek is None :
        return redirect(url_for('browse_treks'))
    if request.method == 'POST' :
        if(trek.available_slots<=0) :
            return redirect(url_for('browse_treks'))
        if trek.status != "Open":
            return redirect(url_for("browse_treks"))
        existing = Booking.query.filter_by(user_id=session["user_id"],trek_id=trek.id).first()
        if existing:
            return redirect(url_for("my_bookings"))
        booking = Booking(user_id = session['user_id'], trek_id = trek.id, booking_date = date.today(), status="Booked")
        db.session.add(booking)
        trek.available_slots -= 1
        db.session.commit()
        return redirect(url_for('my_bookings'))
    return render_template("user/book.html", trek=trek)



@app.route("/user/history")
def history():
    if "user_id" not in session or session.get("user_role") != "user":
        return redirect(url_for("login"))
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    completed_bookings = []
    for booking in bookings :
        trek = Trek.query.filter_by(id=booking.trek_id).first()
        if trek.status == 'Completed' :
            completed_bookings.append(booking) 
    return render_template("user/history.html", completed_bookings=completed_bookings)



@app.route("/user/browse_treks")
def browse_treks():
    if "user_id" not in session or session.get("user_role") != "user":
        return redirect(url_for("login"))
    search = request.args.get("search")
    difficulty = request.args.get("difficulty")
    location = request.args.get("location")
    query = Trek.query.filter(Trek.status == "Open")
    if search:
        query = query.filter(Trek.trek_name.ilike(f"%{search}%"))
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    treks = query.all()
    return render_template("user/browse_treks.html",treks=treks)


@app.route("/user/my_bookings")
def my_bookings():
    if "user_id" not in session or session.get("user_role") != "user":
        return redirect(url_for("login"))
    all_bookings = Booking.query.filter_by(user_id=session["user_id"]).all()
    bookings = []
    for booking in all_bookings:
        trek = Trek.query.get(booking.trek_id)
        if trek.status != "Completed":
            bookings.append(booking)
    return render_template("user/my_bookings.html", bookings=bookings, Trek=Trek)


@app.route("/user/cancel_booking/<int:id>")
def cancel_booking(id):
    booking = Booking.queryfilter_by(id=id).first()
    trek = Trek.query.get(booking.trek_id)
    trek.available_slots += 1
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for("my_bookings"))



@app.route("/user/profile")
def profile():
    if "user_id" not in session or session.get("user_role") != "user":
        return redirect(url_for("login"))
    user = User.query.filter_by(id=session['user_id']).first()
    return render_template("user/profile.html", user=user)


@app.route("/user/edit_profile", methods=['POST','GET'])
def edit_profile() :
    if "user_id" not in session or session.get("user_role") != "user":
        return redirect(url_for("login"))
    user = User.query.filter_by(id=session['user_id']).first()
    if request.method=='POST' :
        user.name = request.form["name"]
        user.contact = request.form["contact"]
        user.password = request.form["password"]
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template("user/edit_profile.html", user=user)




if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email="admin@gmail.com").first()

        if not admin:
            admin = User(
                name="Administrator",
                email="admin@gmail.com",
                password="admin123",
                role="admin",
                contact="9999999999",
                approved=True,
                blacklisted=False
            )

            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)