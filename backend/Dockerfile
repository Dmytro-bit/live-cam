FROM python:3.13-slim

RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*


RUN curl -Ls https://astral.sh/uv/install.sh | sh


ENV PATH="/root/.local/bin:/root/.cargo/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

EXPOSE 8000

CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:8000", "-w" , "3", "--threads", "8", "run:app"]
