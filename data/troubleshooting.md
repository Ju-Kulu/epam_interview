# Troubleshooting Common Configuration Issues

## Overview

This document helps teams resolve common onboarding and configuration failures. Most problems are caused by mismatched credentials, expired tokens, or invalid endpoint configuration.

## Common Symptoms

- Login failures after a certificate rotation
- Repeated webhook 401 responses
- Incomplete sync jobs for third-party systems

## Resolution Steps

1. Confirm the environment name matches the tenant configuration.
2. Recheck API keys and secret values.
3. Validate callback URLs and token scopes.
4. Re-run the connectivity test before publishing changes.
