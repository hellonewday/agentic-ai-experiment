## Tài liệu hướng dẫn sử dụng source code

1. Only for Windows: tải VS Build tools về và chạy để update C++ 2014 sử dụng CrewAI

```bash
vs_buildtools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
```

2. Cài đặt thư viện trong `requirements.txt`

```pip install -r requirements.txt```

3. Thêm OpenAI Key vào `.env` 

4. Cài `wkhtmltopdf` để generate ra PDF 
- Windows: Tải file installer, cài đặt và thêm file vào PATH và uncomment dòng 25-26 trong config.py
- Linux: `sudo apt install wkhtmltopdf`

5. Setup `STMP_USER` và `SMTP_PASSWORD` ở `.env` là credentials trong Mailtrap

6. Chạy full giao diện `python3 -m streamlit run app.py`

Xem giao diện ở `localhost:8501`

- Nếu muốn chạy không cần streamlit:
`python3 main.py`

7. Test kết quả ở thư mục `/reports` hoặc xem trên Mailtrap.

### Deployment

1. Setup file `.env`
  
2. Build docker: 
`docker build -t <image_name>:<image_version> . `

3. Chạy docker:
`sudo docker run --env-file .env  -it -d -p 8501:8501 <image_name>:<image_version>`
