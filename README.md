## Tài liệu hướng dẫn sử dụng source code trên Windows

1. Tải VS Build tools về và chạy

```bash
vs_buildtools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
```

để update C++ 2014 sử dụng CrewAI

2. Cài đặt thư viện trong `requirements.txt`

3. Tải Ollama hoặc thêm OpenAI Key vào `.env` 

Nếu sử dụng OpenAI key, comment dòng 4 -> dòng 7 ở `agents.py` và xoá `llm=llm` ở các agents

4. Cài `wkhtmltopdf` để generate ra PDF

5. Setup `STMP_USER` và `SMTP_PASSWORD` ở `config.py` là credentials trong Mailtrap

6. Chạy `streamlit run app.py`
