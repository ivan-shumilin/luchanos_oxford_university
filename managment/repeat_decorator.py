import asyncio
from functools import wraps

from starlette.concurrency import run_in_threadpool


def repeat_every(
    *,
    seconds: float,
    wait_first: bool = False,
    # logger: logging.Logger | None = logging.getLogger("JobWorker"),
    raise_exceptions: bool = False,
    max_repetitions = None,
):
    raise_exceptions = False  # TODO: Use config.debug before release

    def decorator(func):
        is_coroutine = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def wrapped(*args) -> None:
            repetitions = 0

            async def loop() -> None:
                nonlocal repetitions
                if wait_first:
                    await asyncio.sleep(seconds)
                while max_repetitions is None or repetitions < max_repetitions:
                    try:
                        if is_coroutine:
                            await func(*args)  # type: ignore
                        else:
                            await run_in_threadpool(func, *args)
                        repetitions += 1
                    except Exception as exc:
                        # if logger is not None:
                        #     formatted_exception = "".join(format_exception(type(exc), exc, exc.__traceback__))
                        #     logger.error(formatted_exception)
                        if raise_exceptions:
                            raise exc
                    await asyncio.sleep(seconds)

            asyncio.ensure_future(loop())

        return wrapped

    return decorator
