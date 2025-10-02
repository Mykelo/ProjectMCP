#!/usr/bin/env python3
"""Script to generate JWT tokens for testing FastMCP server authentication."""

import os
from pathlib import Path
from typing import Optional

import typer
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv
from fastmcp.server.auth.providers.jwt import RSAKeyPair, SecretStr

load_dotenv()

app = typer.Typer(
    help="Generate JWT tokens for testing FastMCP server authentication",
    rich_markup_mode="rich",
)


@app.command()
def generate_keys(
    public_key_file: Path = typer.Option(
        "credentials/public_key.pem",
        "--public-key-file",
        "-k",
        help="Path to save the RSA public key (PEM format)",
    ),
    private_key_file: Path = typer.Option(
        "credentials/private_key.pem",
        "--private-key-file",
        help="Path to save the RSA private key (PEM format) - [red]WARNING: Never use in production![/red]",
    ),
) -> None:
    """Generate RSA key pair for JWT authentication."""
    typer.echo("Generating RSA key pair for JWT authentication...")

    # Generate a key pair for testing
    key_pair = RSAKeyPair.generate()
    typer.secho("✓ RSA key pair generated", fg=typer.colors.GREEN)

    # Save public key to file
    try:
        public_key_file.parent.mkdir(parents=True, exist_ok=True)
        public_key_file.write_text(key_pair.public_key)
        typer.secho(f"✓ Public key saved to: {public_key_file}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"✗ Failed to save public key: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    # Save private key to file (WARNING: Never use in production!)
    try:
        private_key_file.parent.mkdir(parents=True, exist_ok=True)
        private_key_file.write_text(key_pair.private_key.get_secret_value())
        typer.secho(
            f"⚠️  Private key saved to: {private_key_file} (FOR TESTING ONLY)",
            fg=typer.colors.YELLOW,
        )
    except Exception as e:
        typer.secho(f"✗ Failed to save private key: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    typer.secho(
        "⚠️  WARNING: This private key can be used to sign tokens - NEVER use in production!",
        fg=typer.colors.YELLOW,
    )


@app.command()
def generate_token(
    private_key_file: Path = typer.Option(
        "credentials/private_key.pem",
        "--private-key-file",
        "-k",
        help="Path to the RSA private key file (PEM format)",
        exists=True,
    ),
    token_file: Optional[Path] = typer.Option(
        "credentials/token.txt",
        "--token-file",
        "-t",
        help="Path to save the JWT token (plain text)",
    ),
    subject: str = typer.Option(
        "ProjectMCP",
        "--subject",
        "-s",
        help="JWT token subject",
    ),
    issuer: Optional[str] = typer.Option(
        None,
        "--issuer",
        "-i",
        help="JWT token issuer (defaults to JWT_ISSUER environment variable)",
    ),
    audience: Optional[str] = typer.Option(
        None,
        "--audience",
        "-a",
        help="JWT token audience (defaults to JWT_AUDIENCE environment variable)",
    ),
    scopes: Optional[str] = typer.Option(
        "read,write,admin",
        "--scopes",
        help="Comma-separated list of JWT token scopes",
    ),
) -> None:
    """Generate JWT token using existing RSA private key."""
    typer.echo("Generating JWT token using existing private key...")

    # Read private key from file
    try:
        private_key_pem = private_key_file.read_text()
    except Exception as e:
        typer.secho(f"✗ Failed to read private key: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    # Load and parse the private key to extract public key
    try:
        # Load the private key using cryptography
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode(),
            password=None,
        )

        # Extract and serialize public key
        public_pem = (
            private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8")
        )

        # Create RSAKeyPair using the original private key PEM and extracted public key
        key_pair = RSAKeyPair(
            private_key=SecretStr(private_key_pem),
            public_key=public_pem,
        )
        typer.secho("✓ Private key loaded", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"✗ Failed to load private key: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    # Get issuer and audience from parameters or environment
    jwt_issuer = issuer or os.getenv("JWT_ISSUER")
    jwt_audience = audience or os.getenv("JWT_AUDIENCE")

    if not jwt_issuer:
        typer.secho(
            "✗ JWT_ISSUER not provided via --issuer or environment variable",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    if not jwt_audience:
        typer.secho(
            "✗ JWT_AUDIENCE not provided via --audience or environment variable",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    typer.secho("✓ JWT configuration validated", fg=typer.colors.GREEN)

    # Parse scopes
    scope_list = [s.strip() for s in scopes.split(",") if s.strip()]

    # Generate token
    test_token = key_pair.create_token(
        subject=subject,
        issuer=jwt_issuer,
        audience=jwt_audience,
        scopes=scope_list,
        expires_in_seconds=3600 * 24 * 730,  # 2 years
    )
    typer.secho("✓ JWT token generated", fg=typer.colors.GREEN)

    # Save token to file if requested
    if token_file:
        try:
            token_file.parent.mkdir(parents=True, exist_ok=True)
            token_file.write_text(test_token)
            typer.secho(f"✓ JWT token saved to: {token_file}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"✗ Failed to save JWT token: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

    # Display the token
    typer.echo(f"\n{'=' * 60}")
    typer.secho("JWT TOKEN:", fg=typer.colors.BLUE, bold=True)
    typer.echo(f"{'=' * 60}")
    typer.echo(test_token)
    typer.echo(f"{'=' * 60}")

    # Display token details
    typer.echo("\nToken details:")
    typer.echo(f"- Subject: {subject}")
    typer.echo(f"- Issuer: {jwt_issuer}")
    typer.echo(f"- Audience: {jwt_audience}")
    typer.echo(f"- Scopes: {', '.join(scope_list)}")

    # Display token usage information
    if token_file:
        typer.echo(f"\nJWT token saved to file: {token_file}")
        typer.echo("To use this token, set the Authorization header:")
        typer.echo(f"Authorization: Bearer <contents of {token_file}>")
    else:
        typer.echo("\nTo use this token, set the Authorization header:")
        typer.echo(f"Authorization: Bearer {test_token}")


if __name__ == "__main__":
    app()
