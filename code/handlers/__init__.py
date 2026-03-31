"""
Custom resource handlers for AWS resource types that need non-default
discovery or transformation logic.

Each module in this package contains one or more AWSResourceHandler subclasses
and calls resource_registry.register() to override the DefaultResourceHandler
installed from aws_dict at startup.

Modules are imported here so that registrations happen at startup when this
package is imported.
"""

# Custom handler modules will be imported here as they are created.
# Example (uncomment as each service is migrated):
# from handlers import lambda_  # noqa: F401
# from handlers import s3       # noqa: F401
# from handlers import ec2      # noqa: F401
