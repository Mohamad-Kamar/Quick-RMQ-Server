FROM python:3.9.0-slim-buster

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1


# Install pip requirements
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . .

CMD ["python3","quick_server.py"]