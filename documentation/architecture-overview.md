# aws2tf Architecture Overview

## What is aws2tf?

aws2tf is a Python tool that imports existing AWS infrastructure into Terraform, automatically generating the corresponding Terraform HCL configuration files. It discovers AWS resources, imports them into Terraform state, and creates properly formatted `.tf` files with de-referenced values and dependency tracking.

## High-Level Workflow

```
1. Parse Arguments & Setup
   ├─ Validate CLI arguments (region, type, resource ID)
   ├─ Setup logging and context
   └─ Initialize workspace directory

2. Build Resource Lists (Parallel Discovery)
   ├─ Discover VPCs, Subnets, Security Groups
   ├─ Discover Lambda functions, S3 buckets
   ├─ Discover IAM roles, policies, instance profiles
   └─ Store in context for later reference

3. Process Requested Resources
   ├─ Call AWS APIs to list/describe resources
   ├─ Generate import statements
   └─ Track dependencies

4. Process Known Dependencies
   ├─ Import parent resources (VPCs for subnets, etc.)
   └─ Follow predefined dependency chains

5. Process Detected Dependencies (Iterative)
   ├─ Parse generated .tf files
   ├─ Find resource references
   ├─ Import missing dependencies
   └─ Repeat until no new dependencies found

6. Validate & Import
   ├─ Run terraform init
   ├─ Run terraform import for all resources
   ├─ Run terraform plan to verify
   └─ Check for drift

7. Finalize & Cleanup
   ├─ Run security checks (trivy)
   ├─ Merge files if requested (-s flag)
   ├─ Generate summary report
   └─ Exit
```

## Major Components

### 1. Main Entry Point (`aws2tf.py`)

Orchestrates the entire 10-phase workflow. Key functions:
- `main_new()` — main entry point
- `parse_and_validate_arguments()` — CLI argument parsing
- `setup_environment_and_context()` — initialize global state
- `build_resource_lists_phase()` — parallel resource discovery
- `process_detected_dependencies()` — iterative dependency resolution

### 2. Resource Handler Interface (`code/resource_handler.py`)

**The central abstraction.** Every Terraform resource type is represented by a class implementing `AWSResourceHandler`:

```python
class AWSResourceHandler(ABC):

    @property
    @abstractmethod
    def terraform_type(self) -> str: ...

    @abstractmethod
    def discover(self, resource_id: str | None) -> bool:
        """Call AWS APIs, write import blocks, register dependencies."""
        ...

    @abstractmethod
    def transform(self, line, attr_name, attr_value, flag1, flag2) -> tuple[int, str, bool, str]:
        """Transform a single HCL attribute line. Return (skip, line, flag1, flag2)."""
        ...

    def prescan(self, lines: list[str]) -> None:
        """Optional: inspect the full .out file before line-by-line transform."""
        pass
```

`discover()` replaces the old `get_aws_<service>.py` functions.
`transform()` replaces the old `fixtf_aws_resources/fixtf_<service>.py` functions.

### 3. Resource Registry (`code/resource_registry.py`)

A dict mapping every Terraform resource type string to its handler instance.

At startup:
1. `DefaultResourceHandler` instances are auto-created for all 1,600+ types from `aws_dict.aws_resources`.
2. Custom handler modules in `code/handlers/` call `register()` to override the defaults for resource types with non-trivial logic.

Handlers are looked up in `common.call_resource()` and `fixtf.fixtf()` before falling back to the old module-based paths, so migration is incremental — unmigrated services continue to work.

### 4. Custom Handlers (`code/handlers/`)

One file per AWS service group. Each file contains `AWSResourceHandler` subclasses that override `discover()` and/or `transform()` only where the default behaviour is insufficient.

| File | Services covered |
|------|-----------------|
| `lambda_.py` | All `aws_lambda_*` types |
| `iam.py` | All `aws_iam_*` types |
| `s3.py` | All `aws_s3_*` types |

Services not yet migrated fall through to the legacy code paths (see below).

See `MIGRATE_INSTRUCTIONS.md` for the step-by-step process of migrating a service.

### 5. Legacy Resource Files (being phased out)

These two directories are progressively replaced by `code/handlers/`:

- `code/get_aws_resources/aws_<service>.py` — one file per service, containing `get_aws_<type>()` functions that call boto3 and write import blocks.
- `code/fixtf_aws_resources/fixtf_<service>.py` — one file per service, containing `aws_<type>(t1, tt1, tt2, flag1, flag2)` functions that transform individual HCL lines.

Both directories will be empty once all services are migrated.

The following files in `fixtf_aws_resources/` are **not** being deleted — they contain shared utilities and data:

| File | Purpose |
|------|---------|
| `aws_dict.py` | Metadata registry (boto3 client, list op, response keys) for all 1,600+ resource types |
| `base_handler.py` | Static utility methods (`skip_if_null`, `add_resource_reference`, `sanitize_resource_name`, etc.) |
| `aws_common.py` | Cross-resource transforms applied to every resource (VPC refs, bucket refs, KMS refs, etc.) |
| `arn_dict.py` | ARN parsing data |
| `aws_not_implemented.py` | Exclusion list |
| `aws_no_import.py` | Import exclusion list |

### 6. Resource Metadata (`code/fixtf_aws_resources/aws_dict.py`)

Central registry mapping every Terraform resource type to its boto3 API details:

```python
aws_vpc = {
    "clfn": "ec2",              # boto3 client name
    "descfn": "describe_vpcs", # boto3 list/describe method
    "topkey": "Vpcs",           # top-level key in response
    "key": "VpcId",             # field holding the resource ID
    "filterid": "VpcId",        # filter parameter for single-resource lookup
}
```

### 7. Common Utilities (`code/common.py`)

Shared utilities used throughout:
- `write_import()` — write Terraform import statements
- `add_dependancy()` — queue a resource for dependency processing
- `add_known_dependancy()` — register a known child resource
- `call_resource()` — entry point for resource processing; checks registry first
- `getresource()` — generic boto3 paginator fallback
- `rc()` — execute shell commands
- `wrapup()` — run `terraform plan` and validate

### 8. File Transformation (`code/fixtf.py`)

Reads generated `.out` files line by line, calls `aws_common.aws_common()` for cross-resource transforms, then the resource-specific `handler.transform()`, and writes the result to the final `.tf` file.

The registry handler is resolved once per `fixtf()` call (before the line loop) and takes priority over the old `FIXTF_MODULES` dict.

### 9. Context (`code/context.py`)

Module-level global state. Key attributes:

| Attribute | Purpose |
|-----------|---------|
| `region`, `acc` | Current AWS region and account ID |
| `vpclist`, `subnetlist`, `sglist` | Pre-discovered resource ID maps |
| `lambdalist`, `s3list`, `rolelist`, `policylist` | More pre-discovered maps |
| `rproc` | Processed resource tracking (`type.id → True`) |
| `rdep`, `trdep` | Dependency queues |
| `fast`, `debug`, `merge` | Runtime flags |

### 10. Resource Discovery (`code/build_lists.py`)

Parallel pre-discovery of common resource types using `ThreadPoolExecutor`. Populates the `context.*list` dicts used by handlers. Runs before the main import phase.

### 11. Stack Processing (`code/stacks.py`)

CloudFormation stack import — discovers stacks and routes each stack resource through the normal `call_resource()` path.

## Data Flow

### Import Phase
```
User request (-t lambda)
    ↓
resources.py (type code → terraform type list)
    ↓
common.call_resource("aws_lambda_function", None)
    ↓
resource_registry → LambdaFunctionHandler.discover(None)   ← new path
    OR
AWS_RESOURCE_MODULES → get_aws_lambda.get_aws_lambda_function()  ← legacy path
    ↓
common.write_import() → import block written
    ↓
terraform import → .out file generated
    ↓
fixtf.fixtf("aws_lambda_function", ...)
    ↓
registry → LambdaFunctionHandler.transform()   ← new path
    OR
FIXTF_MODULES → fixtf_lambda.aws_lambda_function()  ← legacy path
    ↓
Clean .tf file written
```

## File Layout

```
aws2tf/
├── aws2tf.py                        # Main entry point
├── MIGRATE_INSTRUCTIONS.md          # How to migrate a service
├── code/
│   ├── resource_handler.py          # AWSResourceHandler ABC
│   ├── resource_registry.py         # Registry + DefaultResourceHandler
│   ├── handlers/                    # Migrated service handlers
│   │   ├── lambda_.py
│   │   ├── iam.py
│   │   └── s3.py
│   ├── build_lists.py               # Parallel pre-discovery
│   ├── resources.py                 # Type code mapping
│   ├── common.py                    # Shared utilities
│   ├── context.py                   # Global state
│   ├── stacks.py                    # CloudFormation
│   ├── fixtf.py                     # File transformation
│   ├── get_aws_resources/           # Legacy discovery (being phased out)
│   └── fixtf_aws_resources/         # Legacy transforms + shared data
│       ├── aws_dict.py              # Kept — resource metadata
│       ├── base_handler.py          # Kept — transform utilities
│       ├── aws_common.py            # Kept — cross-resource transforms
│       └── fixtf_<service>.py       # Being deleted as services migrate
├── tests/
└── generated/
    └── tf-<account>-<region>/
```
