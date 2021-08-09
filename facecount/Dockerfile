FROM python:3.7

ADD main.py .

COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python", "./main.py" ]