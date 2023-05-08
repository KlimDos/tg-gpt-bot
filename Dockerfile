
FROM python:slim-buster
LABEL maintainer="Sasha Alimov klimdos@gmail.com"
WORKDIR /app_workdir
COPY src/ src/
COPY readme.md .

RUN pip install -r src/requirements.txt

ENV TG_API_TOKEN=""
ENV GPT_API_TOKEN=""

ENTRYPOINT ["python", "src/app.py"]
