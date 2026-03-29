# Manhwa

Browser extension for translating raw manhwas to English.

## Setup

Install:

- uv (0.11.2)
- Docker Desktop (4.66.1)

Steps:

1. Clone this repo and `cd` into it

    ```bash
    gh repo clone midgramr/manhwa
    cd manhwa
    ```

2. Run Docker with a bind mount on the current directory:

    ```bash
    docker run -it -v .:/app -v /app/.venv astral/uv:python3.12-trixie bash
    ```
