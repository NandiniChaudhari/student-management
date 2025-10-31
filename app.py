import sqlite3
from flask import Flask, request, jsonify, g
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret-key"  # change in production

jwt = JWTManager(app)

DATABASE = "student_course.db"



def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with open("schema.sql", "r") as f:
            db.executescript(f.read())
        db.commit()
        print("✅ Database initialized!")


# ------------------ Auth ------------------

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "student")

    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role),
        )
        db.commit()
        return jsonify({"msg": "User registered"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"msg": "Username already exists"}), 400


@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("student_course.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user is None:
        return jsonify({"message": "User not found"}), 404

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"message": "Incorrect password"}), 401

    token = create_access_token(identity=str(user["id"]), additional_claims={"role": user["role"]})

    return jsonify({"token": token, "message": "Login successful"}), 200
# ------------------ Courses ------------------

@app.route("/courses", methods=["GET"])
@jwt_required()
def get_courses():
    db = get_db()
    rows = db.execute("SELECT * FROM courses").fetchall()
    return jsonify([dict(row) for row in rows])


# ------------------ Students ------------------

@app.route("/students", methods=["POST"])
@jwt_required()
def add_student():
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"msg": "Admins only"}), 403

    data = request.get_json()
    full_name = data["full_name"]
    email = data["email"]
    phone = data.get("phone")
    course_code = data.get("course_code")

    db = get_db()
    course = db.execute("SELECT course_id FROM courses WHERE course_code = ?", (course_code,)).fetchone()
    if not course:
        return jsonify({"msg": "Course not found"}), 400

    try:
        cur = db.execute(
            "INSERT INTO students (full_name, email, phone, course_id) VALUES (?, ?, ?, ?)",
            (full_name, email, phone, course["course_id"]),
        )
        db.commit()
        return jsonify({"student_id": cur.lastrowid}), 201
    except sqlite3.IntegrityError:
        return jsonify({"msg": "Email already exists"}), 400


@app.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    claims = get_jwt()
    db = get_db()

    if claims["role"] == "admin":
        rows = db.execute(
            """SELECT s.*, c.course_name, c.course_code
               FROM students s LEFT JOIN courses c ON s.course_id = c.course_id"""
        ).fetchall()
        return jsonify([dict(row) for row in rows])

    # If student role, show their record only
    user = db.execute("SELECT * FROM users WHERE user_id = ?", (get_jwt()["sub"],)).fetchone()
    if not user or not user["student_id"]:
        return jsonify({"msg": "No linked student"}), 404
    row = db.execute(
        """SELECT s.*, c.course_name, c.course_code
           FROM students s LEFT JOIN courses c ON s.course_id = c.course_id
           WHERE s.student_id = ?""",
        (user["student_id"],),
    ).fetchone()
    return jsonify(dict(row)) if row else ({"msg": "Not found"}, 404)


@app.route("/students/by-course/<string:course_code>", methods=["GET"])
@jwt_required()
def get_students_by_course(course_code):
    db = get_db()
    course = db.execute("SELECT * FROM courses WHERE course_code = ?", (course_code,)).fetchone()
    if not course:
        return jsonify({"msg": "Course not found"}), 404

    rows = db.execute("SELECT * FROM students WHERE course_id = ?", (course["course_id"],)).fetchall()
    return jsonify({"course": course["course_name"], "students": [dict(r) for r in rows]})


@app.route("/students/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"msg": "Admins only"}), 403

    data = request.get_json()
    db = get_db()

    # Update details
    updates = []
    params = []

    if "full_name" in data:
        updates.append("full_name = ?")
        params.append(data["full_name"])
    if "email" in data:
        updates.append("email = ?")
        params.append(data["email"])
    if "phone" in data:
        updates.append("phone = ?")
        params.append(data["phone"])
    if "course_code" in data:
        course = db.execute("SELECT course_id FROM courses WHERE course_code = ?", (data["course_code"],)).fetchone()
        if not course:
            return jsonify({"msg": "Course not found"}), 400
        updates.append("course_id = ?")
        params.append(course["course_id"])

    if not updates:
        return jsonify({"msg": "No fields to update"}), 400

    params.append(student_id)
    db.execute(f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?", params)
    db.commit()
    return jsonify({"msg": "Updated"})


@app.route("/students/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    claims = get_jwt()
    if claims["role"] != "admin":
        return jsonify({"msg": "Admins only"}), 403

    db = get_db()
    db.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    db.commit()
    return jsonify({"msg": "Deleted"})


if __name__ == "__main__":
    import os
    if not os.path.exists("student_course.db"):
        init_db()
    app.run(debug=True)
