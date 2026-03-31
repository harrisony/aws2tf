"""
S3 resource handlers — discovery and HCL transformation.

Replaces:
  code/get_aws_resources/aws_s3.py
  code/fixtf_aws_resources/fixtf_s3.py
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

import common
import context
import fixtf
from fixtf_aws_resources.base_handler import BaseResourceHandler
from resource_handler import AWSResourceHandler
from resource_registry import DefaultResourceHandler, register

log = logging.getLogger("aws2tf")

_RETRY_CONFIG = Config(retries={"max_attempts": 10, "mode": "standard"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_bucket_name(id_or_arn: str | None) -> str | None:
    if id_or_arn is None:
        return None
    if id_or_arn.startswith("arn:"):
        parts = id_or_arn.split(":")
        if len(parts) >= 6:
            return parts[5].split("/")[0]
        return None
    return id_or_arn


def _check_access(bucket_name: str, region: str) -> bool:
    """Return True if bucket is accessible, False otherwise. Updates context.bucketlist."""
    try:
        s3 = boto3.client("s3", region_name=region)
        s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        context.bucketlist[bucket_name] = True
        return True
    except NoCredentialsError:
        context.bucketlist[bucket_name] = False
        return False
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "AccessDenied":
            context.bucketlist[bucket_name] = False
            context.s3list[bucket_name] = False
            context.rproc[f"aws_s3_bucket.{bucket_name}"] = True
            return False
        if code == "ExpiredToken":
            context.bucketlist[bucket_name] = False
            return False
        return False
    except Exception:
        return False


def _get_s3_configs(s3_fields: dict, bucket_name: str) -> None:
    """Fetch and write_import for each S3 sub-resource configuration."""
    for tf_type, api_fn in s3_fields.items():
        try:
            resp = api_fn(Bucket=bucket_name)
            if len(resp) > 1:
                common.write_import(tf_type, bucket_name, f"b-{bucket_name}")
                if tf_type == "aws_s3_bucket_replication_configuration":
                    rules = resp.get("ReplicationConfiguration", {}).get("Rules", [])
                    for rule in rules:
                        dest = rule.get("Destination", {}).get("Bucket", "")
                        if dest:
                            common.add_known_dependancy("aws_s3_bucket", _extract_bucket_name(dest))
        except Exception:
            pass


def _get_all_s3_buckets(filter_bucket: str | None, region: str) -> None:
    s3 = boto3.resource("s3", region_name=region)
    client = boto3.client("s3", region_name=region)

    s3_fields = {
        "aws_s3_bucket_acl": client.get_bucket_acl,
        "aws_s3_bucket_cors_configuration": client.get_bucket_cors,
        "aws_s3_bucket_lifecycle_configuration": client.get_bucket_lifecycle_configuration,
        "aws_s3_bucket_logging": client.get_bucket_logging,
        "aws_s3_bucket_notification": client.get_bucket_notification_configuration,
        "aws_s3_bucket_object_lock_configuration": client.get_object_lock_configuration,
        "aws_s3_bucket_ownership_controls": client.get_bucket_ownership_controls,
        "aws_s3_bucket_policy": client.get_bucket_policy,
        "aws_s3_bucket_replication_configuration": client.get_bucket_replication,
        "aws_s3_bucket_request_payment_configuration": client.get_bucket_request_payment,
        "aws_s3_bucket_server_side_encryption_configuration": client.get_bucket_encryption,
        "aws_s3_bucket_versioning": client.get_bucket_versioning,
        "aws_s3_bucket_website_configuration": client.get_bucket_website,
        "aws_s3_bucket_intelligent_tiering_configuration": client.list_bucket_intelligent_tiering_configurations,
        "aws_s3_bucket_inventory": client.list_bucket_inventory_configurations,
        "aws_s3_bucket_metric": client.list_bucket_metrics_configurations,
        "aws_s3_bucket_analytics_configuration": client.list_bucket_analytics_configurations,
    }

    if filter_bucket in ("", "null", None):
        buckets_to_check = list(context.s3list.keys())
    elif filter_bucket not in context.s3list:
        return
    else:
        buckets_to_check = [filter_bucket]

    if context.debug:
        # Single-threaded path
        for bucket_name in buckets_to_check:
            if not _check_access(bucket_name, region):
                continue
            import_name = f"b-{bucket_name}"
            common.write_import("aws_s3_bucket", bucket_name, import_name)
            common.add_dependancy("aws_s3_access_point", bucket_name)
            context.rproc[f"aws_s3_bucket.{bucket_name}"] = True
            _get_s3_configs(s3_fields, bucket_name)
    else:
        # Parallel access checks
        accessible = []
        with ThreadPoolExecutor(max_workers=context.cores) as ex:
            futures = {ex.submit(_check_access, bn, region): bn for bn in buckets_to_check}
            for fut in as_completed(futures):
                bn = futures[fut]
                if fut.result():
                    accessible.append(bn)

        for bucket_name in accessible:
            import_name = f"b-{bucket_name}"
            common.write_import("aws_s3_bucket", bucket_name, import_name)
            common.add_dependancy("aws_s3_access_point", bucket_name)
            context.rproc[f"aws_s3_bucket.{bucket_name}"] = True

        # Parallel config fetching
        with ThreadPoolExecutor(max_workers=context.cores) as ex:
            futures = [ex.submit(_get_s3_configs, s3_fields, bn) for bn in accessible]
            for fut in as_completed(futures):
                fut.result()


# ---------------------------------------------------------------------------
# aws_s3_bucket (and sub-resource aliases that route here)
# ---------------------------------------------------------------------------

class S3BucketHandler(DefaultResourceHandler):

    def __init__(self, tf_type: str = "aws_s3_bucket") -> None:
        super().__init__(
            tf_type=tf_type,
            clfn="s3", descfn="list_buckets",
            topkey="Buckets", key="Name", filterid="Name",
        )

    def discover(self, resource_id: str | None) -> bool:
        bucket_name = _extract_bucket_name(resource_id)
        context.tracking_message = f"S3 {bucket_name or 'all'}"
        _get_all_s3_buckets(bucket_name, context.region)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        sub_resource_markers = {
            "request_payment_configuration", "accelerate_configuration", "acl",
            "analytics", "cors_configuration", "intelligent_tiering_configuration",
            "inventory", "lifecycle_configuration", "logging", "metric",
            "notification", "object_lock_configuration", "ownership_controls",
            "policy", "replication_configuration", "server_side_encryption_configuration",
            "versioning", "website_configuration",
        }
        if attr_name in sub_resource_markers:
            flag2 = "True"
        else:
            if attr_name == "bucket" and flag2 == "True":
                line = f"{attr_name} = aws_s3_bucket.b-{attr_value}.bucket\n"
                flag2 = ""
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_s3_directory_bucket
# ---------------------------------------------------------------------------

class S3DirectoryBucketHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_s3_directory_bucket",
            clfn="s3", descfn="list_directory_buckets",
            topkey="Buckets", key="Name", filterid="Name",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client(self._clfn, config=_RETRY_CONFIG)
            bucket_name = _extract_bucket_name(resource_id)
            resp = client.list_directory_buckets()
            for bucket in resp.get(self._topkey, []):
                bn = bucket[self._key]
                if bucket_name is None or bn == bucket_name:
                    common.write_import(self.terraform_type, bn, None)
        except Exception as e:
            common.handle_error(e, "S3DirectoryBucketHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# Transform-only S3 sub-resource handlers
# ---------------------------------------------------------------------------

class S3BucketLifecycleConfigurationHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_s3_bucket_lifecycle_configuration",
            clfn="s3", descfn="get_bucket_lifecycle_configuration",
            topkey="Rules", key="ID", filterid="Bucket",
        )

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name in ("date", "days", "expired_object_delete_marker") and attr_value == "null":
            skip = 1
        elif attr_name == "bucket":
            line = line + "\n lifecycle {\n   ignore_changes = [rule]\n}\n"
        return skip, line, flag1, flag2


class S3BucketObjectLockConfigurationHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_s3_bucket_object_lock_configuration",
            clfn="s3", descfn="get_object_lock_configuration",
            topkey="ObjectLockConfiguration", key="ObjectLockEnabled", filterid="Bucket",
        )

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name in ("years", "days") and attr_value == "0":
            skip = 1
        return skip, line, flag1, flag2


class S3BucketPolicyHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_s3_bucket_policy",
            clfn="s3", descfn="get_bucket_policy",
            topkey="Policy", key="Policy", filterid="Bucket",
        )

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "policy":
            line = fixtf.globals_replace(line, attr_name, attr_value)
        return skip, line, flag1, flag2


class S3BucketReplicationConfigurationHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_s3_bucket_replication_configuration",
            clfn="s3", descfn="get_bucket_replication",
            topkey="ReplicationConfiguration", key="Role", filterid="Bucket",
        )

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if "destination" in line:
            context.destbuck = True
        if attr_name == "bucket" and "arn:aws:s3" in attr_value:
            bn = attr_value.split(":")[-1]
            try:
                if context.bucketlist.get(bn):
                    line = f"{attr_name} = aws_s3_bucket.b-{bn}.arn\n"
            except KeyError:
                pass
            context.destbuck = False
        context.destbuck = False
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# Register all handlers
# ---------------------------------------------------------------------------

for _handler in [
    S3BucketHandler("aws_s3_bucket"),
    # Sub-resource aliases that route to the same discovery logic
    S3BucketHandler("aws_s3_bucket_cors_configuration"),
    S3BucketHandler("aws_s3_bucket_server_side_encryption_configuration"),
    S3DirectoryBucketHandler(),
    S3BucketLifecycleConfigurationHandler(),
    S3BucketObjectLockConfigurationHandler(),
    S3BucketPolicyHandler(),
    S3BucketReplicationConfigurationHandler(),
]:
    register(_handler)
