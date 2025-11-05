import sys
import time
import logging
import uvicorn
from crawler import run_index_crawler, main_crawler 
from get_countries import run  
from app import app  

def main_prop():
    print("Bắt đầu crawler...")
    main_crawler()

    print("Đang lấy dữ liệu quốc gia...")
    run() 

    print("Khởi chạy ứng dụng FastAPI...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main_prop()
