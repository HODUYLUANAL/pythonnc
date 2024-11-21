from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import extract, func
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask
from nguongcanhbao import NGUONG_CANH_BAO 


# Cấu hình ứng dụng Flask và cơ sở dữ liệu
app = Flask(__name__)
app.config["SECRET_KEY"] = "hoduyluan"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:211062@localhost:5432/baitap3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Thiết lập thời gian sống của phiên đăng nhập là 1 phút
app.permanent_session_lifetime = timedelta(minutes=10)

# Định nghĩa mô hình người dùng
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    
    
# Định nghĩa mô hình dữ liệu tiêu thụ
class Consumption(db.Model):
    __tablename__ = 'consumptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dien = db.Column(db.Float, nullable=False)
    nuoc = db.Column(db.Float, nullable=False)
    gas = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False, default=0)
    date = db.Column(db.Date, nullable=False)  
    month_year = db.Column(db.String(7), nullable=False) 

    user = db.relationship("User", backref="consumptions")
    
# Đường dẫn cho trang chủ
@app.route('/')
def home():
    if "user" in session:
        return redirect(url_for('hello_user'))
    return render_template('home.html')

# Đường dẫn cho trang đăng kí
@app.route('/register', methods=["POST", "GET"])
def register():
    if "user" in session:
        return redirect(url_for('hello_user'))
    
    if request.method == "POST":
        user_name = request.form["name"]
        user_password = request.form["password"]
        user_email = request.form["email"]
        user_phone = request.form["phone"]

        # Kiểm tra nếu tên người dùng đã tồn tại
        existing_user = User.query.filter_by(name=user_name).first()
        if existing_user:
            flash("Tên người dùng đã tồn tại!", "error")
            return redirect(url_for("register"))

        # Kiểm tra nếu email đã tồn tại
        existing_email = User.query.filter_by(email=user_email).first()
        if existing_email:
            flash("Email đã được sử dụng!", "error")
            return redirect(url_for("register"))

        # Kiểm tra nếu số điện thoại đã tồn tại
        existing_phone = User.query.filter_by(phone=user_phone).first()
        if existing_phone:
            flash("Số điện thoại đã được sử dụng!", "error")
            return redirect(url_for("register"))

        # Băm mật khẩu trước khi lưu vào cơ sở dữ liệu
        hashed_password = generate_password_hash(user_password, method='pbkdf2:sha256')

        # Tạo người dùng mới
        new_user = User(name=user_name, password=hashed_password, email=user_email, phone=user_phone)
        db.session.add(new_user)
        db.session.commit()

        flash("Đăng ký thành công! Bạn có thể đăng nhập.", "info")
        return redirect(url_for("login"))

    return render_template("register.html")


# Đường dẫn cho trang đăng nhập
@app.route('/login', methods=["POST", "GET"])
def login():
    if "user" in session:
        return redirect(url_for('hello_user'))
    
    if request.method == "POST":
        user_name = request.form["name"]
        user_password = request.form["password"]  # Thêm trường mật khẩu vào form đăng nhập

        # Kiểm tra xem người dùng có tồn tại trong cơ sở dữ liệu không
        user = User.query.filter_by(name=user_name).first()
        
        if user and check_password_hash(user.password, user_password):
            session.permanent = True
            session["user"] = user_name
            flash("Bạn đã đăng nhập thành công!", "info")
            return render_template("user.html", user=user_name)
        else:
            flash("Tên đăng nhập hoặc mật khẩu không chính xác!", "error")
            return redirect(url_for("login"))

    return render_template('login.html')

# Đường dẫn hiển thị trang người dùng
@app.route('/user')
def hello_user():
    if "user" in session:
        name = session["user"]
        return render_template("user.html", user=name)
    else:
        flash("Bạn chưa đăng nhập!", "info")
        return redirect(url_for("login"))

# Đường dẫn để đăng xuất
@app.route('/logout')
def log_out():
    if "user" in session:
        session.pop("user", None)
        flash("Bạn đã đăng xuất tài khoản!", "info")
    else:
        flash("Bạn chưa đăng nhập!", "info")
    return redirect(url_for("login"))
# Đường dẫn để nhập liệu 
@app.route('/nhap_lieu', methods=["POST", "GET"])
def nhap_lieu():
    if "user" not in session:
        flash("Bạn cần đăng nhập để nhập dữ liệu tiêu thụ!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            dien = float(request.form["dien"])
            nuoc = float(request.form["nuoc"])
            gas = float(request.form["gas"])
            date_input = request.form["date"]

            if dien < 0 or nuoc < 0 or gas < 0:
                flash("Lỗi: Giá trị điện, nước, và gas không được phép là số âm.", "danger")
                return redirect(url_for('nhap_lieu'))
            
            # Kiểm tra ngưỡng cảnh báo
            if dien > NGUONG_CANH_BAO["dien"]:
                flash("Cảnh báo: Tiêu thụ điện vượt quá ngưỡng cho phép!", "warning")
            if nuoc > NGUONG_CANH_BAO["nuoc"]:
                flash("Cảnh báo: Tiêu thụ nước vượt quá ngưỡng cho phép!", "warning")
            if gas > NGUONG_CANH_BAO["gas"]:
                flash("Cảnh báo: Tiêu thụ khí gas vượt quá ngưỡng cho phép!", "warning")

            # Tính tổng tiền
            total_cost = dien * 2500 + nuoc * 10000 + gas * 30000

            # Chuyển đổi ngày từ chuỗi sang datetime
            date_input = datetime.strptime(date_input, "%Y-%m-%d")
            month_year = date_input.strftime("%Y-%m")

            # Lấy ID người dùng từ session
            user_name = session["user"]
            user = User.query.filter_by(name=user_name).first()

            # Kiểm tra xem người dùng đã có dữ liệu nhập cho ngày này chưa
            existing_entry = Consumption.query.filter_by(user_id=user.id, date=date_input).first()
            if existing_entry:
                flash("Bạn đã nhập thông tin tiêu thụ cho ngày này rồi!", "danger")
                return redirect(url_for("nhap_lieu"))

            # Tạo bản ghi mới cho dữ liệu tiêu thụ
            new_consumption = Consumption(
                user_id=user.id,
                dien=dien,
                nuoc=nuoc,
                gas=gas,
                total_cost=total_cost,  # Lưu tổng tiền vào cơ sở dữ liệu
                date=date_input,
                month_year=month_year
            )
            db.session.add(new_consumption)
            db.session.commit()

            flash(f"Lưu thông tin tiêu thụ thành công!", "success")
            flash(f"Tổng tiền: {total_cost:.0f} VNĐ", "info")
            return redirect(url_for("nhap_lieu"))
        except ValueError:
            flash("Dữ liệu nhập không hợp lệ!", "danger")
        except Exception as e:
            flash("Đã xảy ra lỗi trong quá trình lưu thông tin!", "danger")
            print(e)  # Để kiểm tra lỗi trong quá trình phát triển

    return render_template("nhaplieu.html")

#Đường dẫn để cập nhật form

@app.route('/update_consumption', methods=['GET', 'POST'])
def update_consumption():
    if 'user' not in session:
        flash('Vui lòng đăng nhập trước khi cập nhật thông tin!', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form
            date = request.form['date']
            dien_update = request.form['dien']
            nuoc_update = request.form['nuoc']
            gas_update = request.form['gas']
            
            if float(dien_update) < 0 or float(nuoc_update) < 0 or float(gas_update) < 0:
                flash('Số liệu không được là số âm!', 'danger')
                return redirect(url_for('update_consumption'))
            
            
            # Chuyển đổi ngày sang định dạng phù hợp
            date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Lấy ID người dùng từ session 
            user_name = session["user"] #lấy tên người dùng trong session
            user = User.query.filter_by(name=user_name).first()# truy vấn cái tên ấy trong csdl
            user_id = user.id  # lấy id cuả người dùng ấy 

            # Tìm đối tượng tiêu thụ theo user_id và ngày
            consumption = Consumption.query.filter_by(user_id=user_id, date=date).first()
            
            if consumption:
                consumption.dien = dien_update
                consumption.nuoc = nuoc_update
                consumption.gas = gas_update
                consumption.total_cost = float(dien_update) * 2500 + float(nuoc_update) * 10000 + float(gas_update) * 30000
                db.session.commit()
                flash('Thông tin đã được cập nhật thành công!', 'success')
                return redirect(url_for('update_consumption'))
            else:
                flash('Không tìm thấy thông tin tiêu thụ cho ngày này!', 'danger')
                
        
        except ValueError:
            flash("Dữ liệu nhập không hợp lệ!", "error")
        except Exception as e:
            flash("Đã xảy ra lỗi trong quá trình lưu thông tin!", "error")
            print(e)  # Để kiểm tra lỗi trong quá trình phát triển
    
    return render_template('update_form.html')
#Đường dẫn cho trang tìm kiếm 
@app.route('/search_consumption', methods=['GET', 'POST'])
def search_consumption():
    if 'user' not in session:
        flash('Vui lòng đăng nhập để tìm kiếm thông tin tiêu thụ!', 'warning')
        return redirect(url_for('login'))
    
    search_results = None  # Khởi tạo biến để lưu kết quả tìm kiếm

    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form tìm kiếm
            date = request.form['date']

            # Chuyển đổi ngày sang định dạng phù hợp
            date = datetime.strptime(date, '%Y-%m-%d').date()

            # Lấy ID người dùng từ session
            user_name = session["user"]
            user = User.query.filter_by(name=user_name).first()
            user_id = user.id

            # Truy vấn thông tin tiêu thụ theo user_id và ngày
            search_results = Consumption.query.filter_by(user_id=user_id, date=date).all()
            
            if not search_results:
                flash('Không tìm thấy thông tin tiêu thụ cho ngày này!', 'warning')
            else:
                flash('Tìm kiếm thành công!', 'success')

        except ValueError:
            flash("Ngày nhập không hợp lệ!", "error")
        except Exception as e:
            flash("Đã xảy ra lỗi trong quá trình tìm kiếm!", "error")
            print(e)  # Để kiểm tra lỗi trong quá trình phát triển

    return render_template('search_form.html', results=search_results)


#Đường dẫn cho trang liệt kê theo tháng 
@app.route('/monthly_report', methods=['GET', 'POST'])
def monthly_report():
    if 'user' not in session:
        flash('Vui lòng đăng nhập để xem báo cáo!', 'warning')
        return redirect(url_for('login'))

    consumption_data = []  # Khởi tạo consumption_data là danh sách rỗng mặc định

    if request.method == 'GET':  # Đảm bảo sử dụng GET khi nhận dữ liệu từ form
        month = request.args.get('month')  # Lấy tham số tháng từ URL
        year = request.args.get('year')    # Lấy tham số năm từ URL

        # Kiểm tra nếu các tham số tháng và năm không trống
        if month and year:
            try:
                # Tạo giá trị month_year để truy vấn
                month = request.args.get('month', '').zfill(2)  # Chắc chắn tháng có ít nhất 2 ký tự
                month_year = f"{year}-{month}"
                user_name = session["user"]
                user = User.query.filter_by(name=user_name).first()
                user_id = user.id
                # Truy vấn dữ liệu theo user_id và month_year
                consumption_data = Consumption.query.filter(Consumption.user_id==user_id, Consumption.month_year==month_year).all()
                if not consumption_data:
                    flash('Không tìm thấy thông tin tiêu thụ cho tháng và năm này!', 'warning')
                else:
                    flash('Tìm kiếm thành công!', 'success')

            except Exception as e:
                flash("Đã xảy ra lỗi trong quá trình tìm kiếm!", "error")
                print(e)  # Để kiểm tra lỗi trong quá trình phát triển

    return render_template('monthly_report.html', report_data=consumption_data)

@app.route('/show_price', methods=["POST", "GET"])
def show_price():
    
    gia_dien = 2500  # Giá tiền điện (VNĐ/KWh)
    gia_nuoc = 10000  # Giá tiền nước (VNĐ/m3)
    gia_gas = 30000  # Giá tiền gas (VNĐ/kg)
    # Cập nhật label với kết quả giá
    result_text = f"Giá tiền điện : {gia_dien} VNĐ\n"
    result_text += f"Giá tiền nước : {gia_nuoc} VNĐ\n"
    result_text += f"Giá tiền gas : {gia_gas} VNĐ\n"
    return render_template('show_price.html', gia_dien=gia_dien, gia_nuoc=gia_nuoc, gia_gas=gia_gas)




# Tạo bảng trong cơ sở dữ liệu nếu chưa có
with app.app_context():
    db.create_all()
    print("Đã tạo cơ sở dữ liệu và các bảng")

if __name__ == "__main__":
    app.run(debug=True)
