import abc
import logging
import httpx


class ResultsObserver(abc.ABC):
    @abc.abstractmethod
    def observe(self, data: bytes) -> None: ...


async def do_reliable_request(url: str, observer: ResultsObserver) -> None:
    """
    Одна из главных проблем распределённых систем - это ненадёжность связи.

    Ваша задача заключается в том, чтобы таким образом исправить этот код, чтобы он
    умел переживать возвраты ошибок и таймауты со стороны сервера, гарантируя
    успешный запрос (в реальной жизни такая гарантия невозможна, но мы чуть упростим себе задачу).

    Все успешно полученные результаты должны регистрироваться с помощью обсёрвера.
    """

    retries = 10
    timeout = 10.0

    async with httpx.AsyncClient() as client:
        for _ in range(retries):
            try:
                response = await client.get(url, timeout=timeout)
                response.raise_for_status()
                data = response.read()

                observer.observe(data)
                return
            except httpx.HTTPStatusError as error:
                logging.error(f"Произошла ошибка HTTP: {error}")
            except httpx.ReadTimeout as error:
                logging.error(f"Произошёл timeout: {error}")
