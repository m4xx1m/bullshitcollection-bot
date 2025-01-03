import logging
import structlog


def setup_logging(level: str):
    match level.lower():
        case "debug":
            lvl = "DEBUG"
            as_json = False
        case "info":
            lvl = "INFO"
            as_json = False
        case "prod":
            lvl = "DEBUG"
            as_json = True
        case _:
            raise ValueError(f"unknown log level: {level}")

    common_processors = (
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f"),
        structlog.processors.dict_tracebacks,
    )

    logging_processors = (structlog.stdlib.ProcessorFormatter.remove_processors_meta,)
    logging_console_processors = (
        *logging_processors,
        structlog.processors.JSONRenderer() if as_json else _render,
    )

    console_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=common_processors,
        processors=logging_console_processors
    )

    handler = logging.StreamHandler()
    handler.set_name("default")
    handler.setFormatter(console_formatter)

    logging.basicConfig(
        handlers=[handler],
        level="WARN",
    )
    logging.getLogger("app").setLevel(lvl)


def _render(logger: structlog.typing.WrappedLogger, name: str, event_dict: structlog.typing.EventDict) -> str:
    timestamp = event_dict.pop("timestamp")
    level = event_dict.pop("level")
    event = event_dict.pop("event")
    logger_name = event_dict.pop("logger")
    exception = event_dict.pop("exception", None)
    kwargs = " ".join([f"{_k}={_v}" for _k, _v in event_dict.items()])

    return f"{timestamp} | {level.ljust(8)} | {logger_name} - {event} {kwargs}" + (f"\n{exception}" if exception else "")
