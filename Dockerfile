# Sử dụng image Python chính thức
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép các file yêu cầu vào container
COPY requirements.txt .

# Cài đặt các thư viện cần thiết từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép tất cả mã nguồn vào container
COPY . .

# Mở port 8000 để truy cập ứng dụng FastAPI
EXPOSE 8000

# Thay vì chạy app.py, chạy main.py để thực hiện các file theo thứ tự
CMD ["python", "main.py"]
