import boto3
import os
import sys
import context
import logging

from get_aws_resources import aws_s3
import botocore
import common
from timed_interrupt import timed_int
from aws_null_cf_types import AWS_NULL_CF_TYPES

log = logging.getLogger("aws2tf")


## Enter here:
def get_stacks(stack_name):
    client = boto3.client("cloudformation")
    nested = []
    log.info("Level 1 stack nesting for " + stack_name)
    nested = getstack(stack_name, nested, client)

    if nested is not None:
        log.info("Level 2 stack nesting")
        for nest in nested:
            sn = nest.split("/")[1]
            if sn != stack_name:
                nested = getstack(sn, nested, client)

        log.info("-------------------------------------------")
        nst = len(nested)
        i = 1
        with open("stacks.sh", "a") as f6:
            for nest in nested:
                sn = nest.split("/")[1]
                f6.write("../../aws2tf.py -t stack -i " + sn + "\n")
                log.info(
                    "\n############## Getting resources for stack "
                    + sn
                    + " "
                    + str(i)
                    + " of "
                    + str(nst)
                    + " ##############"
                )
                getstackresources(nest, client)
                i = i + 1
            log.info("Stack " + stack_name + " done")


def getstack(stack_name, nested, client):
    try:
        # Get the stack info to get StackId
        stack_info = client.describe_stacks(StackName=stack_name)
        stack_id = stack_info["Stacks"][0]["StackId"]

        # Use paginator to get all stack resources (handles >100 resources)
        paginator = client.get_paginator("list_stack_resources")
        response = []
        for page in paginator.paginate(StackName=stack_name):
            response.extend(page["StackResourceSummaries"])

    except botocore.exceptions.ClientError as err:
        log.error("ValidationError error in getstack")
        log.error("Stack " + stack_name + " may not exist in region " + context.region)
        return

    except Exception as e:
        log.error(f"{e=}")
        log.error("-1->unexpected error in getstack")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.error("%s %s %s %s", exc_type, fname, exc_tb.tb_lineno)
        return

    # Add the stack ID to nested list
    if stack_id not in (str(nested)):
        nested = nested + [stack_id]

    for j in response:
        type = j["ResourceType"]
        stat = j["ResourceStatus"]

        # most added here
        if type == "AWS::CloudFormation::Stack":
            if stat == "CREATE_COMPLETE" or stat == "CREATE_FAILED":
                if stat == "CREATE_FAILED":
                    log.warning(
                        "WARNING: Stack " + stack_name + " status is CREATE_FAILED"
                    )
                stackr = j["PhysicalResourceId"]
                if stackr not in (str(nested)):
                    nested = nested + [stackr]

    return nested


def getstackresources(stack_name, client):
    try:
        log.info("Getting resources for stack: " + stack_name.split("/")[1])

        # Use paginator to get all stack resources (handles >100 resources)
        paginator = client.get_paginator("list_stack_resources")
        response = []
        for page in paginator.paginate(StackName=stack_name):
            response.extend(page["StackResourceSummaries"])
    except Exception as e:
        log.error(f"{e=}")
        log.error("-1->unexpected error in getstack")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.error("%s %s %s %s", exc_type, fname, exc_tb.tb_lineno)
        log.info("exit 014")
        timed_int.stop()
        exit()
    ri = 0
    rl = len(response)

    for j in response:
        f3 = open("stack-fetched-implicit.log", "a")
        f4 = open("stack-fetched-explicit.log", "a")
        f5 = open("stack-custom-resources.log", "a")

        type = j["ResourceType"]
        stat = j["ResourceStatus"]
        if stat == "CREATE_FAILED":
            log.warning("CREATE_FAILED status for " + type + "skipping .....")
            continue
        pid = j["PhysicalResourceId"].split("/")[-1]
        parn = j["PhysicalResourceId"]
        lrid = j["LogicalResourceId"]
        stat = j["ResourceStatus"]
        ri = ri + 1

        if context.debug:
            log.debug("type=" + type)
        sn = stack_name.split("/")[-2]
        log.info(
            "Importing " + str(ri) + " of " + str(rl) + " type=" + type + " pid=" + pid
        )

        f4.write("Type=" + type + " pid=" + pid + " parn=" + parn + "\n")

        if type == "AWS::CloudFormation::Stack":
            continue
        elif "AWS::CloudFormation::WaitCondition" in type:
            f3.write("skipping " + type + "\n")
        elif type in AWS_NULL_CF_TYPES:
            common.call_resource("aws_null", type + " " + pid)

        elif type == "AWS::ApplicationAutoScaling::ScalableTarget":
            common.call_resource("aws_appautoscaling_target", pid)
        elif type == "AWS::ApplicationAutoScaling::ScalingPolicy":
            common.call_resource("aws_appautoscaling_policy", pid)

        elif type == "AWS::AppMesh::Mesh":
            common.call_resource("aws_appmesh_mesh", pid)
        elif type == "AWS::AppMesh::VirtualGateway":
            f3.write(type + " " + pid + " fetched as part of parent mesh\n")
        elif type == "AWS::AppMesh::VirtualNode":
            f3.write(type + " " + pid + "  fetched as part of parent mesh\n")
        elif type == "AWS::AppMesh::VirtualRouter":
            f3.write(type + " " + pid + "  fetched as part of parent mesh\n")
        elif type == "AWS::AppMesh::VirtualService":
            f3.write(type + " " + pid + "  fetched as part of parent mesh\n")

        elif type == "AWS::Athena::NamedQuery":
            common.call_resource("aws_athena_named_query", pid)
        elif type == "AWS::Athena::WorkGroup":
            common.call_resource("aws_athena_workgroup", pid)

        elif type == "AWS::AutoScaling::AutoScalingGroup":
            common.call_resource("aws_autoscaling_group", pid)
        elif type == "AWS::AutoScaling::LaunchConfiguration":
            common.call_resource("aws_launch_configuration", pid)
        elif type == "AWS::AutoScaling::LifecycleHook":
            common.call_resource("aws_autoscaling_lifecycle_hook", pid)

        elif type == "AWS::CDK::Metadata":
            f3.write(type + " " + pid + " skipped only relevant to CDK .. \n")

        elif type == "AWS::Cloud9::EnvironmentEC2":
            common.call_resource("aws_cloud9_environment_ec2", pid)

        elif type == "AWS::CloudWatch::Alarm":
            common.call_resource("aws_cloudwatch_metric_alarm", parn)

        elif type == "AWS::EC2::Instance":
            common.call_resource("aws_instance", pid)
        elif type == "AWS::EC2::KeyPair":
            common.call_resource("aws_key_pair", pid)
        elif type == "AWS::EC2::DHCPOptions":
            common.call_resource("aws_vpc_dhcp_options", pid)
        elif type == "AWS::EC2::EIP":
            f3.write(type + " " + pid + " fetched as part of other resources..\n")
        elif type == "AWS::EC2::NatGateway":
            common.call_resource("aws_nat_gateway", pid)
        elif type == "AWS::EC2::NetworkAcl":
            common.call_resource("aws_network_acl", pid)
        elif type == "AWS::EC2::NetworkAclEntry":
            f3.write(type + " " + pid + " fetched as part of NetworkAcl..\n")
        elif type == "AWS::EC2::SubnetNetworkAclAssociation":
            f3.write(type + " fetched as part of NetworkAcl..\n")
        elif type == "AWS::EC2::InternetGateway":
            common.call_resource("aws_internet_gateway", pid)
        elif type == "AWS::EC2::LaunchTemplate":
            common.call_resource("aws_launch_template", pid)
        elif type == "AWS::EC2::SecurityGroup":
            common.call_resource("aws_security_group", pid)
        elif type == "AWS::EC2::SecurityGroupIngress":
            f3.write(type + " fetched as part of SecurityGroup..\n")
        elif type == "AWS::EC2::SecurityGroupEgress":
            f3.write(type + " fetched as part of SecurityGroup..\n")

        elif type == "AWS::EC2::VPCEndpoint":
            common.call_resource("aws_vpc_endpoint", pid)
        elif type == "AWS::EC2::VPC":
            common.call_resource("aws_vpc", pid)
        elif type == "AWS::EC2::Subnet":
            common.call_resource("aws_subnet", pid)
        elif type == "AWS::EC2::RouteTable":
            common.call_resource("aws_route_table", pid)
        elif type == "AWS::EC2::Route":
            f3.write(type + " " + pid + " fetched as part of RouteTable...\n")
        elif type == "AWS::EC2::SubnetRouteTableAssociation":
            f3.write(type + " " + pid + " fetched as part of Subnet...\n")
        elif type == "AWS::EC2::VPCGatewayAttachment":
            f3.write(type + " " + pid + " fetched as part of IGW...\n")
        elif type == "AWS::EC2::VPCEndpointService":
            common.call_resource("aws_vpc_endpoint_service", pid)
        elif type == "AWS::EC2::FlowLog":
            common.call_resource("aws_flow_log", pid)

        elif type == "AWS::ECR::Repository":
            common.call_resource("aws_ecr_repository", pid)

        elif type == "AWS::ECS::Cluster":
            common.call_resource("aws_ecs_cluster", pid)
        elif type == "AWS::ECS::Service":
            common.call_resource("aws_ecs_service", parn)
        elif type == "AWS::ECS::TaskDefinition":
            common.call_resource("aws_ecs_task_definition", pid)

        elif type == "AWS::EFS::FileSystem":
            common.call_resource("aws_efs_file_system", pid)
        elif type == "AWS::EFS::MountTarget":
            f3.write(type + " " + pid + " attached as part of EFS::FileSystem ..\n")
        elif type == "AWS::EFS::AccessPoint":
            f3.write(type + " " + pid + " attached as part of EFS::FileSystem ..\n")

        elif type == "AWS::EKS::Cluster":
            common.call_resource("aws_eks_cluster", pid)
        elif type == "AWS::EKS::Nodegroup":
            f3.write(
                type + " " + pid + "  Should be fetched via the EKS Cluster Resource\n"
            )

        elif type == "AWS::ElasticLoadBalancingV2::LoadBalancer":
            common.call_resource("aws_lb", parn)
        elif type == "AWS::ElasticLoadBalancingV2::Listener":
            common.call_resource("aws_lb_listener", parn)
        elif type == "AWS::ElasticLoadBalancingV2::ListenerRule":
            common.call_resource("aws_lb_listener_rule", parn)
        elif type == "AWS::ElasticLoadBalancingV2::TargetGroup":
            common.call_resource("aws_lb_target_group", parn)

        elif type == "AWS::EMR::Cluster":
            common.call_resource("aws_emr_cluster", pid)
        elif type == "AWS::EMR::SecurityConfiguration":
            common.call_resource("aws_emr_security_configuration", pid)

        elif type == "AWS::Events::EventBus":
            common.call_resource("aws_cloudwatch_event_bus", pid)
        elif type == "AWS::Events::Rule":
            common.call_resource("aws_cloudwatch_event_rule", pid)

        elif type == "AWS::Glue::Connection":
            common.call_resource("aws_glue_connection", pid)
        elif type == "AWS::Glue::Crawler":
            common.call_resource("aws_glue_crawler", pid)
        elif type == "AWS::Glue::Database":
            common.call_resource("aws_glue_catalog_database", pid)
        elif type == "AWS::Glue::Job":
            common.call_resource("aws_glue_job", pid)
        elif type == "AWS::Glue::Table":
            f3.write(type + " " + pid + " fetched as part of AWS::Glue::Database ...\n")
        elif type == "AWS::Glue::Trigger":
            common.call_resource("aws_glue_trigger", pid)
        elif type == "AWS::Glue::Partition":
            common.call_resource("aws_glue_partition", pid)

        elif type == "AWS::IAM::Role":
            common.call_resource("aws_iam_role", pid)
        elif type == "AWS::IAM::ManagedPolicy":
            common.call_resource("aws_iam_policy", parn)
        elif type == "AWS::IAM::InstanceProfile":
            common.call_resource("aws_iam_instance_profile", pid)
        elif type == "AWS::IAM::User":
            common.call_resource("aws_iam_user", pid)
        elif type == "AWS::IAM::AccessKey":
            f3.write(type + " " + pid + " Should be fetched via IAM Users etc\n")
        elif type == "AWS::IAM::ServiceLinkedRole":
            common.call_resource("aws_iam_service_linked_role", pid)
        elif type == "AWS::IAM::Group":
            common.call_resource("aws_iam_group", pid)
        # elif type == "AWS::IAM::Policy)  echo "../../scripts/get-iam-policies.sh $parn" >> commands.sh ;;
        elif type == "AWS::IAM::Policy":
            f3.write(type + " " + pid + " Should be fetched via Roles etc\n")

        elif type == "AWS::KinesisFirehose::DeliveryStream":
            common.call_resource("aws_kinesis_firehose_delivery_stream", pid)
        elif type == "AWS::Kinesis::Stream":
            common.call_resource("aws_kinesis_stream", pid)

        elif type == "AWS::KMS::Key":
            common.call_resource("aws_kms_key", pid)
        elif type == "AWS::KMS::Alias":
            common.call_resource("aws_kms_alias", pid)

        elif type == "AWS::LakeFormation::DataLakeSettings":
            common.call_resource("aws_lakeformation_data_lake_settings", pid)
        elif type == "AWS::LakeFormation::Resource":
            common.call_resource("aws_lakeformation_resource", pid)
        # pid pard can be json structures for this one
        elif type == "AWS::LakeFormation::Permissions":
            common.call_resource("aws_lakeformation_permissions", pid)
        elif type == "AWS::LakeFormation::PrincipalPermissions":
            common.call_resource("aws_lakeformation_permissions", lrid)

        elif type == "AWS::Logs::LogGroup":
            common.call_resource("aws_cloudwatch_log_group", pid)

        ##### terraform crash !
        elif type == "AWS::RedshiftServerless::Namespace":
            common.call_resource("aws_redshiftserverless_namespace", pid)
        ##### terraform crash !

        elif type == "AWS::RedshiftServerless::Workgroup":
            common.call_resource("aws_redshiftserverless_workgroup", pid)

        elif type == "AWS::Redshift::Cluster":
            common.call_resource("aws_redshift_cluster", pid)
        elif type == "AWS::Redshift::ClusterParameterGroup":
            common.call_resource("aws_redshift_parameter_group", pid)
        elif type == "AWS::Redshift::ClusterSubnetGroup":
            common.call_resource("aws_redshift_subnet_group", pid)

        elif type == "AWS::RDS::DBCluster":
            common.call_resource("aws_rds_cluster", pid)
        elif type == "AWS::RDS::DBClusterParameterGroup":
            common.call_resource("aws_rds_cluster_parameter_group", pid)
        elif type == "AWS::RDS::DBInstance":
            common.call_resource("aws_db_instance", pid)
        elif type == "AWS::RDS::DBParameterGroup":
            common.call_resource("aws_db_parameter_group", pid)
        elif type == "AWS::RDS::DBSubnetGroup":
            common.call_resource("aws_db_subnet_group", pid)
        elif type == "AWS::RDS::EventSubscription":
            common.call_resource("aws_db_event_subscription", pid)

        elif type == "AWS::ServiceCatalog::PortfolioPrincipalAssociation":
            tarn = parn.split("|")[0]
            common.call_resource("aws_null", tarn)

        elif type == "AWS::S3::Bucket":
            common.call_resource("aws_s3_bucket", pid)
        elif type == "AWS::S3::BucketPolicy":
            f3.write(type + " fetched as part of bucket...\n")
        elif type == "AWS::S3::AccessGrant":
            common.call_resource("aws_s3control_access_grant", pid)
        elif type == "AWS::S3::AccessGrantsInstance":
            common.call_resource("aws_s3control_access_grants_instance", pid)
        elif type == "AWS::S3::AccessGrantsLocation":
            common.call_resource("aws_s3control_access_grants_location", pid)
        elif type == "AWS::S3::AccessPoint":
            common.call_resource("aws_s3_access_point", pid)
        elif type == "AWS::S3::MultiRegionAccessPoint":
            common.call_resource("aws_s3control_multi_region_access_point", pid)
        elif type == "AWS::S3::MultiRegionAccessPointPolicy":
            common.call_resource("aws_s3control_multi_region_access_point_policy", pid)
        elif type == "AWS::S3::StorageLens":
            common.call_resource("aws_s3control_storage_lens_configuration", pid)

        elif type == "AWS::SageMaker::AppImageConfig":
            common.call_resource("aws_sagemaker_app_image_config", pid)
        elif type == "AWS::SageMaker::Domain":
            common.call_resource("aws_sagemaker_domain", parn)
        elif type == "AWS::SageMaker::Image":
            common.call_resource("aws_sagemaker_image", pid)
        elif type == "AWS::SageMaker::ImageVersion":
            f3.write(type + " " + pid + "  as part of SageMaker Image..\n")
        elif type == "AWS::SageMaker::NotebookInstance":
            common.call_resource("aws_sagemaker_notebook_instance", pid)
        elif type == "AWS::SageMaker::UserProfile":
            common.call_resource("aws_sagemaker_user_profile", pid)

        elif type == "AWS::SNS::Subscription":
            common.call_resource("aws_sns_topic_subscription", parn)
        elif type == "AWS::SNS::Topic":
            common.call_resource("aws_sns_topic", parn)
        elif type == "AWS::SNS::TopicPolicy":
            common.call_resource("aws_sns_topic_policy", parn)
        elif type == "AWS::SQS::Queue":
            common.call_resource("aws_sqs_queue", parn)
        elif type == "AWS::SQS::QueuePolicy":
            f3.write(type + " " + pid + "  as part of SQS Queue ..\n")

        elif type == "AWS::SSM::Parameter":
            common.call_resource("aws_ssm_parameter", pid)
        elif type == "AWS::ServiceDiscovery::PrivateDnsNamespace":
            common.call_resource("aws_service_discovery_private_dns_namespace", pid)
        elif type == "AWS::StepFunctions::StateMachine":
            common.call_resource("aws_sfn_state_machine", pid)
        elif type == "AWS::SecretsManager::SecretTargetAttachment":
            f3.write(type + " " + pid + " implicit elsewhere ..\n")
        elif type == "AWS::SecretsManager::Secret":
            common.call_resource("aws_secretsmanager_secret", parn)
        elif type == "AWS::ServiceDiscovery::Service":
            common.call_resource(" aws_service_discovery_service", pid)
        elif type == "AWS::ACMPCA::CertificateAuthority":
            common.call_resource("aws_acmpca_certificate_authority", pid)
        elif type == "AWS::ACMPCA::Permission":
            common.call_resource("aws_acmpca_permission", pid)
        elif type == "AWS::AccessAnalyzer::Analyzer":
            common.call_resource("aws_accessanalyzer_analyzer", pid)
        elif type == "AWS::AmazonMQ::Broker":
            common.call_resource("aws_mq_broker", pid)
        elif type == "AWS::AmazonMQ::Configuration":
            common.call_resource("aws_mq_configuration", pid)
        elif type == "AWS::Amplify::App":
            common.call_resource("aws_amplify_app", pid)
        elif type == "AWS::Amplify::Branch":
            f3.write(type + " " + pid + " as part of Amplify App ..\n")

        elif type == "AWS::ApiGateway::Account":
            f3.write(
                "Error: **Terraform does not support import of " + type + " skipped**\n"
            )
        elif type == "AWS::ApiGateway::ApiKey":
            common.call_resource("aws_api_gateway_api_key", pid)
        elif type == "AWS::ApiGateway::Authorizer":
            f3.write(type + " " + pid + "  as part of RestApi..\n")
        elif type == "AWS::ApiGateway::BasePathMapping":
            common.call_resource("aws_api_gateway_base_path_mapping", pid)
        elif type == "AWS::ApiGateway::ClientCertificate":
            common.call_resource("aws_api_gateway_client_certificate", pid)
        elif type == "AWS::ApiGateway::Deployment":
            f3.write(type + " " + pid + " as part of RestApi..\n")
        elif type == "AWS::ApiGateway::DomainName":
            common.call_resource("aws_api_gateway_domain_name", pid)
        elif type == "AWS::ApiGateway::GatewayResponse":
            common.call_resource("aws_api_gateway_gateway_response", pid)
        elif type == "AWS::ApiGateway::Method":
            f3.write(type + " " + pid + " as part of RestApi..\n")
        elif type == "AWS::ApiGateway::Model":
            common.call_resource("aws_api_gateway_model", pid)
        elif type == "AWS::ApiGateway::RequestValidator":
            common.call_resource("aws_api_gateway_request_validator", pid)
        elif type == "AWS::ApiGateway::Resource":
            f3.write(type + " " + pid + "  as part of RestApi..\n")
        elif type == "AWS::ApiGateway::Stage":
            f3.write(type + " " + pid + "  as part of RestApi..\n")
        elif type == "AWS::ApiGateway::UsagePlan":
            common.call_resource("aws_api_gateway_usage_plan", pid)
        elif type == "AWS::ApiGateway::UsagePlanKey":
            common.call_resource("aws_api_gateway_usage_plan_key", pid)
        elif type == "AWS::ApiGateway::VpcLink":
            common.call_resource("aws_api_gateway_vpc_link", pid)
        elif type == "AWS::ApiGateway::RestApi":
            common.call_resource("aws_api_gateway_rest_api", pid)

        elif type == "AWS::ApiGatewayV2::Api":
            common.call_resource("aws_apigatewayv2_api", pid)
        elif type == "AWS::ApiGatewayV2::ApiMapping":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::Authorizer":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::Deployment":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::DomainName":
            common.call_resource("aws_apigatewayv2_domain_name", pid)
        elif type == "AWS::ApiGatewayV2::Integration":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::IntegrationResponse":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::Model":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::Route":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::RouteResponse":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::Stage":
            f3.write(type + " " + pid + " fetched as part of ApiGatewayV2 Api..\n")
        elif type == "AWS::ApiGatewayV2::VpcLink":
            common.call_resource("aws_apigatewayv2_vpc_link", pid)

        elif type == "AWS::AppMesh::GatewayRoute":
            common.call_resource("aws_appmesh_gateway_route", pid)
        elif type == "AWS::AppMesh::Route":
            common.call_resource("aws_appmesh_route", pid)
        elif type == "AWS::Athena::DataCatalog":
            common.call_resource("aws_athena_data_catalog", pid)
        elif type == "AWS::Athena::PreparedStatement":
            common.call_resource("aws_athena_prepared_statement", pid)
        elif type == "AWS::CertificateManager::Certificate":
            common.call_resource("aws_acm_certificate", parn)
        elif type == "AWS::CloudFormation::CustomResource":
            f5.write("Type=" + type + " pid=" + pid + " parn=" + parn + "\n")
        elif type == "AWS::CloudFront::CachePolicy":
            common.call_resource("aws_cloudfront_cache_policy", pid)
        elif type == "AWS::CloudFront::CloudFrontOriginAccessIdentity":
            common.call_resource("aws_cloudfront_origin_access_identity", pid)
        elif type == "AWS::CloudFront::Distribution":
            common.call_resource("aws_cloudfront_distribution", parn)
        elif type == "AWS::CloudFront::Function":
            common.call_resource("aws_cloudfront_function", pid)
        elif type == "AWS::CloudFront::OriginAccessControl":
            common.call_resource("aws_cloudfront_origin_access_control", pid)
        elif type == "AWS::CloudFront::OriginRequestPolicy":
            common.call_resource("aws_cloudfront_origin_request_policy", pid)
        elif type == "AWS::CloudWatch::Dashboard":
            common.call_resource("aws_cloudwatch_dashboard", pid)
        elif type == "AWS::CloudWatch::InsightRule":
            common.call_resource("aws_cloudwatch_contributor_insight_rule", parn)
        # elif type == "AWS::CodeBuild::Project": common.call_resource("aws_codebuild_project", pid)
        elif type == "AWS::CodeCommit::Repository":
            common.call_resource("aws_codecommit_repository", pid)
        elif type == "AWS::Cognito::UserPool":
            common.call_resource("aws_cognito_user_pool", pid)
        elif type == "AWS::Cognito::UserPoolClient":
            f3.write(type + " " + pid + " fetched as part of Cognito UserPool\n")
        elif type == "AWS::Cognito::UserPoolDomain":
            common.call_resource("aws_cognito_user_pool_domain", pid)
        elif type == "AWS::Cognito::UserPoolGroup":
            f3.write(type + " " + pid + " fetched as part of Cognito UserPool\n")
        elif type == "AWS::Config::ConfigRule":
            common.call_resource("aws_config_config_rule", pid)
        elif type == "AWS::Config::ConfigurationRecorder":
            common.call_resource("aws_config_configuration_recorder", pid)
        elif type == "AWS::Config::DeliveryChannel":
            common.call_resource("aws_config_delivery_channel", pid)
        elif type == "AWS::Connect::ContactFlow":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::Connect::HoursOfOperation":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::Connect::Instance":
            common.call_resource("aws_connect_instance", pid)
        elif type == "AWS::Connect::InstanceStorageConfig":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::Connect::IntegrationAssociation":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::Connect::PhoneNumber":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::Connect::Queue":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::Connect::RoutingProfile":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::Connect::SecurityProfile":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::Connect::User":
            f3.write(type + " " + pid + " as part of Connect Instance..\n")
        elif type == "AWS::DMS::ReplicationInstance":
            common.call_resource("aws_dms_replication_instance", pid)
        elif type == "AWS::DMS::ReplicationSubnetGroup":
            common.call_resource("aws_dms_replication_subnet_group", pid)
        elif type == "AWS::DataZone::DataSource":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DataZone::Domain":
            common.call_resource("aws_datazone_domain", pid)
        elif type == "AWS::DataZone::Environment":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DataZone::EnvironmentActions":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DataZone::EnvironmentBlueprintConfiguration":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DataZone::EnvironmentProfile":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DataZone::Project":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DataZone::ProjectMembership":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DataZone::SubscriptionTarget":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DataZone::UserProfile":
            f3.write(type + " " + pid + " Should be fetched via DataZone Domain\n")
        elif type == "AWS::DirectoryService::MicrosoftAD":
            common.call_resource("aws_directory_service_directory", pid)
        elif type == "AWS::DocDB::DBCluster":
            common.call_resource("aws_docdb_cluster", pid)
        elif type == "AWS::DocDB::DBInstance":
            common.call_resource("aws_docdb_cluster_instance", pid)
        elif type == "AWS::DocDB::DBSubnetGroup":
            common.call_resource("aws_docdb_subnet_group", pid)
        elif type == "AWS::DynamoDB::Table":
            common.call_resource("aws_dynamodb_table", pid)
        elif type == "AWS::EC2::EIPAssociation":
            common.call_resource("aws_eip_association", pid)
        elif type == "AWS::EC2::GatewayRouteTableAssociation":
            f3.write(type + " " + pid + " Should be fetched via Route Table\n")
        elif type == "AWS::EC2::TransitGateway":
            common.call_resource("aws_ec2_transit_gateway", pid)
        elif type == "AWS::EC2::VPCDHCPOptionsAssociation":
            common.call_resource("aws_vpc_dhcp_options_association", pid)
        elif type == "AWS::EC2::Volume":
            common.call_resource("aws_ebs_volume", pid)
        elif type == "AWS::EMR::InstanceGroupConfig":
            f3.write(type + " " + pid + " fetched as part of aws_emr_cluster..\n")
        elif type == "AWS::Glue::Classifier":
            common.call_resource("aws_glue_classifier", pid)
        elif type == "AWS::Glue::SecurityConfiguration":
            common.call_resource("aws_glue_security_configuration", pid)
        elif type == "AWS::IAM::UserToGroupAddition":
            f3.write(type + " fetched as part of IAM Group...\n")
        elif type == "AWS::Kendra::DataSource":
            f3.write(type + " " + pid + " fetched as part of Kendra Index ..\n")
        elif type == "AWS::Kendra::Faq":
            f3.write(type + " " + pid + " fetched as part of Kendra Index ..\n")
        elif type == "AWS::Kendra::Index":
            common.call_resource("aws_kendra_index", pid)
        elif type == "AWS::Lambda::Function":
            common.call_resource("aws_lambda_function", pid)
        elif type == "AWS::Lambda::LayerVersion":
            common.call_resource("aws_lambda_layer_version", pid)
        elif type == "AWS::Lambda::Permission":
            f3.write(
                type + " " + pid + "  as part of function..\n"
            )  # fetched as part of function
        elif type == "AWS::Lambda::EventInvokeConfig":
            f3.write(
                type + " " + pid + "  as part of function..\n"
            )  # fetched as part of function
        elif type == "AWS::Lambda::EventSourceMapping":
            f3.write(
                type + " " + pid + "  as part of function..\n"
            )  # fetched as part of function
        elif type == "AWS::Lambda::Alias":
            common.call_resource("aws_lambda_alias", parn)
        elif type == "AWS::Lambda::CodeSigningConfig":
            common.call_resource("aws_lambda_code_signing_config", parn)
        elif type == "AWS::Lambda::Url":
            # Extract function name from ARN for import
            # ARN format: arn:aws:lambda:region:account:function:function-name
            function_name = pid.split(":")[-1] if pid.startswith("arn:") else pid
            common.call_resource("aws_lambda_function_url", function_name)
        elif type == "AWS::Lambda::Version":
            f3.write(type + " " + pid + " fetched as part of Lambda function..\n")
        elif type == "AWS::MSK::Cluster":
            common.call_resource("aws_msk_cluster", parn)
        elif type == "AWS::MSK::ClusterPolicy":
            f3.write(type + " " + pid + " fetched as part of aws_msk_cluster..\n")
        elif type == "AWS::MSK::ServerlessCluster":
            common.call_resource("aws_msk_serverless_cluster", parn)
        elif type == "AWS::MWAA::Environment":
            common.call_resource("aws_mwaa_environment", pid)
        elif type == "AWS::NetworkFirewall::Firewall":
            common.call_resource("aws_networkfirewall_firewall", pid)
        elif type == "AWS::NetworkFirewall::FirewallPolicy":
            common.call_resource("aws_networkfirewall_firewall_policy", pid)
        elif type == "AWS::NetworkFirewall::LoggingConfiguration":
            f3.write(type + " " + pid + " fetched as part of Firewall..\n")
        elif type == "AWS::NetworkFirewall::RuleGroup":
            common.call_resource("aws_networkfirewall_rule_group", parn)
        elif type == "AWS::OpenSearchService::Domain":
            common.call_resource("aws_opensearch_domain", pid)
        elif type == "AWS::Pipes::Pipe":
            common.call_resource("aws_pipes_pipe", pid)
        elif type == "AWS::RDS::DBSecurityGroup":
            common.call_resource("aws_security_group", pid)
        elif type == "AWS::Route53::HostedZone":
            common.call_resource("aws_route53_zone", pid)
        elif type == "AWS::Route53::RecordSet":
            f3.write(type + " " + pid + " fetched as part of Route53 HostedZone..\n")
        elif type == "AWS::SSM::Association":
            common.call_resource("aws_ssm_association", pid)
        elif type == "AWS::SSM::Document":
            common.call_resource("aws_ssm_document", pid)
        elif type == "AWS::SageMaker::CodeRepository":
            common.call_resource("aws_sagemaker_code_repository", pid)
        elif type == "AWS::SageMaker::Endpoint":
            common.call_resource("aws_sagemaker_endpoint", pid)
        elif type == "AWS::SageMaker::Model":
            common.call_resource("aws_sagemaker_model", pid)
        elif type == "AWS::SageMaker::NotebookInstanceLifecycleConfig":
            common.call_resource(
                "aws_sagemaker_notebook_instance_lifecycle_configuration", pid
            )
        elif type == "AWS::SageMaker::Pipeline":
            common.call_resource("aws_sagemaker_pipeline", pid)
        elif type == "AWS::SageMaker::Project":
            common.call_resource("aws_sagemaker_project", pid)
        elif type == "AWS::SageMaker::Space":
            common.call_resource("aws_sagemaker_space", pid)
        elif type == "AWS::SageMaker::Workteam":
            common.call_resource("aws_sagemaker_workteam", pid)
        elif type == "AWS::Scheduler::ScheduleGroup":
            common.call_resource("aws_scheduler_schedule_group", pid)
        elif type == "AWS::SecretsManager::ResourcePolicy":
            common.call_resource("aws_secretsmanager_secret_policy", pid)
        elif type == "AWS::SecretsManager::RotationSchedule":
            common.call_resource("aws_secretsmanager_secret_rotation", pid)
            common.call_resource("aws_null", type + " " + pid)
        elif type == "AWS::ServiceDiscovery::HttpNamespace":
            common.call_resource("aws_service_discovery_http_namespace", pid)
        elif type == "AWS::StepFunctions::Activity":
            common.call_resource("aws_sfn_activity", pid)
        elif type == "AWS::StepFunctions::StateMachineAlias":
            common.call_resource("aws_sfn_alias", pid)
        elif type == "AWS::VpcLattice::AccessLogSubscription":
            common.call_resource("aws_vpclattice_access_log_subscription", pid)
        elif type == "AWS::VpcLattice::AuthPolicy":
            common.call_resource("aws_vpclattice_auth_policy", pid)
        elif type == "AWS::VpcLattice::Listener":
            common.call_resource("aws_vpclattice_listener", pid)
        elif type == "AWS::VpcLattice::ResourcePolicy":
            common.call_resource("aws_vpclattice_resource_policy", pid)
        elif type == "AWS::VpcLattice::Rule":
            common.call_resource("aws_vpclattice_listener_rule", pid)
        elif type == "AWS::VpcLattice::Service":
            common.call_resource("aws_vpclattice_service", pid)
        elif type == "AWS::VpcLattice::ServiceNetwork":
            common.call_resource("aws_vpclattice_service_network", pid)
        elif type == "AWS::VpcLattice::ServiceNetworkServiceAssociation":
            common.call_resource(
                "aws_vpclattice_service_network_service_association", pid
            )
        elif type == "AWS::VpcLattice::ServiceNetworkVpcAssociation":
            common.call_resource("aws_vpclattice_service_network_vpc_association", pid)
        elif type == "AWS::VpcLattice::TargetGroup":
            common.call_resource("aws_vpclattice_target_group", pid)
        elif type == "AWS::WAFv2::IPSet":
            common.call_resource("aws_wafv2_ip_set", pid)
        elif type == "AWS::WAFv2::LoggingConfiguration":
            f3.write(type + " " + pid + " fetched as part of wafv2_web__acl..\n")
        elif type == "AWS::WAFv2::WebACL":
            common.call_resource("aws_wafv2_web_acl", pid)
        elif type == "AWS::WorkSpaces::Workspace":
            common.call_resource("aws_workspaces_workspace", pid)
        elif type == "AWS::XRay::Group":
            common.call_resource("aws_xray_group", parn)
        elif type == "":
            common.call_resource("aws_null", type + " " + pid)
            # END AUTOGEN
        elif "Custom::" in type:
            f3.write(type + " fetched as Lambda function ..." + pid + "\n")
        else:
            log.warning("--UNPROCESSED-- " + type + " " + pid + " " + parn)
            with open("stack-unprocessed.err", "a") as f:
                f.write("--UNPROCESSED-- " + type + " " + pid + " " + parn + " \n")

    f3.close()
    f4.close()
    f5.close()
    ## Plan it so Terraform not overwhealmed ?
    # common.tfplan1()
    # common.tfplan2()

    return
