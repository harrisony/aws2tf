"""
Registry of all AWS resource handlers.

At startup, every Terraform resource type known to aws_dict.aws_resources is
automatically registered with a DefaultResourceHandler that delegates to the
existing getresource() and pass-through transform logic.

Custom handler classes (for the ~14% of resources with non-default behaviour)
are registered by importing code/handlers/<service>.py modules which call
register() directly.

Usage:
    from resource_registry import get_handler, register

    handler = get_handler("aws_lambda_function")
    if handler:
        handler.discover(resource_id)
"""

from __future__ import annotations

import logging

from resource_handler import AWSResourceHandler

log = logging.getLogger("aws2tf")

_registry: dict[str, AWSResourceHandler] = {}


def register(handler: AWSResourceHandler) -> None:
    """Register a handler, replacing any existing entry for the same type."""
    _registry[handler.terraform_type] = handler


def get_handler(terraform_type: str) -> AWSResourceHandler | None:
    """Return the handler for a Terraform resource type, or None if not registered."""
    return _registry.get(terraform_type)


def registered_types() -> list[str]:
    """Return all registered Terraform resource type strings."""
    return list(_registry.keys())


# ---------------------------------------------------------------------------
# DefaultResourceHandler
# ---------------------------------------------------------------------------

class DefaultResourceHandler(AWSResourceHandler):
    """
    Generic handler for resources that need no custom discovery or transform logic.

    - discover() delegates to common.getresource() using the aws_dict metadata.
    - transform() is a pass-through: includes every line unchanged.
    """

    def __init__(
        self,
        tf_type: str,
        clfn: str,
        descfn: str,
        topkey: str,
        key: str,
        filterid: str,
    ) -> None:
        self._terraform_type = tf_type
        self._clfn = clfn
        self._descfn = descfn
        self._topkey = topkey
        self._key = key
        self._filterid = filterid

    @property
    def terraform_type(self) -> str:
        return self._terraform_type

    def discover(self, resource_id: str | None) -> bool:
        """Delegate to the existing generic getresource() in common.py."""
        import common  # local import to avoid circular dependency at module load

        result = common.getresource(
            self._terraform_type,
            resource_id,
            self._clfn,
            self._descfn,
            self._topkey,
            self._key,
            self._filterid,
        )
        return bool(result)

    def transform(
        self,
        line: str,
        attr_name: str,
        attr_value: str,
        flag1: bool,
        flag2: str,
    ) -> tuple[int, str, bool, str]:
        """Pass every attribute through unchanged."""
        return 0, line, flag1, flag2


# ---------------------------------------------------------------------------
# Auto-populate registry from aws_dict at import time
# ---------------------------------------------------------------------------

def _populate_from_aws_dict() -> None:
    """
    Register a DefaultResourceHandler for every entry in aws_dict.aws_resources.

    Runs once at import time. Custom handlers registered afterwards via
    register() will silently override these defaults.
    """
    try:
        from fixtf_aws_resources import aws_dict
    except ImportError:
        log.warning("resource_registry: could not import aws_dict — registry not populated")
        return

    for tf_type, meta in aws_dict.aws_resources.items():
        handler = DefaultResourceHandler(
            tf_type=tf_type,
            clfn=meta.get("clfn", ""),
            descfn=meta.get("descfn", ""),
            topkey=meta.get("topkey", ""),
            key=meta.get("key", ""),
            filterid=meta.get("filterid", ""),
        )
        register(handler)

    log.debug("resource_registry: registered %d resource types from aws_dict", len(_registry))


_populate_from_aws_dict()
