FROM python:3.12-slim

WORKDIR /job

COPY requirements.txt /job/requirements.txt
RUN pip install --no-cache-dir -r /job/requirements.txt
COPY job.py /job/job.py

CMD [ "python", "job.py" ]