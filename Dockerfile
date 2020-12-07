FROM python:3

WORKDIR /current

COPY . .

RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "depix.py"]
