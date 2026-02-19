import uvicorn
from core.logger import configure_logging


def main():
    configure_logging()
    uvicorn.run("api.PeopleScopeApi:app", host='127.0.0.1', port=8080, reload=False)


if __name__ == '__main__':
    main()
