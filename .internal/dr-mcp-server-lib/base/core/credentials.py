# Copyright 2025 DataRobot, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Dict, Optional

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from base.core.config_utils import (
    extract_datarobot_credential_runtime_param_payload,
    extract_datarobot_runtime_param_payload,
)
from base.core.constants import (
    DEFAULT_DATAROBOT_ENDPOINT,
    RUNTIME_PARAM_ENV_VAR_NAME_PREFIX,
)


class DataRobotCredentials(BaseSettings):
    """DataRobot API credentials."""

    application_api_token: str = Field(
        default="",
        validation_alias=AliasChoices(
            RUNTIME_PARAM_ENV_VAR_NAME_PREFIX + "DATAROBOT_API_TOKEN",
            "DATAROBOT_API_TOKEN",
        ),
        description="DataRobot API token",
    )
    endpoint: str = Field(
        default=DEFAULT_DATAROBOT_ENDPOINT,
        validation_alias=AliasChoices(
            RUNTIME_PARAM_ENV_VAR_NAME_PREFIX + "DATAROBOT_ENDPOINT",
            "DATAROBOT_ENDPOINT",
        ),
        description="DataRobot API endpoint",
    )

    @field_validator(
        "application_api_token",
        "endpoint",
        mode="before",
    )
    @classmethod
    def validate_runtime_params(cls, v: Any) -> Any:
        """Validate runtime parameters."""
        return extract_datarobot_runtime_param_payload(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )


class MCPServerCredentials(BaseSettings):
    """Application credentials combining DataRobot and AWS credentials."""

    datarobot: DataRobotCredentials = Field(default_factory=DataRobotCredentials)

    # AWS Credentials - loaded from DataRobot credential object via aws_credential runtime parameter
    aws_credential: Optional[Dict[str, Any]] = Field(
        default=None,
        validation_alias=AliasChoices(
            RUNTIME_PARAM_ENV_VAR_NAME_PREFIX + "AWS_CREDENTIAL",
            "AWS_CREDENTIAL",
        ),
        description="DataRobot AWS Credential object (contains awsAccessKeyId, awsSecretAccessKey, awsSessionToken)",
    )
    # AWS credentials are also available as direct environment variables for local development
    aws_access_key_id: Optional[str] = Field(
        default=None,
        alias="AWS_ACCESS_KEY_ID",
        description="AWS Access Key ID (direct, for local use)",
    )
    aws_secret_access_key: Optional[str] = Field(
        default=None,
        alias="AWS_SECRET_ACCESS_KEY",
        description="AWS Secret Access Key (direct, for local use)",
    )
    aws_session_token: Optional[str] = Field(
        default=None,
        alias="AWS_SESSION_TOKEN",
        description="AWS Session Token (direct, for local use)",
    )

    aws_predictions_s3_bucket: str = Field(
        default="datarobot-rd",
        validation_alias=AliasChoices(
            RUNTIME_PARAM_ENV_VAR_NAME_PREFIX + "AWS_PREDICTIONS_S3_BUCKET",
            "AWS_PREDICTIONS_S3_BUCKET",
        ),
        description="S3 bucket name",
    )
    aws_predictions_s3_prefix: str = Field(
        default="dev/mcp-temp-storage/predictions/",
        validation_alias=AliasChoices(
            RUNTIME_PARAM_ENV_VAR_NAME_PREFIX + "AWS_PREDICTIONS_S3_PREFIX",
            "AWS_PREDICTIONS_S3_PREFIX",
        ),
        description="S3 key prefix",
    )

    @field_validator(
        "aws_credential",
        "aws_predictions_s3_bucket",
        "aws_predictions_s3_prefix",
        mode="before",
    )
    @classmethod
    def validate_credential_runtime_params(cls, v: Any) -> Any:
        """Validate credential runtime parameters"""
        return extract_datarobot_credential_runtime_param_payload(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def has_aws_credentials(self) -> bool:
        """Check if AWS credentials are configured (either direct or via credential object)."""
        return bool(
            (self.aws_access_key_id and self.aws_secret_access_key)
            or self.aws_credential
        )

    def has_datarobot_credentials(self) -> bool:
        """Check if DataRobot credentials are configured."""
        return bool(self.datarobot.application_api_token)

    def get_aws_credentials(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Get AWS credentials (access_key_id, secret_access_key, session_token).

        If aws_credential dict is set, extracts credentials from it.
        Otherwise, returns the direct environment variable values.

        Returns:
            Tuple of (access_key_id, secret_access_key, session_token)
        """
        # If credentials are provided directly (local development), use them
        if self.aws_access_key_id and self.aws_secret_access_key:
            return (
                self.aws_access_key_id,
                self.aws_secret_access_key,
                self.aws_session_token,
            )

        # If credential object is provided, extract keys from it
        if self.aws_credential:
            try:
                return (
                    self.aws_credential.get("awsAccessKeyId"),
                    self.aws_credential.get("awsSecretAccessKey"),
                    self.aws_credential.get("awsSessionToken"),
                )
            except Exception as e:
                import logging

                logging.getLogger(__name__).warning(
                    f"Failed to extract AWS credentials from credential object: {e}"
                )
                return (None, None, None)

        return (None, None, None)


# Global credentials instance
_credentials: Optional[MCPServerCredentials] = None


def get_credentials() -> MCPServerCredentials:
    """Get the global credentials instance."""
    global _credentials
    if _credentials is None:
        _credentials = MCPServerCredentials()
    return _credentials
