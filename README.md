# Manhwa

Browser extension for translating raw manhwas to English.

## Setup

Install:

- uv (0.11.2)
- Docker Desktop (4.66.1)

Steps:

1. Clone this repo

    ```bash
    gh repo clone midgramr/manhwa
    ```

2. `cd` into the repo directory
3. Pull the base image from Docker Hub:

    ```bash
    docker pull astral/uv:python3.12-trixie
    ```

4. Run Docker with a bind mount:

    ```bash
    docker run -it --rm -v .:/app -v /app/.venv bash
    ```
