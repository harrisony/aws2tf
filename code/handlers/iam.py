"""
IAM resource handlers — discovery and HCL transformation.

Replaces:
  code/get_aws_resources/aws_iam.py
  code/fixtf_aws_resources/fixtf_iam.py
"""

from __future__ import annotations

import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
from botocore.config import Config

import common
import context
import fixtf
from resource_handler import AWSResourceHandler
from resource_registry import DefaultResourceHandler, register

log = logging.getLogger("aws2tf")

_RETRY_CONFIG = Config(retries={"max_attempts": 10, "mode": "standard"})


# ---------------------------------------------------------------------------
# aws_iam_role
# ---------------------------------------------------------------------------

class IamRoleHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_role",
            clfn="iam", descfn="list_roles",
            topkey="Roles", key="RoleName", filterid="RoleName",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client(self._clfn, region_name="us-east-1")
            if resource_id is None:
                for rn in context.rolelist.keys():
                    if "/aws-service-role/" in rn:
                        continue
                    safe_name = rn.replace(".", "_")
                    common.write_import(self.terraform_type, rn, safe_name)
                    common.add_known_dependancy("aws_iam_role_policy_attachment", rn)
                    common.add_known_dependancy("aws_iam_role_policy", rn)
                    context.rproc[f"{self.terraform_type}.{rn}"] = True
            else:
                if "/aws-service-role/" in resource_id:
                    return True
                safe_name = resource_id.replace(".", "_")
                common.write_import(self.terraform_type, resource_id, safe_name)
                common.add_known_dependancy("aws_iam_role_policy_attachment", resource_id)
                common.add_known_dependancy("aws_iam_role_policy", resource_id)
                context.rproc[f"{self.terraform_type}.{resource_id}"] = True
        except Exception as e:
            common.handle_error(e, "IamRoleHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "name" and len(attr_value) > 0:
            flag1 = True
            flag2 = attr_value
        elif attr_name == "name_prefix" and flag1:
            skip = 1
        elif attr_name == "policy":
            line = fixtf.globals_replace(line, attr_name, attr_value)
        elif attr_name == "assume_role_policy":
            line = fixtf.globals_replace(line, attr_name, attr_value)
        elif attr_name == "permissions_boundary" and attr_value != "null":
            if "arn:aws:iam::aws:policy" not in attr_value:
                pn = attr_value.split("/")[-1]
                common.add_dependancy("aws_iam_policy", attr_value)
                line = f"{attr_name} = aws_iam_policy.{pn}.arn\n"
        elif attr_name == "managed_policy_arns":
            if attr_value == "[]":
                skip = 1
            elif context.acc in attr_value:
                inner = attr_value.lstrip("[").rstrip("]")
                arns = [a.strip().strip('"') for a in inner.split(",")]
                parts = []
                for arn in arns:
                    if context.acc in arn:
                        replaced = arn.replace(context.acc, f'format("%s",data.aws_caller_identity.current.account_id)')
                        parts.append(f'"{replaced}"')
                    else:
                        parts.append(f'"{arn}"')
                line = f'{attr_name} = [{",".join(parts)}]\n'
                if flag2 not in context.roles:
                    context.roles.append(flag2)
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_iam_role_policy
# ---------------------------------------------------------------------------

class IamRolePolicyHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_role_policy",
            clfn="iam", descfn="list_role_policies",
            topkey="PolicyNames", key="PolicyName", filterid="RoleName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client(self._clfn)
            pkey = f"{self.terraform_type}.{resource_id}"
            if len(context.role_policies_list) > 0:
                policies = context.role_policies_list.get(resource_id, [])
            else:
                resp = client.list_role_policies(RoleName=resource_id)
                policies = resp[self._topkey]
            for pn in policies:
                theid = f"{resource_id}:{pn}"
                common.write_import(self.terraform_type, theid, None)
            context.rproc[pkey] = True
        except Exception as e:
            common.handle_error(e, "IamRolePolicyHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "name" and len(attr_value) > 0:
            flag1 = True
        elif attr_name == "name_prefix" and flag1:
            skip = 1
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_iam_role_policy_attachment
# ---------------------------------------------------------------------------

class IamRolePolicyAttachmentHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_role_policy_attachment",
            clfn="iam", descfn="list_attached_role_policies",
            topkey="AttachedPolicies", key="PolicyArn", filterid="RoleName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client(self._clfn)
            pkey = f"{self.terraform_type}.{resource_id}"
            if len(context.attached_role_policies_list) > 0:
                policies = context.attached_role_policies_list.get(resource_id, [])
            else:
                paginator = client.get_paginator(self._descfn)
                policies = []
                for page in paginator.paginate(RoleName=resource_id):
                    policies.extend(page[self._topkey])
            for pol in policies:
                parn = pol["PolicyArn"]
                theid = f"{resource_id}/{parn}"
                common.write_import(self.terraform_type, theid, None)
                if "arn:aws:iam::aws:policy" not in parn:
                    common.add_dependancy("aws_iam_policy", parn)
            context.rproc[pkey] = True
        except Exception as e:
            common.handle_error(e, "IamRolePolicyAttachmentHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "policy_arn":
            line = fixtf.globals_replace(line, attr_name, attr_value)
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_iam_policy
# ---------------------------------------------------------------------------

class IamPolicyHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_policy",
            clfn="iam", descfn="list_policies",
            topkey="Policies", key="PolicyName", filterid="PolicyArn",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client(self._clfn)
            if resource_id is None:
                for parn in context.policylist.keys():
                    ln = parn.rfind("/")
                    pn = parn[ln + 1:]
                    common.write_import(self.terraform_type, parn, pn)
                    context.rproc[f"{self.terraform_type}.{parn}"] = True
            else:
                if "arn:" in resource_id:
                    resp = client.get_policy(PolicyArn=resource_id)
                    parn = resp["Policy"]["Arn"]
                else:
                    parn = resource_id
                ln = parn.rfind("/")
                pn = parn[ln + 1:]
                common.write_import(self.terraform_type, parn, pn)
                context.rproc[f"{self.terraform_type}.{parn}"] = True
        except Exception as e:
            common.handle_error(e, "IamPolicyHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "name" and len(attr_value) > 0:
            flag1 = True
        elif attr_name == "name_prefix" and flag1:
            skip = 1
        elif attr_name == "policy":
            line = fixtf.globals_replace(line, attr_name, attr_value)
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_iam_instance_profile
# ---------------------------------------------------------------------------

class IamInstanceProfileHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_instance_profile",
            clfn="iam", descfn="get_instance_profile",
            topkey="InstanceProfile", key="InstanceProfileName", filterid="InstanceProfileName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client(self._clfn)
            resp = client.get_instance_profile(InstanceProfileName=resource_id)
            theid = resp[self._topkey][self._key]
            common.write_import(self.terraform_type, theid, None)
        except Exception as e:
            common.handle_error(e, "IamInstanceProfileHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_iam_user_group_membership
# ---------------------------------------------------------------------------

class IamUserGroupMembershipHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_user_group_membership",
            clfn="iam", descfn="get_group",
            topkey="Users", key="UserName", filterid="GroupName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client(self._clfn)
            resp = client.get_group(GroupName=resource_id)
            for user in resp[self._topkey]:
                uid = user[self._key]
                theid = f"{uid}/{resource_id}"
                common.write_import(self.terraform_type, theid, None)
            context.rproc[f"{self.terraform_type}.{resource_id}"] = True
        except Exception as e:
            common.handle_error(e, "IamUserGroupMembershipHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "user" and attr_value != "null":
            line = f"{attr_name} = aws_iam_user.{attr_value}.id\n"
            common.add_dependancy("aws_iam_user", attr_value)
        elif attr_name == "groups":
            skip, line, flag1, flag2 = fixtf.deref_array(line, attr_name, attr_value, "aws_iam_group", "", skip)
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_iam_user_policy
# ---------------------------------------------------------------------------

class IamUserPolicyHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_user_policy",
            clfn="iam", descfn="list_user_policies",
            topkey="PolicyNames", key="PolicyName", filterid="UserName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client(self._clfn)
            resp = client.list_user_policies(UserName=resource_id)
            for pn in resp[self._topkey]:
                common.write_import(self.terraform_type, f"{resource_id}:{pn}", None)
            context.rproc[f"{self.terraform_type}.{resource_id}"] = True
        except Exception as e:
            common.handle_error(e, "IamUserPolicyHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_iam_group_policy
# ---------------------------------------------------------------------------

class IamGroupPolicyHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_group_policy",
            clfn="iam", descfn="list_group_policies",
            topkey="PolicyNames", key="PolicyName", filterid="GroupName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client(self._clfn)
            resp = client.list_group_policies(GroupName=resource_id)
            for pn in resp[self._topkey]:
                common.write_import(self.terraform_type, f"{resource_id}:{pn}", None)
            context.rproc[f"{self.terraform_type}.{resource_id}"] = True
        except Exception as e:
            common.handle_error(e, "IamGroupPolicyHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "group" and attr_value != "null":
            line = f"{attr_name} = aws_iam_group.{attr_value}.id\n"
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# aws_iam_service_linked_role
# ---------------------------------------------------------------------------

class IamServiceLinkedRoleHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_service_linked_role",
            clfn="iam", descfn="list_roles",
            topkey="Roles", key="RoleName", filterid="RoleName",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client(self._clfn)
            if resource_id is None:
                paginator = client.get_paginator(self._descfn)
                for page in paginator.paginate():
                    for role in page[self._topkey]:
                        if ":role/aws-service-role" in role["Arn"]:
                            common.write_import(self.terraform_type, role["Arn"], None)
            else:
                resp = client.get_role(RoleName=resource_id)
                role = resp["Role"]
                if ":role/aws-service-role" in role["Arn"]:
                    common.write_import(self.terraform_type, role["Arn"], None)
        except Exception as e:
            common.handle_error(e, "IamServiceLinkedRoleHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_iam_group_policy_attachment
# ---------------------------------------------------------------------------

class IamGroupPolicyAttachmentHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_group_policy_attachment",
            clfn="iam", descfn="list_attached_group_policies",
            topkey="AttachedPolicies", key="PolicyArn", filterid="GroupName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client(self._clfn)
            paginator = client.get_paginator(self._descfn)
            for page in paginator.paginate(GroupName=resource_id):
                for pol in page[self._topkey]:
                    parn = pol[self._key]
                    theid = f"{resource_id}/{parn}"
                    common.write_import(self.terraform_type, theid, None)
                    if "arn:aws:iam::aws:policy" not in parn:
                        common.add_dependancy("aws_iam_policy", parn)
            context.rproc[f"{self.terraform_type}.{resource_id}"] = True
        except Exception as e:
            common.handle_error(e, "IamGroupPolicyAttachmentHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_iam_group
# ---------------------------------------------------------------------------

class IamGroupHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_group",
            clfn="iam", descfn="list_groups",
            topkey="Groups", key="GroupName", filterid="GroupName",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client(self._clfn, config=_RETRY_CONFIG)
            if resource_id is None:
                paginator = client.get_paginator(self._descfn)
                for page in paginator.paginate():
                    for group in page[self._topkey]:
                        gn = group[self._key]
                        common.write_import(self.terraform_type, gn, None)
                        common.add_known_dependancy("aws_iam_user_group_membership", gn)
                        common.add_known_dependancy("aws_iam_group_policy", gn)
                        common.add_known_dependancy("aws_iam_group_policy_attachment", gn)
            else:
                resp = client.get_group(GroupName=resource_id)
                gn = resp["Group"][self._key]
                common.write_import(self.terraform_type, gn, None)
                common.add_known_dependancy("aws_iam_user_group_membership", gn)
                common.add_known_dependancy("aws_iam_group_policy", gn)
                common.add_known_dependancy("aws_iam_group_policy_attachment", gn)
        except Exception as e:
            common.handle_error(e, "IamGroupHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_iam_user
# ---------------------------------------------------------------------------

class IamUserHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_user",
            clfn="iam", descfn="list_users",
            topkey="Users", key="UserName", filterid="UserName",
        )

    def discover(self, resource_id: str | None) -> bool:
        try:
            client = boto3.client(self._clfn, config=_RETRY_CONFIG)
            if resource_id is None:
                paginator = client.get_paginator(self._descfn)
                for page in paginator.paginate():
                    for user in page[self._topkey]:
                        un = user[self._key]
                        common.write_import(self.terraform_type, un, None)
                        common.add_known_dependancy("aws_iam_user_policy_attachment", un)
                        common.add_known_dependancy("aws_iam_user_policy", un)
                        groups = client.list_groups_for_user(UserName=un)
                        for g in groups["Groups"]:
                            common.add_known_dependancy("aws_iam_user_group_membership", g["GroupName"])
            else:
                resp = client.get_user(UserName=resource_id)
                un = resp["User"][self._key]
                common.write_import(self.terraform_type, un, None)
                common.add_known_dependancy("aws_iam_user_policy_attachment", un)
                common.add_known_dependancy("aws_iam_user_policy", un)
                groups = client.list_groups_for_user(UserName=un)
                for g in groups["Groups"]:
                    common.add_known_dependancy("aws_iam_user_group_membership", g["GroupName"])
        except Exception as e:
            common.handle_error(e, "IamUserHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# aws_iam_user_policy_attachment
# ---------------------------------------------------------------------------

class IamUserPolicyAttachmentHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_user_policy_attachment",
            clfn="iam", descfn="list_attached_user_policies",
            topkey="AttachedPolicies", key="PolicyArn", filterid="UserName",
        )

    def discover(self, resource_id: str | None) -> bool:
        if resource_id is None:
            return True
        try:
            client = boto3.client(self._clfn)
            paginator = client.get_paginator(self._descfn)
            for page in paginator.paginate(UserName=resource_id):
                for pol in page[self._topkey]:
                    parn = pol[self._key]
                    theid = f"{resource_id}/{parn}"
                    common.write_import(self.terraform_type, theid, None)
                    if "arn:aws:iam::aws:policy" not in parn:
                        common.add_dependancy("aws_iam_policy", parn)
            context.rproc[f"{self.terraform_type}.{resource_id}"] = True
        except Exception as e:
            common.handle_error(e, "IamUserPolicyAttachmentHandler.discover", self._clfn, self._descfn, self._topkey, resource_id)
        return True


# ---------------------------------------------------------------------------
# Transform-only handlers (no custom discover needed)
# ---------------------------------------------------------------------------

class IamAccessKeyHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_access_key",
            clfn="iam", descfn="list_access_keys",
            topkey="AccessKeyMetadata", key="AccessKeyId", filterid="UserName",
        )

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "user":
            line = f"{attr_name} = aws_iam_user.{attr_value}.id\n"
            context.rproc[f"aws_iam_user.{attr_value}"] = True
        return skip, line, flag1, flag2


class IamGroupMembershipHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_group_membership",
            clfn="iam", descfn="get_group",
            topkey="Users", key="UserName", filterid="GroupName",
        )

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "user" and attr_value != "null":
            line = f"{attr_name} = aws_iam_user.{attr_value}.id\n"
            common.add_dependancy("aws_iam_user", attr_value)
        return skip, line, flag1, flag2


class IamOpenidConnectProviderHandler(DefaultResourceHandler):

    def __init__(self) -> None:
        super().__init__(
            tf_type="aws_iam_openid_connect_provider",
            clfn="iam", descfn="list_open_id_connect_providers",
            topkey="OpenIDConnectProviderList", key="Arn", filterid="Arn",
        )

    def transform(self, line: str, attr_name: str, attr_value: str, flag1: bool, flag2: str) -> tuple[int, str, bool, str]:
        skip = 0
        if attr_name == "url":
            line = f'{attr_name} = "https://{attr_value}"\n'
        return skip, line, flag1, flag2


# ---------------------------------------------------------------------------
# Register all handlers
# ---------------------------------------------------------------------------

for _handler in [
    IamRoleHandler(),
    IamRolePolicyHandler(),
    IamRolePolicyAttachmentHandler(),
    IamPolicyHandler(),
    IamInstanceProfileHandler(),
    IamUserGroupMembershipHandler(),
    IamUserPolicyHandler(),
    IamGroupPolicyHandler(),
    IamServiceLinkedRoleHandler(),
    IamGroupPolicyAttachmentHandler(),
    IamGroupHandler(),
    IamUserHandler(),
    IamUserPolicyAttachmentHandler(),
    IamAccessKeyHandler(),
    IamGroupMembershipHandler(),
    IamOpenidConnectProviderHandler(),
]:
    register(_handler)
