from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션 사용을 위한 비밀 키

# 업로드할 이미지 파일 저장 경로
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 허용할 파일 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 사용자 데이터와 상품 데이터를 저장할 리스트 (임시 저장)
users = {}
products = []

# 파일 확장자 체크 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 로그인 페이지
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # 사용자 인증
        if username in users and users[username] == password:
            session["username"] = username  # 로그인한 사용자 세션 저장
            return redirect(url_for("welcome"))  # 성공 시 환영 페이지로 이동
        else:
            error = "아이디 또는 비밀번호가 잘못되었습니다."
            return render_template("login.html", error=error)

    return render_template("login.html")


# 회원가입 페이지
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # 사용자 이름 중복 확인
        if username in users:
            error = "이미 존재하는 아이디입니다."
            return render_template("signup.html", error=error)
        else:
            users[username] = password  # 사용자 저장
            return redirect(url_for("login"))  # 회원가입 후 로그인 페이지로 이동

    return render_template("signup.html")


# 환영 페이지
@app.route("/welcome")
def welcome():
    if "username" not in session:
        return redirect(url_for("login"))  # 로그인하지 않은 경우 로그인 페이지로 리다이렉트

    username = session["username"]
    return render_template("welcome.html", username=username)


# 상품 등록 페이지
@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if "username" not in session:
        return redirect(url_for("login"))  # 로그인하지 않은 경우 로그인 페이지로 리다이렉트

    if request.method == "POST":
        title = request.form["title"]
        price = request.form["price"]
        description = request.form["description"]

        # 이미지 파일 처리
        if "image" not in request.files:
            error = "이미지를 업로드 해주세요."
            return render_template("add_product.html", error=error)

        image = request.files["image"]
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # 이미지 저장

            # 상품 정보를 저장
            products.append({
                "title": title,
                "price": price,
                "description": description,
                "seller": session["username"],
                "image": f"uploads/{filename}"  # 이미지 경로 저장
            })

            return redirect(url_for("product_list"))  # 상품 목록으로 리다이렉트

    return render_template("add_product.html")


# 상품 목록 페이지
@app.route("/products")
def product_list():
    if "username" not in session:
        return redirect(url_for("login"))  # 로그인하지 않은 경우 로그인 페이지로 리다이렉트
    
    return render_template("product_list.html", products=products)


# 로그아웃 처리
@app.route("/logout")
def logout():
    session.pop("username", None)  # 세션에서 사용자 정보 제거
    return redirect(url_for("login"))

if __name__ == "__main__":
    # 업로드 폴더가 없으면 생성
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    app.run(debug=True)
