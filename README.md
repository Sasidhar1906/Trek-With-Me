# 🏔️ Trek With Me – Trekking Management System

A web-based **Trekking Management System** built using Python and Flask that makes exploring and booking trekking trips easier. The platform provides separate dashboards for Admin, Staff, and Users to manage trekking activities, bookings, participants, and trek information efficiently.

---

## ✨ Features

### 👨‍💼 Admin
- Manage and monitor trekking activities.
- Add, update, and delete trekking details.
- Manage registered users and staff.
- Approve staff registrations.
- Monitor and manage trekking bookings.
- View overall platform activities.

### 🧑‍💻 Staff
- View assigned trekking activities.
- Manage trek availability and slots.
- Track registered participants.
- Update trekking status.
- Manage trekking-related information.

### 👤 User
- Register and log in to the platform.
- Explore available trekking destinations.
- Search and browse treks.
- View trek details, locations, and difficulty levels.
- Book available trekking trips.
- Manage existing bookings.
- View booking and trekking history.

### 📅 Booking Management
- Manage trekking reservations.
- Track available and booked slots.
- Prevent bookings when a trek is full or unavailable.
- Maintain booking records.

### 🔐 Authentication & Authorization
- Secure user authentication.
- Role-based access control.
- Separate dashboards for Admin, Staff, and Users.
- Restricted access to role-specific functionalities.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web application framework |
| Flask-SQLAlchemy | Database management |
| SQLite | Database |
| HTML5 | Frontend structure |
| CSS3 | Styling and layout |
| Jinja2 | Dynamic HTML rendering |

---

## 📂 Project Structure

```text
Trek-With-Me/
│
├── app.py                  # Main Flask application
│
├── instance/               # Application database
│
├── static/                 # CSS, images and static files
│
├── templates/              # HTML templates
│   ├── admin/              # Admin dashboard pages
│   ├── staff/              # Staff dashboard pages
│   ├── user/               # User dashboard pages
│   └── ...
│
└── README.md               # Project documentation
```

---

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Sasidhar1906/Trek-With-Me.git
```

### 2️⃣ Navigate to the Project Directory

```bash
cd Trek-With-Me
```

### 3️⃣ Create a Virtual Environment (Optional)

```bash
python -m venv venv
```

Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 4️⃣ Install Dependencies

```bash
pip install flask flask-sqlalchemy
```

### 5️⃣ Run the Application

```bash
python app.py
```

### 6️⃣ Open in Browser

Once the application starts, visit:

```text
http://127.0.0.1:5000/
```

---

## 🔑 Default Admin Credentials

If you are running the application for the first time, the default administrator account is created automatically.

| Field | Credentials |
|---|---|
| Email | admin@gmail.com |
| Password | admin123 |

**Note:** Change the default credentials before deploying the application publicly.

---

## 🎯 Project Objective

The main objective of **Trek With Me** is to simplify trekking management by providing a centralized platform where users can discover and book trekking experiences while administrators and staff can efficiently manage trekking activities and reservations.

---

## 🚀 Future Enhancements

- Online payment integration.
- Interactive maps and route navigation.
- Email notifications for booking confirmations.
- User reviews and ratings for trekking destinations.
- Advanced search and filtering options.

---

## 👨‍💻 Author

**Sasidhar**

- GitHub: [@Sasidhar1906](https://github.com/Sasidhar1906)
- Repository: [Trek With Me](https://github.com/Sasidhar1906/Trek-With-Me)

---

⭐ If you find this project interesting, consider giving it a star!
