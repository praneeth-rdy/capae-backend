import sys

from loguru import logger
from starlette.requests import Request
from starlette.responses import Response

from app.server.config import config


def logging_api_requests(request: Request, response: Response):
    logs = f'{request.client.host}:{request.client.port} {request.method} {request.url} {response.status_code}'
    logs += '\n\n' + '*********Request Headers Start***********\n'
    logs += '\n'.join(f'{name} : {value}' for name, value in request.headers.items())
    logs += '\n' + '*********Request Headers End***********\n'
    logs += '\n\n' + '*********Response Headers Start***********\n'
    logs += '\n'.join(f'{name} : {value}' for name, value in response.headers.items())
    logs += '\n' + '*********Response Headers End***********\n'
    logger.debug(logs)


SEPARATOR = '\n--------------------------------------------------------------------------\n'
FORMAT = '{level} | {time:ddd MMMM YYYY, HH:mm:ss:SSS} | {name}:{function}:{line}' + SEPARATOR + '{message}' + SEPARATOR
logger.remove()
logger = logger.opt(colors=True)
logger.add(sys.stdout, colorize=True, level=config.LOG_LEVEL, format=FORMAT, enqueue=True, backtrace=True)
logger.enable('logger')
logger.add(f'logs/{config.LOG_FILE_NAME}.log', colorize=True, rotation='10 MB', level=config.LOG_LEVEL, format=FORMAT, enqueue=True, backtrace=True)
logger.add(sys.stderr, colorize=True, level='ERROR', format=FORMAT, enqueue=True, backtrace=True)
