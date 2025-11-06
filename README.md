# 🧩 StaffSync — Full-Stack Employee Management System

A **full-stack employee management web application** built with **Flask** and **MySQL**, designed to simplify HR operations and employee data management.
StaffSync enables organizations to efficiently **create, read, update, delete, and export** employee records within a clean, responsive interface.

![Project Screenshot](https://i.ibb.co/00JgBZD/Screenshot-2025-11-05-231624.png)


---

## 🚀 Key Features

✅ **Full CRUD Operations** — Seamlessly add, view, edit, and delete employee records.
✅ **Smart Search & Filtering** — Instantly search employees by name, email, department, or city.
✅ **Column Sorting & Pagination** — Efficiently manage large datasets with sorting and pagination controls.
✅ **CSV Export** — Export employee data based on current filters to a `.csv` file.
✅ **Form Validation** — Server-side validation ensures clean, accurate, and secure data.
✅ **Responsive Design** — Built with **Bootstrap 4**, ensuring compatibility across all devices.
✅ **Connection Pooling** — Uses `mysql.connector.pooling` for optimized database access.
✅ **Environment-Based Configuration** — Securely manages credentials via `.env` file.

---

## 🛠️ Tech Stack

| Category        | Technology                                         |
| --------------- | -------------------------------------------------- |
| **Backend**     | Flask (Python)                                     |
| **Database**    | MySQL                                              |
| **Frontend**    | HTML5, CSS3, Bootstrap 4                           |
| **Environment** | `.env` using `python-dotenv`                       |
| **Libraries**   | `Flask`, `mysql-connector-python`, `python-dotenv` |

---

## ⚙️ Setup & Installation

### 1️⃣ Prerequisites

* Python **3.8+**
* MySQL Server
* (Optional) Git for repository cloning

---

### 2️⃣ Clone the Repository

```bash
git clone https://github.com/Ehtijad-Ali/StaffSync.git
cd StaffSync
```

---

### 3️⃣ Create and Activate a Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4️⃣ Install Dependencies

Create a file named `requirements.txt` containing:

```txt
Flask
mysql-connector-python
python-dotenv
```

Then install:

```bash
pip install -r requirements.txt
```

---

### 5️⃣ Database Setup

1. Start your MySQL server.
2. Run the `schema.sql` script to create the database and tables:

```bash
mysql -u root -p < schema.sql
```

This will create a database named **employees** and an `employees` table with all required fields.

---

### 6️⃣ Environment Configuration

Create a `.env` file in the project’s root directory:

```ini
# Flask Configuration
SECRET_KEY="replace-with-your-own-secret-key"

# MySQL Configuration
DB_HOST="localhost"
DB_USER="root"
DB_PASS="your_mysql_password"
DB_NAME="employees"
```

---

### 7️⃣ Run the Application

```bash
python app.py
```

Then open your browser and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 💻 Application Usage

| Feature                 | Description                                        |
| ----------------------- | -------------------------------------------------- |
| 🏠 **Dashboard**        | View and manage a paginated list of all employees. |
| ➕ **Add Employee**      | Use the form to create a new employee record.      |
| 👁️ **View Details**    | See complete employee details on a dedicated page. |
| ✏️ **Edit Employee**    | Update existing employee information.              |
| 🗑️ **Delete Employee** | Remove an employee record (with confirmation).     |
| 📤 **Export CSV**       | Export filtered employee data as a `.csv` file.    |

---

## 📂 Project Structure

```
StaffSync/
│
├── app.py               # Flask main application file
├── schema.sql           # MySQL database schema
├── .env.example         # Example environment configuration
├── requirements.txt     # Python dependencies
│
├── templates/           # HTML templates (Jinja2)
│   ├── base.html
│   ├── list_employees.html
│   ├── employee_form.html
│   └── view_employee.html
│
└── static/              # Static files (CSS, JS, images)
```

---

## 🧑‍💻 Future Enhancements

* Add **user authentication** (Admin & HR roles)
* Integrate **data visualization dashboards** (salary trends, department insights)
* Enable **bulk import/export** features
* Introduce **REST API endpoints** for integration

