FROM python:3.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install discord.py python-dotenv

COPY . /app/

CMD ["python", "bot.py"]
