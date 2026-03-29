# Manhwa

Browser extension for translating raw manhwas to English.

## Setup

Install:

- uv (0.11.2)
- Docker Desktop (4.66.1)

1. Clone this repo and `cd` into it

    ```bash
    gh repo clone midgramr/manhwa
    cd manhwa
    ```

2. Build the image (I know passing in the API key as a build arg is bad practice, but idrc lol)

    ```bash
    docker build -t app --build-arg ANTHROPIC_API_KEY=<your key> .
    ```

3. To run for development:

    ```bash
    docker run -it -v .:/app -p 8000:8000 app bash
    ```

3. To run for production:

    ```bash
    docker run -it --rm -p 8000:8000 app
