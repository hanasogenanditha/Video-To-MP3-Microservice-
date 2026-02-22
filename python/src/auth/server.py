import jwt
import datetime
import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# MySQL config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", 3306))

JWT_SECRET = os.environ.get("JWT_SECRET")


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    cur = mysql.connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM users WHERE email=%s", (auth.username,)
    )

    if res <= 0:
        return "invalid credentials", 401

    user_row = cur.fetchone()
    email = user_row[0]
    password = user_row[1]

    if auth.password != password:
        return "invalid credentials", 401

    token = createJWT(auth.username, JWT_SECRET, True)
    return token, 200


@server.route("/validate", methods=["POST"])
def validate():
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return "missing credentials", 401

    token = auth_header.split(" ")[1]

    try:
        decoded = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"]
        )
    except Exception as e:
        print("JWT decode error:", e)
        return "not authorized", 403

    return jsonify(decoded), 200


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
