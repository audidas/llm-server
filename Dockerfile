FROM python:3.9

WORKDIR /llm-server

COPY ./requirements.txt /llm-server/requirements.txt

ENV TZ=Asia/Seoul

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /llm-server/requirements.txt

COPY ./app /llm-server/app
COPY ./main.py /llm-server
COPY ./.env /llm-server/.env

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000","--workers","3"]
