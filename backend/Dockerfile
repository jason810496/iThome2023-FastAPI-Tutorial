# pull official base image
FROM python:3.11.1-slim

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/backend

COPY ./requirements.txt /usr/backend/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/backend/

# # 
# FROM python:3.11.1-slim as requirements-stage

# # 
# WORKDIR /tmp

# # 
# RUN pip install poetry

# # 
# COPY ./pyproject.toml ./poetry.lock* /tmp/

# # 
# RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# # 
# FROM python:3.11.1-slim

# # 
# WORKDIR /usr/backend/

# # 
# COPY --from=requirements-stage /tmp/requirements.txt /usr/backend/requirements.txt

# # 
# RUN pip install --no-cache-dir --upgrade -r /usr/backend/requirements.txt

# # 
# COPY . /usr/backend

# 
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
# CMD ["python3" ,"run.py" ]
