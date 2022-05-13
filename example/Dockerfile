FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# cf. https://fastapi.tiangolo.com/deployment/docker/
COPY . /app


# Create non root user app
RUN addgroup --system app && adduser --system --group app

# Make sure all files belongs to the app user
RUN chown -R app:app /app && \
    chown -R app:app $HOME

USER app

# EXPOSE 80
# ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]