FROM python:3.7.4
WORKDIR /powerplant-challenge
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]