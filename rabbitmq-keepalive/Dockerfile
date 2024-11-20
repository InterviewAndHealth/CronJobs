FROM python:3.12-slim

WORKDIR /job

COPY requirements.txt /job/requirements.txt
RUN pip install --no-cache-dir -r /job/requirements.txt
COPY job.py /job/job.py

RUN touch run_job.sh
RUN echo "#!/bin/bash" >> run_job.sh
RUN echo "QUEUES=\$(env | grep '_QUEUE=' | awk -F'=' '{print \$2}' | tr '\n' ',' | sed 's/,\$//')" >> run_job.sh
RUN echo "export QUEUES" >> run_job.sh
RUN echo "echo \"Starting job with queues: \$QUEUES\"" >> run_job.sh
RUN echo "python job.py" >> run_job.sh

RUN chmod +x run_job.sh
ENTRYPOINT [ "./run_job.sh" ]