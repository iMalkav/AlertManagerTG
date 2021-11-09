FROM python:3.8 AS builder
COPY requirements.txt .

RUN pip install Cython

RUN pip install --user -r requirements.txt

FROM python:3.8-slim
WORKDIR /alertmanagertg

COPY --from=builder /root/.local /root/.local
COPY ./src .

ENV PATH=/root/.local:$PATH

CMD ["python", "-u", "./AlertManagerTG.py"]
