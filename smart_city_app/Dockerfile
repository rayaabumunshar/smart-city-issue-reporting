FROM python:3.11-slim

WORKDIR /app
COPY smart_city_app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY smart_city_app ./smart_city_app
COPY data ./data

EXPOSE 8501
CMD ["streamlit", "run", "smart_city_app/app.py", "--server.address=0.0.0.0", "--server.port=8501"]

