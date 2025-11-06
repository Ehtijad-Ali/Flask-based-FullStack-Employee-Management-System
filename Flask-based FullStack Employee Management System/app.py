import os
import csv
from io import StringIO
from decimal import Decimal, InvalidOperation
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort, Response
)
import mysql.connector
from mysql.connector import pooling, Error

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

db_config = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASS", ""),
    "database": os.environ.get("DB_NAME", "employees"),
}

# Use a small connection pool for efficiency
cnxpool = pooling.MySQLConnectionPool(pool_name="emppool", pool_size=5, **db_config)

def get_conn():
    return cnxpool.get_connection()

ALLOWED_SORTS = {
    "first_name": "first_name",
    "last_name": "last_name",
    "email": "email",
    "department": "department",
    "salary": "salary",
    "hire_date": "hire_date",
    "created_at": "created_at",
}

def build_filters(args):
    where = []
    params = []
    q = args.get("q", "").strip()
    department = args.get("department", "").strip()
    status = args.get("status", "").strip()

    if q:
        like = f"%{q}%"
        where.append("(first_name LIKE %s OR last_name LIKE %s OR email LIKE %s OR city LIKE %s OR department LIKE %s)")
        params += [like, like, like, like, like]
    if department:
        where.append("department = %s")
        params.append(department)
    if status:
        where.append("status = %s")
        params.append(status)

    where_sql = " WHERE " + " AND ".join(where) if where else ""
    return where_sql, params

@app.route("/")
def index():
    # Query params
    q = request.args.get("q", "").strip()
    department = request.args.get("department", "").strip()
    status = request.args.get("status", "").strip()
    sort_key = request.args.get("sort", "last_name")
    order_dir = request.args.get("dir", "asc")
    page = int(request.args.get("page", 1))
    per_page = min(max(int(request.args.get("per_page", 10)), 5), 50)

    if sort_key not in ALLOWED_SORTS:
        sort_key = "last_name"
    order_dir_sql = "ASC" if order_dir == "asc" else "DESC"

    where_sql, params = build_filters(request.args)

    offset = (page - 1) * per_page
    count_sql = f"SELECT COUNT(*) AS total FROM employees{where_sql}"
    select_sql = f"""
        SELECT id, first_name, last_name, email, department, position, salary, hire_date, status, city
        FROM employees
        {where_sql}
        ORDER BY {ALLOWED_SORTS[sort_key]} {order_dir_sql}
        LIMIT %s OFFSET %s
    """

    total = 0
    rows = []
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(count_sql, params)
        total = cur.fetchone()["total"]
        cur.execute(select_sql, params + [per_page, offset])
        rows = cur.fetchall()

    pages = (total + per_page - 1) // per_page if total else 1

    return render_template(
        "list_employees.html",
        employees=rows,
        total=total,
        pages=pages,
        page=page,
        per_page=per_page,
        q=q,
        department=department,
        status=status,
        sort=sort_key,
        order_dir=order_dir,
    )

@app.route("/employee/<int:emp_id>")
def view_employee(emp_id):
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM employees WHERE id = %s", (emp_id,))
        emp = cur.fetchone()
    if not emp:
        abort(404)
    return render_template("view_employee.html", employee=emp)

@app.route("/add", methods=["GET", "POST"])
def add_employee():
    if request.method == "POST":
        form = request.form
        try:
            data = parse_employee_form(form)
        except ValueError as e:
            flash(str(e), "danger")
            return render_template("employee_form.html", mode="create", employee=form)

        try:
            with get_conn() as conn:
                cur = conn.cursor()
                sql = """
                INSERT INTO employees
                    (first_name, last_name, email, phone, gender, dob, department, position,
                     hire_date, salary, city, address, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql, (
                    data["first_name"], data["last_name"], data["email"], data["phone"],
                    data["gender"], data["dob"], data["department"], data["position"],
                    data["hire_date"], data["salary"], data["city"], data["address"], data["status"]
                ))
                conn.commit()
                flash("Employee added successfully!", "success")
                return redirect(url_for("index"))
        except Error as e:
            if hasattr(e, "errno") and e.errno == 1062:
                flash("Email already exists. Please use a different email.", "danger")
            else:
                flash(f"Database error: {e}", "danger")
            return render_template("employee_form.html", mode="create", employee=form)

    return render_template("employee_form.html", mode="create", employee=None)

@app.route("/edit/<int:emp_id>", methods=["GET", "POST"])
def edit_employee(emp_id):
    if request.method == "POST":
        form = request.form
        try:
            data = parse_employee_form(form)
        except ValueError as e:
            flash(str(e), "danger")
            # Repopulate form with previous values
            return render_template("employee_form.html", mode="edit", employee=dict(form), emp_id=emp_id)

        try:
            with get_conn() as conn:
                cur = conn.cursor()
                sql = """
                UPDATE employees SET
                    first_name=%s, last_name=%s, email=%s, phone=%s, gender=%s, dob=%s,
                    department=%s, position=%s, hire_date=%s, salary=%s, city=%s, address=%s, status=%s
                WHERE id=%s
                """
                cur.execute(sql, (
                    data["first_name"], data["last_name"], data["email"], data["phone"],
                    data["gender"], data["dob"], data["department"], data["position"],
                    data["hire_date"], data["salary"], data["city"], data["address"], data["status"],
                    emp_id
                ))
                if cur.rowcount == 0:
                    abort(404)
                conn.commit()
                flash("Employee updated successfully!", "success")
                return redirect(url_for("view_employee", emp_id=emp_id))
        except Error as e:
            if hasattr(e, "errno") and e.errno == 1062:
                flash("Email already exists. Please use a different email.", "danger")
            else:
                flash(f"Database error: {e}", "danger")
            return render_template("employee_form.html", mode="edit", employee=dict(form), emp_id=emp_id)

    # GET — load employee
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM employees WHERE id = %s", (emp_id,))
        emp = cur.fetchone()
    if not emp:
        abort(404)
    return render_template("employee_form.html", mode="edit", employee=emp, emp_id=emp_id)

@app.route("/delete/<int:emp_id>", methods=["POST"])
def delete_employee(emp_id):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM employees WHERE id = %s", (emp_id,))
        if cur.rowcount == 0:
            abort(404)
        conn.commit()
    flash("Employee deleted.", "success")
    return redirect(url_for("index"))

@app.route("/export")
def export_csv():
    where_sql, params = build_filters(request.args)
    select_sql = f"""
        SELECT id, first_name, last_name, email, phone, gender, dob, department, position,
               hire_date, salary, city, address, status, created_at
        FROM employees
        {where_sql}
        ORDER BY last_name ASC, first_name ASC
    """
    with get_conn() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(select_sql, params)
        rows = cur.fetchall()

    def to_str(val):
        if isinstance(val, Decimal):
            return f"{val:.2f}"
        if isinstance(val, (datetime,)):
            return val.isoformat()
        return "" if val is None else str(val)

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["ID", "First Name", "Last Name", "Email", "Phone", "Gender", "DOB", "Department",
                     "Position", "Hire Date", "Salary", "City", "Address", "Status", "Created At"])
    for r in rows:
        writer.writerow([
            r["id"], r["first_name"], r["last_name"], r["email"], r["phone"], r["gender"],
            r["dob"], r["department"], r["position"], r["hire_date"], to_str(r["salary"]),
            r["city"], r["address"], r["status"], r["created_at"]
        ])
    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=employees_export.csv"}
    )

def parse_employee_form(form):
    """
    Basic server-side validation and normalization.
    Raises ValueError with a friendly message if invalid.
    """
    first_name = form.get("first_name", "").strip()
    last_name = form.get("last_name", "").strip()
    email = form.get("email", "").strip().lower()
    phone = form.get("phone", "").strip()
    gender = form.get("gender") or None
    dob = form.get("dob") or None
    department = form.get("department", "").strip() or None
    position = form.get("position", "").strip() or None
    hire_date = form.get("hire_date") or None
    salary_raw = form.get("salary", "").strip()
    city = form.get("city", "").strip() or None
    address = form.get("address", "").strip() or None
    status = form.get("status", "Active")

    if not first_name or not last_name:
        raise ValueError("First name and last name are required.")
    if not email or "@" not in email:
        raise ValueError("A valid email is required.")
    if not salary_raw:
        raise ValueError("Salary is required.")
    try:
        salary = Decimal(salary_raw)
        if salary < 0:
            raise ValueError("Salary cannot be negative.")
    except (InvalidOperation, ValueError):
        raise ValueError("Salary must be a valid number.")

    # Optional: verify date formats
    for date_val in [dob, hire_date]:
        if date_val:
            try:
                datetime.strptime(date_val, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Dates must be in YYYY-MM-DD format.")

    if status not in ("Active", "Inactive"):
        status = "Active"

    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "gender": gender,
        "dob": dob,
        "department": department,
        "position": position,
        "hire_date": hire_date,
        "salary": salary,
        "city": city,
        "address": address,
        "status": status,
    }

if __name__ == "__main__":
    app.run(debug=True)