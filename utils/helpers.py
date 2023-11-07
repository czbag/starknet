from typing import Union

from loguru import logger

from settings import RETRY_COUNT
from utils.sleeping import sleep


def retry(func):
    async def wrapper(*args, **kwargs):
        retries = 0
        while retries < RETRY_COUNT:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Error | {e}")
                await sleep(10, 60)
                retries += 1

    return wrapper


def remove_line(file_name: str, text_to_remove: str):
    with open(file_name, "r") as file:
        lines = file.readlines()

    with open(file_name, "w") as file:
        for line in lines:
            if text_to_remove not in line:
                file.write(line)


def remove_wallet(private_key: str, recipient: Union[str, None] = None):
    remove_line("accounts.txt", private_key)
    if recipient:
        remove_line("recipients.txt", recipient)
