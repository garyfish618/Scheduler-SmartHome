FROM python:latest as base
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
ADD ./scheduler ./scheduler

##### DEBUGGER ####
FROM base as debug
RUN pip install ptvsd
WORKDIR /scheduler
CMD python3 -m ptvsd --host 0.0.0.0 --port 5678  --multiprocess main.py 


#### PRODUCTION ####
FROM base as production
WORKDIR /scheduler
ENTRYPOINT ["python3"]
CMD ["main.py"]