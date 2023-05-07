
FROM python:slim-buster
LABEL maintainer="Sasha Alimov klimdos@gmail.com"
WORKDIR /src
COPY src/ .
RUN pip install -r requirements.txt

ENV TG_API_TOKEN=""
ENV GPT_API_TOKEN=""

ENTRYPOINT ["python", "app.py"]
