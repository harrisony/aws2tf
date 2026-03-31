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
