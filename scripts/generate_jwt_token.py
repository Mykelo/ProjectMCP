#!/usr/bin/env python3
"""Script to generate JWT tokens for testing FastMCP server authentication."""

import os
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from fastmcp.server.auth.providers.jwt import RSAKeyPair

load_dotenv()

app = typer.Typer(
    help="Generate JWT tokens for testing FastMCP server authentication",
    rich_markup_mode="rich",
)


@app.command()
def generate(
    public_key_file: Optional[Path] = typer.Option(
        "credentials/public_key.pem",
        "--public-key-file",
        "-k",
        help="Path to save the RSA public key (PEM format)",
    ),
    private_key_file: Optional[Path] = typer.Option(
        "credentials/private_key.pem",
        "--private-key-file",
        help="Path to save the RSA private key (PEM format) - [red]WARNING: Never use in production![/red]",
    ),
    token_file: Optional[Path] = typer.Option(
        "credentials/token.txt",
        "--token-file",
        "-t",
        help="Path to save the JWT token (plain text)",
    ),
) -> None:
    """Generate a test JWT token for MCP server authentication."""
    typer.echo("Generating RSA key pair and JWT token for testing...")

    # Generate a key pair for testing
    key_pair = RSAKeyPair.generate()
    typer.secho("✓ RSA key pair generated", fg=typer.colors.GREEN)

    # Save public key to file if requested
    if public_key_file:
        try:
            public_key_file.write_text(key_pair.public_key)
            typer.secho(f"✓ Public key saved to: {public_key_file}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"✗ Failed to save public key: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

    # Save private key to file if requested (WARNING: Never use in production!)
    if private_key_file:
        try:
            private_key_file.write_text(key_pair.private_key.get_secret_value())
            typer.secho(
                f"⚠️  Private key saved to: {private_key_file} (FOR TESTING ONLY)",
                fg=typer.colors.YELLOW,
            )
        except Exception as e:
            typer.secho(f"✗ Failed to save private key: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

    jwt_issuer = os.getenv("JWT_ISSUER")
    jwt_audience = os.getenv("JWT_AUDIENCE")

    typer.secho("✓ JWTVerifier configured", fg=typer.colors.GREEN)

    # Generate a test token using the private key
    test_token = key_pair.create_token(
        subject="ProjectMCP",
        issuer=jwt_issuer,
        audience=jwt_audience,
        scopes=["read", "write", "admin"],
    )
    typer.secho("✓ Test JWT token generated", fg=typer.colors.GREEN)

    # Save token to file if requested
    if token_file:
        try:
            token_file.write_text(test_token)
            typer.secho(f"✓ JWT token saved to: {token_file}", fg=typer.colors.GREEN)
        except Exception as e:
            typer.secho(f"✗ Failed to save JWT token: {e}", fg=typer.colors.RED, err=True)
            raise typer.Exit(1)

    # Display the token
    typer.echo(f"\n{'=' * 60}")
    typer.secho("TEST JWT TOKEN:", fg=typer.colors.BLUE, bold=True)
    typer.echo(f"{'=' * 60}")
    typer.echo(test_token)
    typer.echo(f"{'=' * 60}")

    # Display token details
    typer.echo("\nToken details:")
    typer.echo(f"- Subject: ProjectMCP")
    typer.echo(f"- Issuer: {jwt_issuer}")
    typer.echo(f"- Audience: {jwt_audience}")
    typer.echo(f"- Scopes: read, write, admin")

    # Display token usage information
    if token_file:
        typer.echo(f"\nJWT token saved to file: {token_file}")
        typer.echo("To use this token, set the Authorization header:")
        typer.echo(f"Authorization: Bearer <contents of {token_file}>")
    else:
        typer.echo("\nTo use this token, set the Authorization header:")
        typer.echo(f"Authorization: Bearer {test_token}")

    # Display or indicate location of public key for server configuration
    if public_key_file:
        typer.echo(f"\nPublic key saved to file: {public_key_file}")
        typer.echo("Use this file for JWT verifier configuration in your server.")
    else:
        typer.echo("\nPublic key for server configuration:")
        typer.echo(key_pair.public_key)

    # Display private key information if saved
    if private_key_file:
        typer.secho(f"\n⚠️  Private key saved to file: {private_key_file}", fg=typer.colors.YELLOW)
        typer.secho(
            "⚠️  WARNING: This private key can be used to sign tokens - NEVER use in production!",
            fg=typer.colors.YELLOW,
        )


if __name__ == "__main__":
    app()
