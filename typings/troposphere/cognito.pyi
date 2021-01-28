"""
This type stub file was generated by pyright.
"""

from . import AWSObject, AWSProperty

VALID_RECOVERYOPTION_NAME = ("admin_only", "verified_email", "verified_phone_number")

def validate_recoveryoption_name(recoveryoption_name):
    """Validate Name for RecoveryOption"""
    ...

class CognitoIdentityProvider(AWSProperty):
    props = ...

class CognitoStreams(AWSProperty):
    props = ...

class PushSync(AWSProperty):
    props = ...

class IdentityPool(AWSObject):
    resource_type = ...
    props = ...

class MappingRule(AWSProperty):
    props = ...

class RulesConfiguration(AWSProperty):
    props = ...

class RoleMapping(AWSProperty):
    props = ...

class IdentityPoolRoleAttachment(AWSObject):
    resource_type = ...
    props = ...

class InviteMessageTemplate(AWSProperty):
    props = ...

class AdminCreateUserConfig(AWSProperty):
    props = ...

class DeviceConfiguration(AWSProperty):
    props = ...

class EmailConfiguration(AWSProperty):
    props = ...

class LambdaConfig(AWSProperty):
    props = ...

class PasswordPolicy(AWSProperty):
    props = ...

class Policies(AWSProperty):
    props = ...

class NumberAttributeConstraints(AWSProperty):
    props = ...

class StringAttributeConstraints(AWSProperty):
    props = ...

class SchemaAttribute(AWSProperty):
    props = ...

class SmsConfiguration(AWSProperty):
    props = ...

class UserPoolAddOns(AWSProperty):
    props = ...

class VerificationMessageTemplate(AWSProperty):
    props = ...

class RecoveryOption(AWSProperty):
    props = ...

class AccountRecoverySetting(AWSProperty):
    props = ...

class UsernameConfiguration(AWSProperty):
    props = ...

class UserPool(AWSObject):
    resource_type = ...
    props = ...

class AnalyticsConfiguration(AWSProperty):
    props = ...

class UserPoolClient(AWSObject):
    resource_type = ...
    props = ...

class CustomDomainConfigType(AWSProperty):
    props = ...

class UserPoolDomain(AWSObject):
    resource_type = ...
    props = ...

class UserPoolGroup(AWSObject):
    resource_type = ...
    props = ...

class UserPoolIdentityProvider(AWSObject):
    resource_type = ...
    props = ...

class ResourceServerScopeType(AWSProperty):
    props = ...

class UserPoolResourceServer(AWSObject):
    resource_type = ...
    props = ...

class AccountTakeoverActionType(AWSProperty):
    props = ...

class AccountTakeoverActionsType(AWSProperty):
    props = ...

class NotifyEmailType(AWSProperty):
    props = ...

class NotifyConfigurationType(AWSProperty):
    props = ...

class AccountTakeoverRiskConfigurationType(AWSProperty):
    props = ...

class CompromisedCredentialsActionsType(AWSProperty):
    props = ...

class CompromisedCredentialsRiskConfigurationType(AWSProperty):
    props = ...

class RiskExceptionConfigurationType(AWSProperty):
    props = ...

class UserPoolRiskConfigurationAttachment(AWSObject):
    resource_type = ...
    props = ...

class UserPoolUICustomizationAttachment(AWSObject):
    resource_type = ...
    props = ...

class AttributeType(AWSProperty):
    props = ...

class UserPoolUser(AWSObject):
    resource_type = ...
    props = ...

class UserPoolUserToGroupAttachment(AWSObject):
    resource_type = ...
    props = ...