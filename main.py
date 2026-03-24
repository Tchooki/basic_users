import logging

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> None:
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
