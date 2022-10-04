FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY ./ /

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
#CMD /etc/init.d/nullmailer start ; /usr/sbin/php5-fpm
CMD alembic upgrade head ; uvicorn app.main:app --host 0.0.0.0 --port 8000
# archive config CMD ["ddtrace-run", "gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4", "app.src.main:app", "--bind", "0.0.0.0:80"]
# DD_DOGSTATSD_URL=udp://172.17.0.2:8125 DD_AGENT_HOST=172.17.0.2 DD_SERVICE="cronhooks" DD_ENV="prod" DD_LOGS_INJECTION=true ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# -e DD_DOGSTATSD_URL=udp://172.17.0.2:8125 -e DD_AGENT_HOST=172.17.0.2 -e DD_SERVICE="cronhooks" -e DD_ENV="prod" DD_LOGS_INJECTION=true

# ddtrace-run uvicorn app.main:app --host 0.0.0.0 --port 8000

