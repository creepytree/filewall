FROM python:3.13-slim

COPY filewall /app/filewall
COPY pyproject.toml /app/pyproject.toml
COPY requirements.txt /app/requirements.txt

# git is needed to install the druidforms framework (a git+ dependency); purge it
# again afterwards so it does not bloat the runtime image.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && pip install /app \
    && apt-get purge -y --auto-remove git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

CMD [ "uvicorn", "filewall.app:app", "--host", "0.0.0.0", "--port", "5000" ]
