"""
Lambda resource handlers — discovery and HCL transformation.

Replaces:
  code/get_aws_resources/aws_lambda.py
  code/fixtf_aws_resources/fixtf_lambda.py
"""

from __future__ import annotations

import os
import logging

import boto3
import requests
from botocore.config import Config
from botocore.exceptions import ClientError

import common
import context
from fixtf_aws_resources.base_handler import BaseResourceHandler
from resource_handler import AWSResourceHandler
from resource_registry import DefaultResourceHandler, register

log = logging.getLogger("aws2tf")

_RETRY_CONFIG = Config(retries={"max_attempts": 10, "mode": "standard"})


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _get_lambda_code(fn: str) -> None:
    """Download the Lambda deployment package zip if it's stored in S3."""
    try:
        client = boto3.client("lambda")
        resp = client.get_function(FunctionName=fn)
        if resp["Code"]["RepositoryType"] == "S3":
            r = requests.get(resp["Code"]["Location"])
            with open(f"aws_lambda_function__{fn}.zip", "wb") as f:
                f.write(r.content)
    except Exception as e:
        common.handle_error(e, "_get_lambda_code", "lambda", "get_function", fn, fn)


def _get_layer_code(arn: str) -> None:
    """Download a Lambda layer version zip."""
    if not arn.startswith("arn:"):
        return
    try:
        tarn = BaseResourceHandler.sanitize_resource_name(arn)
        client = boto3.client("lambda")
        resp = client.get_layer_version_by_arn(Arn=arn)
        r = requests.get(resp["Content"]["Location"])
        with open(f"aws_lambda_layer_version__{tarn}.zip", "wb") as f:
            f.write(r.content)
    except Exception as e:
        common.handle_error(e, "_get_layer_code", "lambda", "get_layer_version_by_arn", arn, arn)


# ---------------------------------------------------------------------------
# aws_lambda_function
# ---------------------------------------------------------------------------

class LambdaFunctionHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_function",
            clfn="lambda", descfn="list_functions",
            topkey="Functions", key="FunctionName", filterid="FunctionName",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            if resource_id is None:
                for fn in context.lambdalist.keys():
                    common.write_import(self.terraform_type, fn, None)
                    _get_lambda_code(fn)
                    common.add_known_dependancy("aws_lambda_alias", fn)
                    common.add_known_dependancy("aws_lambda_permission", fn)
                    common.add_known_dependancy("aws_lambda_function_event_invoke_config", fn)
                    common.add_known_dependancy("aws_lambda_event_source_mapping", fn)
                    context.rproc[f"{self.terraform_type}.{fn}"] = True
            else:
                if resource_id.startswith("arn:"):
                    resource_id = resource_id.split(":")[-1]
                try:
                    if context.lambdalist[resource_id]:
                        common.write_import(self.terraform_type, resource_id, None)
                        _get_lambda_code(resource_id)
                        common.add_known_dependancy("aws_lambda_alias", resource_id)
                        common.add_known_dependancy("aws_lambda_permission", resource_id)
                        common.add_known_dependancy("aws_lambda_function_event_invoke_config", resource_id)
                        common.add_known_dependancy("aws_lambda_event_source_mapping", resource_id)
                        context.rproc[f"{self.terraform_type}.{resource_id}"] = True
                except KeyError:
                    common.log_warning(
                        "WARNING: function not in lambda list %s — may reference a function that no longer exists",
                        resource_id,
                    )
                    context.rproc[f"{self.terraform_type}.{resource_id}"] = True
        except Exception as e:
            common.handle_error(e, "LambdaFunctionHandler.discover", "lambda", "list_functions", "Functions", resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0

        if attr_name == "role":
            role_name = attr_value.split("/")[-1]
            safe_name = role_name.replace(".", "_")
            line = f"{attr_name} = aws_iam_role.{safe_name}.arn\n"
            common.add_dependancy("aws_iam_role", role_name)

        elif attr_name == "log_group":
            safe_name = attr_value.replace("/", "_")
            line = f"{attr_name} = aws_cloudwatch_log_group.{safe_name}.name\n"
            common.add_dependancy("aws_cloudwatch_log_group", attr_value)

        elif attr_name == "filename":
            if os.path.isfile(f"{flag2}.zip"):
                line = f'{attr_name} = "{flag2}.zip"\n lifecycle {{\n   ignore_changes = [filename,publish,source_code_hash]\n}}\n'
            elif attr_value == "null":
                skip = 1

        elif attr_name == "image_uri" and attr_value == "null":
            skip = 1

        elif attr_name == "source_code_hash":
            if os.path.isfile(f"{flag2}.zip"):
                line = f'{attr_name} = filebase64sha256("{flag2}.zip")\n'
            elif attr_value == "null":
                skip = 1

        elif attr_name == "s3_bucket" and attr_value == "null":
            skip = 1

        elif attr_name == "layers" and attr_value not in ("[]", "null"):
            if "arn:" not in attr_value:
                common.log_warning("WARNING: layers is not an array %s", attr_value)
                return skip, line, flag1, flag2
            cc = attr_value.count(",")
            inner = attr_value.lstrip("[").rstrip("]")
            builds = ""
            for i in range(cc + 1):
                subn = inner.split(",")[i].strip().strip('"')
                if context.acc in subn:
                    tarn = BaseResourceHandler.sanitize_resource_name(subn)
                    common.add_dependancy("aws_lambda_layer_version", subn)
                    builds += f"aws_lambda_layer_version.{tarn}.arn,"
                else:
                    builds += f'"{subn}", '
            line = f"{attr_name} = [{builds.rstrip(',')}]\n"

        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_lambda_layer
# ---------------------------------------------------------------------------

class LambdaLayerHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_layer",
            clfn="lambda", descfn="list_layers",
            topkey="Layers", key="LayerArn", filterid="LayerArn",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client("lambda")
            if resource_id is None:
                paginator = client.get_paginator("list_layers")
                for page in paginator.paginate():
                    for layer in page["Layers"]:
                        common.write_import(self.terraform_type, layer["LayerArn"], None)
            else:
                if "arn:" in resource_id:
                    resource_id = resource_id.split(":")[6]
                resp = client.list_layer_versions(LayerName=resource_id)
                for j in resp["LayerVersions"]:
                    common.write_import(self.terraform_type, j["LayerVersionArn"], None)
        except Exception as e:
            common.handle_error(e, "LambdaLayerHandler.discover", "lambda", "list_layers", "Layers", resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_lambda_layer_version
# ---------------------------------------------------------------------------

class LambdaLayerVersionHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_layer_version",
            clfn="lambda", descfn="list_layer_versions",
            topkey="LayerVersions", key="LayerVersionArn", filterid="LayerName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            common.log_warning("WARNING: Must pass LayerName/ARN as parameter for aws_lambda_layer_version")
            return True
        try:
            client = boto3.client("lambda")
            if resource_id.startswith("arn:"):
                # Strip the version number from the end to get the layer ARN
                layer_arn = ":".join(resource_id.split(":")[:-1])
                try:
                    resp = client.list_layer_versions(LayerName=layer_arn)
                except ClientError:
                    log.info("Lambda layer %s does not exist — skipping", layer_arn)
                    context.rproc[f"{self.terraform_type}.{resource_id}"] = True
                    return True
                if not resp["LayerVersions"]:
                    context.rproc[f"{self.terraform_type}.{resource_id}"] = True
                    return True
                for j in resp["LayerVersions"]:
                    _get_layer_code(j["LayerVersionArn"])
                    common.write_import(self.terraform_type, j["LayerVersionArn"], None)
                    context.rproc[f"{self.terraform_type}.{j['LayerVersionArn']}"] = True
        except Exception as e:
            common.handle_error(e, "LambdaLayerVersionHandler.discover", "lambda", "list_layer_versions", "LayerVersions", resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "filename":
            if os.path.isfile(f"{flag2}.zip"):
                line = f'{attr_name} = "{flag2}.zip"\n lifecycle {{\n   ignore_changes = [filename,source_code_hash]\n}}\n'
            elif attr_value == "null":
                skip = 1
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_lambda_alias
# ---------------------------------------------------------------------------

class LambdaAliasHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_alias",
            clfn="lambda", descfn="list_aliases",
            topkey="Aliases", key="Name", filterid="FunctionName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            fn = resource_id
            if resource_id.startswith("arn:"):
                parts = resource_id.split(":")
                if len(parts) >= 7:
                    fn = parts[6]
            response = common.call_boto3(self.terraform_type, self._clfn, self._descfn, self._topkey, self._key, fn)
            for j in response:
                common.write_import(self.terraform_type, f"{fn}/{j['Name']}", None)
        except Exception as e:
            common.handle_error(e, "LambdaAliasHandler.discover", "lambda", "list_aliases", "Aliases", resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_lambda_permission
# ---------------------------------------------------------------------------

class LambdaPermissionHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_permission",
            clfn="lambda", descfn="get_policy",
            topkey="Policy", key="Sid", filterid="FunctionName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client("lambda")
            getfn = getattr(client, self._descfn)
            try:
                resp = getfn(FunctionName=resource_id)
                policy = resp[self._topkey]
            except client.exceptions.ResourceNotFoundException:
                return True
            if not policy:
                return True
            sid = policy.split('Sid":')[-1].split(",")[0].strip('"')
            common.write_import(self.terraform_type, f"{resource_id}/{sid}", None)
        except Exception as e:
            common.handle_error(e, "LambdaPermissionHandler.discover", "lambda", "get_policy", "Policy", resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "function_name" and attr_value != "null":
            line = f"{attr_name} = aws_lambda_function.{attr_value}.function_name\n"
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_lambda_function_event_invoke_config
# ---------------------------------------------------------------------------

class LambdaFunctionEventInvokeConfigHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_function_event_invoke_config",
            clfn="lambda", descfn="list_function_event_invoke_configs",
            topkey="FunctionEventInvokeConfigs", key="FunctionArn", filterid="FunctionName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client("lambda")
            getfn = getattr(client, self._descfn)
            resp = getfn(FunctionName=resource_id)
            for j in resp[self._topkey]:
                common.write_import(self.terraform_type, j["FunctionArn"], None)
        except Exception as e:
            common.handle_error(e, "LambdaFunctionEventInvokeConfigHandler.discover", "lambda", self._descfn, self._topkey, resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "maximum_event_age_in_seconds" and attr_value == "0":
            skip = 1
        elif attr_name == "function_name" and attr_value != "null":
            if attr_value.startswith("arn:"):
                fname = attr_value.split(":")[-1]
                line = f"{attr_name} = aws_lambda_function.{fname}.arn\n"
            else:
                line = f"{attr_name} = aws_lambda_function.{attr_value}.function_name\n"
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_lambda_event_source_mapping
# ---------------------------------------------------------------------------

class LambdaEventSourceMappingHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_event_source_mapping",
            clfn="lambda", descfn="list_event_source_mappings",
            topkey="EventSourceMappings", key="UUID", filterid="FunctionName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client("lambda")
            getfn = getattr(client, self._descfn)
            resp = getfn(FunctionName=resource_id)
            for j in resp[self._topkey]:
                uid = j["UUID"]
                common.write_import(self.terraform_type, uid, f"l-{uid}")
        except Exception as e:
            common.handle_error(e, "LambdaEventSourceMappingHandler.discover", "lambda", self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_lambda_layer_version_permission
# ---------------------------------------------------------------------------

class LambdaLayerVersionPermissionHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_layer_version_permission",
            clfn="lambda", descfn="get_layer_version_policy",
            topkey="Policy", key="LayerVersionArn", filterid="LayerName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client("lambda")
            getfn = getattr(client, self._descfn)
            try:
                resp = getfn(LayerName=resource_id)
                policy = resp[self._topkey]
            except client.exceptions.ResourceNotFoundException:
                return True
            if not policy:
                return True
            for j in resp.get("LayerVersions", []):
                ver = j["Version"]
                theid = f"{resource_id},{ver}"
                altid = BaseResourceHandler.sanitize_resource_name(theid)
                common.write_import(self.terraform_type, theid, altid)
        except Exception as e:
            common.handle_error(e, "LambdaLayerVersionPermissionHandler.discover", "lambda", self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_lambda_function_recursion_config
# ---------------------------------------------------------------------------

class LambdaFunctionRecursionConfigHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_function_recursion_config",
            clfn="lambda", descfn="get_function_recursion_config",
            topkey="RecursiveLoop", key="FunctionName", filterid="FunctionName",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client("lambda", config=_RETRY_CONFIG)
            if resource_id is None:
                paginator = client.get_paginator("list_functions")
                for page in paginator.paginate():
                    for func in page["Functions"]:
                        fn = func["FunctionName"]
                        try:
                            resp = client.get_function_recursion_config(FunctionName=fn)
                            if resp.get("RecursiveLoop"):
                                common.write_import(self.terraform_type, fn, None)
                        except ClientError as e:
                            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                                continue
                            raise
            else:
                resp = client.get_function_recursion_config(FunctionName=resource_id)
                if resp.get("RecursiveLoop"):
                    common.write_import(self.terraform_type, resource_id, None)
        except Exception as e:
            common.handle_error(e, "LambdaFunctionRecursionConfigHandler.discover", "lambda", "get_function_recursion_config", "RecursiveLoop", resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_lambda_function_url
# ---------------------------------------------------------------------------

class LambdaFunctionUrlHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_lambda_function_url",
            clfn="lambda", descfn="list_function_url_configs",
            topkey="FunctionUrlConfigs", key="FunctionName", filterid="FunctionName",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client("lambda", config=_RETRY_CONFIG)
            if resource_id is None:
                paginator = client.get_paginator("list_functions")
                for page in paginator.paginate():
                    for func in page["Functions"]:
                        fn = func["FunctionName"]
                        try:
                            resp = client.list_function_url_configs(FunctionName=fn)
                            if resp.get(self._topkey):
                                common.write_import(self.terraform_type, fn, None)
                        except Exception:
                            continue
            else:
                fn = resource_id.split(":")[-1] if resource_id.startswith("arn:") else resource_id
                resp = client.list_function_url_configs(FunctionName=fn)
                if resp.get(self._topkey):
                    common.write_import(self.terraform_type, fn, None)
        except Exception as e:
            common.handle_error(e, "LambdaFunctionUrlHandler.discover", "lambda", self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# Register all handlers
# ---------------------------------------------------------------------------

for _handler in [
    LambdaFunctionHandler(),
    LambdaLayerHandler(),
    LambdaLayerVersionHandler(),
    LambdaAliasHandler(),
    LambdaPermissionHandler(),
    LambdaFunctionEventInvokeConfigHandler(),
    LambdaEventSourceMappingHandler(),
    LambdaLayerVersionPermissionHandler(),
    LambdaFunctionRecursionConfigHandler(),
    LambdaFunctionUrlHandler(),
]:
    register(_handler)
