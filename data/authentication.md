# Authentication and OAuth Configuration

## Overview

The OmniCorp platform supports OAuth 2.0 for secure customer access. Customer Success Managers should use this document when onboarding new clients or troubleshooting authentication issues.

## OAuth Setup

To enable OAuth, configure the client ID, client secret, authorization endpoint, token endpoint, and redirect URI in the tenant settings page. The system expects HTTPS redirect URLs and a valid callback registration.

## Best Practices

- Store secrets in the secret manager.
- Rotate credentials every 90 days.
- Validate the audience claim before granting access.
