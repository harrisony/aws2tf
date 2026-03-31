"""
Abstract base class (interface) for AWS resource handlers.

Each Terraform resource type should be represented by a concrete subclass
that implements both the discovery phase (calling AWS APIs to find resources
and write terraform import blocks) and the transformation phase (rewriting
individual HCL attribute lines to use Terraform references instead of
hardcoded IDs/ARNs).

This replaces the split between:
  - code/get_aws_resources/aws_<service>.py  (discovery)
  - code/fixtf_aws_resources/fixtf_<service>.py  (transformation)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ClientT = TypeVar("ClientT")


class AWSResourceHandler(ABC):
    @property
    @abstractmethod
    def terraform_type(self) -> str:
        """
        The Terraform resource type string.
        E.g. 'aws_lambda_function', 'aws_s3_bucket'.
        """
        ...

    @abstractmethod
    def discover(self, resource_id: str | None) -> bool:
        """
        Discover resource(s) and write terraform import blocks.

        - resource_id is None  → discover all resources of this type in the
          current region/account and call common.write_import() for each one.
        - resource_id is given → discover that specific resource only.

        Returns True if at least one resource was found and written.

        Replaces: get_aws_<service>.get_<terraform_type>()
        """
        ...

    @abstractmethod
    def transform(
        self,
        line: str,
        attr_name: str,
        attr_value: str,
        flag1: bool,
        flag2: str,
    ) -> tuple[int, str, bool, str]:
        """
        Transform a single HCL attribute line from a terraform show output.

        Called once per line of the .out file during the fixtf phase.

        Args:
            line:       The raw line as it appears in the .out file.
            attr_name:  The Terraform attribute name (LHS of '=').
            attr_value: The Terraform attribute value (RHS of '=', stripped of quotes).
            flag1:      General-purpose boolean flag; usage varies by resource type.
            flag2:      General-purpose string flag; usage varies by resource type.

        Returns:
            (skip, modified_line, flag1, flag2)
            skip=1 omits the line from output; skip=0 writes modified_line.

        Replaces: fixtf_<service>.<terraform_type>()
        """
        ...

    def prescan(self, lines: list[str]) -> None:
        """
        Optional: inspect the full .out file before line-by-line transformation.

        Override this to set resource-type-specific context flags that the
        transform() method will later read.  The default implementation is a
        no-op — most resources do not need a prescan pass.

        Replaces: the cascade of `if ttft == "..."` prescan blocks in fixtf.py.
        """
        pass


class DefaultResourceHandler(AWSResourceHandler):
    """
    Generic handler for resources that need no custom discovery or transform logic.

    - discover() delegates to common.getresource() using the aws_dict metadata.
    - transform() is a pass-through: includes every line unchanged.

    Used for 86% of resources that have default behavior.
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
        self._tf_type = tf_type
        self._metadata = (clfn, descfn, topkey, key, filterid)

    @property
    def terraform_type(self) -> str:
        return self._tf_type

    def discover(self, resource_id: str | None) -> bool:
        """Delegate to the existing generic getresource() in common.py."""
        import common

        result = common.getresource(
            self._tf_type,
            resource_id,
            *self._metadata,
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


class BotoHandler(AWSResourceHandler, Generic[ClientT]):
    """
    Base handler for custom AWS resource handlers that need typed boto3 client access.

    Provides:
    - self.client property → fully typed ClientT boto3 client
    - self.client_in(**kwargs) → same, with optional overrides

    Custom handlers inherit like:
        class LambdaHandler(BotoHandler[LambdaClient]):
            def discover(self, resource_id):
                functions = self.client.list_functions()
                ...

    discover() and transform() have pass-through defaults; override as needed.
    """

    def __init__(self, tf_type: str, client_factory: type[ClientT]) -> None:
        self._tf_type = tf_type
        self._client_factory = client_factory
        self._client: ClientT | None = None

    @property
    def terraform_type(self) -> str:
        return self._tf_type

    @property
    def client(self) -> ClientT:
        """Get the typed boto3 client for this resource type."""
        if self._client is None:
            import common

            self._client = common.boto3.client(self._client_factory.__name__.lower())
        return self._client

    def client_in(self, **kwargs) -> ClientT:
        """Get the typed boto3 client with optional overrides."""
        import common

        return common.boto3.client(self._client_factory.__name__.lower(), **kwargs)

    def discover(self, resource_id: str | None) -> bool:
        """Default no-op discovery; override in subclasses."""
        return False

    def transform(
        self,
        line: str,
        attr_name: str,
        attr_value: str,
        flag1: bool,
        flag2: str,
    ) -> tuple[int, str, bool, str]:
        """Pass every attribute through unchanged; override in subclasses."""
        return 0, line, flag1, flag2
