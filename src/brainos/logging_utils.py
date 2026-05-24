from __future__ import annotations

import contextlib
import io
import logging
import os
from typing import Iterator


@contextlib.contextmanager
def suppress_litellm_noise() -> Iterator[None]:
    previous_log = os.environ.get("LITELLM_LOG")
    os.environ["LITELLM_LOG"] = "CRITICAL"

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    litellm_logger = logging.getLogger("LiteLLM")
    litellm_router_logger = logging.getLogger("LiteLLM Router")
    litellm_proxy_logger = logging.getLogger("LiteLLM Proxy")
    previous_states = [
        (litellm_logger, litellm_logger.disabled, litellm_logger.level),
        (litellm_router_logger, litellm_router_logger.disabled, litellm_router_logger.level),
        (litellm_proxy_logger, litellm_proxy_logger.disabled, litellm_proxy_logger.level),
    ]

    try:
        for logger, _disabled, _level in previous_states:
            logger.disabled = True
            logger.setLevel(logging.CRITICAL)
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            yield
    finally:
        for logger, disabled, level in previous_states:
            logger.disabled = disabled
            logger.setLevel(level)
        if previous_log is None:
            os.environ.pop("LITELLM_LOG", None)
        else:
            os.environ["LITELLM_LOG"] = previous_log
