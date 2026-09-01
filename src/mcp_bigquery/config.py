"""Configuration management for MCP BigQuery Server."""

import logging
from pathlib import Path
from typing import Optional
import sys
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,  # Ignore if .env file doesn't exist
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    # Authentication
    jwt_public_key_path: Optional[Path] = Field(
        None,
        description="JWT public key file",
    )
    jwt_issuer: str = Field(
        ...,
        min_length=1,
        description="JWT issuer",
    )
    jwt_audience: str = Field(
        ...,
        min_length=1,
        description="JWT audience",
    )

    # Google Cloud Configuration
    google_application_credentials: Path = Field(
        ...,
        description="Path to Google Cloud service account JSON key file",
    )
    gcp_project_id: str = Field(
        ...,
        min_length=1,
        description="Google Cloud Project ID",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Optional MongoDB via SSH tunnel (leave MONGO_SSH_HOST unset to disable)
    mongo_ssh_host: str | None = Field(
        default=None,
        description="SSH host for the Mongo tunnel (e.g. api.projectsuite.io)",
    )
    mongo_ssh_username: str = Field(
        default="suite",
        min_length=1,
        description="SSH username for the Mongo tunnel",
    )
    mongo_ssh_pkey: Path = Field(
        default=Path("~/.ssh/id_rsa"),
        description="SSH private key path for the Mongo tunnel",
    )
    mongo_ssh_key_password: str | None = Field(
        default=None,
        validation_alias=AliasChoices("MONGO_SSH_KEY_PASSWORD", "SSH_KEY_PASSWORD"),
        description="Passphrase for the SSH private key",
    )
    mongo_default_database: str = Field(
        default="prelisting",
        min_length=1,
        description="Default Mongo database for tools when none is passed",
    )
    mongo_allowed_databases: str = Field(
        default="prelisting",
        description="Comma-separated allowlist of Mongo databases",
    )
    mongo_query_timeout_ms: int = Field(
        default=30_000,
        ge=1,
        le=300_000,
        description="maxTimeMS applied to Mongo find and count",
    )

    # Optional Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, ge=1, le=65535, description="Server port")

    @property
    def allowed_mongo_databases(self) -> tuple[str, ...]:
        """Parsed, stripped database allowlist."""
        names = tuple(
            part.strip() for part in self.mongo_allowed_databases.split(",") if part.strip()
        )
        return names or ("prelisting",)

    @field_validator("google_application_credentials")
    @classmethod
    def validate_credentials_file(cls, v: Path) -> Path:
        """Validate that the credentials file exists and is readable."""
        if not v.exists():
            raise ValueError(f"Credentials file not found: {v}")
        if not v.is_file():
            raise ValueError(f"Credentials path is not a file: {v}")
        if not v.suffix == ".json":
            raise ValueError(f"Credentials file must be a JSON file: {v}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that log level is a valid logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper

    def configure_logging(self) -> None:
        """Configure application logging based on settings."""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore
        _settings.configure_logging()
    return _settings
