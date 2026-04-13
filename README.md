# Vinavacci - Hệ Thống Quản Lý Tiêm Chủng

<div align="center">
  <img src="static/android-chrome-192x192.png" alt="Vinavacci Logo" width="120" />
</div>

**Vinavacci** là một ứng dụng nền web toàn diện được phát triển bằng Flask (Python), giúp người dùng dễ dàng đặt lịch tiêm chủng, quản lý hồ sơ sức khỏe cá nhân và gia đình, đồng thời cung cấp các chứng nhận tiêm chủng điện tử. Hệ thống phân quyền chặt chẽ với các vai trò: Người dùng (User), Quản trị viên (Admin) và Quản lý Vắc-xin (Vaccine Admin).

---

## 🌟 Tính Năng Nổi Bật

### 👤 Dành cho Người dùng (User)
- **Quản lý tài khoản:** Đăng ký, đăng nhập an toàn với mã hóa mật khẩu.
- **Hồ sơ gia đình:** Tạo và quản lý hồ sơ tiêm chủng cho nhiều thành viên trong gia đình.
- **Đặt lịch thông minh:** Dễ dàng tìm kiếm vắc-xin, trung tâm và chọn lịch tiêm phù hợp.
- **Trợ lý AI (Chatbot):** Tích hợp AI tự động giải đáp các thông tin về sức khỏe và dịch vụ tiêm chủng theo thời gian thực.
- **Chứng nhận điện tử:** Tự động tạo và tải xuống chứng nhận tiêm chủng file PDF có chứa mã QR.
- **Quản lý lịch hẹn:** Xem lịch sử, hủy hoặc dời lịch hẹn nhanh chóng.

### 🛡️ Dành cho Quản trị viên (Admin)
- **Quản lý kho (Inventory):** Kiểm soát số lượng và hạn sử dụng vắc-xin.
- **Quản lý trung tâm:** Thêm, sửa, xóa thông tin các điểm tiêm chủng.
- **Lên lịch tiêm:** Thiết lập lịch làm việc và phân bổ vắc-xin cho các trung tâm.
- **Giám sát lịch hẹn:** Theo dõi tình trạng các ca tiêm chủng trên toàn hệ thống.
- **Thống kê & Báo cáo:** Giao diện Dashboard trực quan theo dõi hoạt động hệ thống.

---

## 🛠️ Công Nghệ Sử Dụng

- **Backend:** Python, Flask (Kiến trúc Blueprint)
- **Database:** MySQL (hỗ trợ bảo mật SSL)
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Login, Werkzeug Security
- **Tạo File PDF & QR:** ReportLab, qrcode
- **Tích hợp AI:** Groq API (LLaMA-3)
- **Frontend:** HTML5, CSS3, JavaScript (Jinja2 Templates)
- **Môi trường & Triển khai:** python-dotenv, Gunicorn

---

## 📂 Cấu Trúc Thư Mục

Hệ thống được thiết kế theo kiến trúc **Blueprint (Phân hệ)** giúp rành mạch logic và dễ dàng mở rộng:

```text
vinavacci/
├── app.py                # Khởi tạo ứng dụng (App Factory)
├── config.py             # Định nghĩa cấu hình hệ thống
├── extensions.py         # Khởi tạo plugins (db, login_manager)
├── models.py             # Khai báo cấu trúc cơ sở dữ liệu (Database Models)
├── requirements.txt      # Chứa các dependencies cần thiết
├── \.env                 # Biến môi trường (Mật khẩu, API keys)
├── routes/               # Bộ điều khiển (Controllers / Blueprints)
│   ├── admin.py          # Xử lý logic của Quản trị viên
│   ├── api.py            # Các endpoints API
│   ├── appointments.py   # Logic đặt lịch tiêm
│   ├── auth.py           # Xác thực (Đăng nhập/Đăng ký)
│   ├── chat.py           # Xử lý chatbot AI Groq
│   └── main.py           # Các trang chủ và Dashboard
├── utils/                # Hàm tiện ích dùng chung
│   ├── decorators.py     # Custom decorators (phân quyền)
│   └── pdf.py            # Tiện ích tạo PDF chứng nhận tiêm chủng
├── static/               # File tĩnh (CSS, JS, Hình ảnh)
└── templates/            # Giao diện HTML (Jinja2)
```

---

## ⚙️ Hướng Dẫn Cài Đặt

### 1. Yêu cầu hệ thống
- Tải và cài đặt **Python 3.9+**
- Cài đặt **MySQL Server** (hoặc sử dụng dịch vụ Cloud MySQL như Aiven.io)

### 2. Thiết lập cơ sở dữ liệu
Đảm bảo bạn đã khởi tạo một database trống trên MySQL. Nếu sử dụng SSL, bạn cần có CA Certificate (`ca.pem`). Encode các file chứng chỉ này sang Base64 nếu muốn thêm trực tiếp vào biến môi trường.

### 3. Clone dự án và cài đặt
Mở terminal/command prompt và chạy các lệnh sau:

```bash
# Clone source code
git clone <repository-url>
cd vinavacci

# Tạo môi trường ảo (Virtual Environment)
python -m venv myenv

# Kích hoạt môi trường ảo
# Windows:
myenv\Scripts\activate
# Linux/Mac:
source myenv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường
Tạo file `.env` tại thư mục gốc của dự án (`vinavacci/.env`) và điền các thông tin sau:

```env
DATABASE_URL=mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>
SECRET_KEY=your_super_secret_key
GROQ_API_KEY=your_groq_api_key
# Nếu dùng MySQL Cloud cần SSL:
CA_PEM=your_base64_encoded_ca_pem
```

---

## 🚀 Khởi Chạy Ứng Dụng

### Môi trường Phát triển (Development)
Sử dụng Flask Development Server để tự do thay đổi mã nguồn:

```bash
python app.py
```
*Hệ thống sẽ chạy tại địa chỉ: `http://127.0.0.1:10000/`*

### Môi trường Thực tế (Production)
Sử dụng **Gunicorn** cho hiệu suất cao (Hỗ trợ trên môi trường Linux):

```bash
gunicorn -c guincorn_config.py app:app
```

---

## 🔒 Bản Quyền & Giấy Phép
Dự án được phân phối dưới giấy phép [MIT License](LICENSE).

---
*© 2026 Vinavacci. Mọi quyền được bảo lưu.*
