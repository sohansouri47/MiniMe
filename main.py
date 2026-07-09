import uvicorn

from src.common.config.config import AppConfig


def main() -> None:
    uvicorn.run(
        "src.app:create_app",
        host=AppConfig.HOST,
        port=AppConfig.PORT,
        factory=True,
        reload=AppConfig.RELOAD,
    )


if __name__ == "__main__":
    main()

