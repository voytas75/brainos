from __future__ import annotations

import contextlib
import io
import logging
import os
from types import ModuleType


def import_litellm_quietly() -> ModuleType:
    previous_log = os.environ.get("LITELLM_LOG")
    previous_silent = os.environ.get("LITELLM_SILENT_LOGGING")
    os.environ["LITELLM_LOG"] = "CRITICAL"
    os.environ["LITELLM_SILENT_LOGGING"] = "true"

    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            import litellm  # type: ignore
    finally:
        if previous_log is None:
            os.environ.pop("LITELLM_LOG", None)
        else:
            os.environ["LITELLM_LOG"] = previous_log
        if previous_silent is None:
            os.environ.pop("LITELLM_SILENT_LOGGING", None)
        else:
            os.environ["LITELLM_SILENT_LOGGING"] = previous_silent

    litellm.suppress_debug_info = True
    for name in ("LiteLLM", "LiteLLM Router", "LiteLLM Proxy"):
        logger = logging.getLogger(name)
        logger.disabled = True
        logger.setLevel(logging.CRITICAL)
    return litellm
