#!/usr/bin/env python3
"""
JWT Key Generator for Demo Project

This script generates secure JWT keys in the proper JWK format.
Run this script to generate new JWT keys for your .env file.
"""

import json
import secrets
import base64

def generate_jwt_key():
    """Generate a secure JWT key in JWK format"""
    # Generate 256-bit (32 bytes) random key
    key_bytes = secrets.token_bytes(32)
    # Base64 URL-safe encode without padding
    key_b64 = base64.urlsafe_b64encode(key_bytes).decode('utf-8').rstrip('=')
    
    # Return JWK format
    return {
        "k": key_b64,
        "kty": "oct"
    }

def main():
    """Generate and display JWT keys"""
    print("🔐 JWT Key Generator for Demo Project")
    print("=" * 50)
    
    # Generate keys
    jwt_key = generate_jwt_key()
    access_jwt_key = generate_jwt_key()
    refresh_jwt_key = generate_jwt_key()
    
    print("\n📋 Add these to your .env file:")
    print("-" * 30)
    print(f'JWT_KEY={json.dumps(jwt_key)}')
    print(f'ACCESS_JWT_KEY={json.dumps(access_jwt_key)}')
    print(f'REFRESH_JWT_KEY={json.dumps(refresh_jwt_key)}')
    
    print("\n⚠️  Security Notes:")
    print("- Keep these keys secret and secure")
    print("- Use different keys for different environments")
    print("- Regenerate keys if compromised")
    print("- Never commit keys to version control")

if __name__ == "__main__":
    main()