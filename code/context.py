import sys, os
import logging

log = logging.getLogger("aws2tf")

AWS2TF_VERSION = "v6273"
TF_PROVIDER_VERSION = "6.27.0"
ESTTIME = 120.0
profile = "default"
sso = False
merge = False
fast = False
apionly = False
tracking_message = "aws2tf: Starting, update messages every 20 seconds"
CORES = 2
CWD = ""
PATH1 = ""
PATH2 = ""
PATH3 = ""
processed = []
dependancies = []
types = []
debug = False
debug5 = False
validate = False
warnings = False
show_status = False  # Show STATUS messages (controlled by --status flag)
dnet = False
dkms = False
dkey = False
dsgs = False
acc = "xxxxxxxxxxxx"
region = "xx-xxxx-x"
regionl = 0

# Adaptive progress tracking
TERRAFORM_PLAN_RATE = 25.0  # Initial estimate: resources per second
TERRAFORM_PLAN_SAMPLES = 0  # Number of samples collected
TERRAFORM_APPLY_RATE = 50.0  # Initial estimate: resources per second for apply
TERRAFORM_APPLY_SAMPLES = 0  # Number of apply samples collected
LAST_PLAN_TIME = 0.0  # Time taken for last terraform plan (for post-import estimate)
policies = []
policyarns = []
roles = []
aws_subnet_resp = []
aws_route_table_resp = []
aws_kms_alias_resp = []
aws_vpc_resp = []
aws_iam_role_resp = []
aws_instance_resp = []
lbc = 0
rbc = 0
asg_azs = False
plan2 = False
lbskipaacl = False
lbskipcnxl = False
mskcfg = False
ssmparamn = ""
repdbin = False
gulejobmaxcap = False
levsmap = False
ec2ignore = False
api_id = ""
stripblock = ""
stripstart = ""
stripend = ""
apigwrestapiid = ""
ssoinstance = None
emrsubnetid = False
# secretsmanager secret version
secid = ""
secvid = ""
pathadd = ""

meshname = ""
workaround = ""
expected = False
all_extypes = []
serverless = False
dzd = ""
dzgid = ""
dzpid = ""
connectinid = ""
waf2id = ""
waf2nm = ""
waf2sc = ""
ec2tag = None
ec2tagv = None
ec2tagk = None
subnetid = ""
credtype = "invalid"
elastirep = False
elastigrep = False
elasticc = False
kinesismsk = False
destbuck = False

badlist = []

## Dicts

rproc = {}
rdep = {}
trdep = {}

# for common boto3
MOPUP = {"aws_service_discovery_http_namespace": "ns-"}

# these skip import - as they can't be imported - or no way to find with boto3
noimport = {
    "aws_iam_user_group_membership": True,
    "aws_iam_security_token_service_preferences": True,
    "aws_ebs_snapshot_copy": True,
    "aws_ebs_snapshot_import": True,
    "aws_vpclattice_target_group_attachment": True,
}

tested = {}

# List Dicts
subnets = {}
vpcs = {}
subnetlist = {}
sglist = {}
vpclist = {}
ltlist = {}
lambdalist = {}
s3list = {}
rolelist = {}
policylist = {}
inplist = {}
bucketlist = {}
tgwlist = {}
gluedbs = {}
attached_role_policies_list = {}
role_policies_list = {}


def exit_aws2tf(mess):
    if mess is not None and mess != "":
        log.error(mess)

    sys.exit(1)
