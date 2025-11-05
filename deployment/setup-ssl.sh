#!/bin/bash

# SSL Certificate Generation Script
# Generates self-signed certificates for testing/development
# For production, use proper certificates from Let's Encrypt or commercial CA

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSL_DIR="$SCRIPT_DIR/nginx/ssl"

echo "🔐 SSL Certificate Setup for Test Case API"
echo "=========================================="

# Create SSL directory
mkdir -p "$SSL_DIR"

echo ""
echo "Select certificate type:"
echo "1) Self-signed certificate (for testing/development)"
echo "2) Let's Encrypt certificate (for production)"
echo "3) Use existing certificates"
read -p "Enter choice (1-3): " CERT_CHOICE

case $CERT_CHOICE in
    1)
        echo ""
        echo "📝 Generating self-signed certificate..."
        read -p "Enter domain name (or press Enter for 'localhost'): " DOMAIN
        DOMAIN=${DOMAIN:-localhost}
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$SSL_DIR/key.pem" \
            -out "$SSL_DIR/cert.pem" \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
        
        echo "✅ Self-signed certificate generated!"
        echo "⚠️  WARNING: Self-signed certificates should only be used for testing!"
        ;;
    
    2)
        echo ""
        echo "📝 Setting up Let's Encrypt certificate..."
        read -p "Enter your domain name: " DOMAIN
        read -p "Enter your email address: " EMAIL
        
        if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
            echo "❌ Domain and email are required for Let's Encrypt"
            exit 1
        fi
        
        echo ""
        echo "Installing Certbot..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y certbot
        elif command -v yum &> /dev/null; then
            sudo yum install -y certbot
        else
            echo "❌ Please install certbot manually"
            exit 1
        fi
        
        echo ""
        echo "Obtaining certificate from Let's Encrypt..."
        echo "⚠️  Make sure port 80 is accessible and pointing to this server!"
        read -p "Press Enter to continue..."
        
        sudo certbot certonly --standalone -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
        
        # Copy certificates
        sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
        sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"
        sudo chown $(whoami):$(whoami) "$SSL_DIR/cert.pem" "$SSL_DIR/key.pem"
        
        echo "✅ Let's Encrypt certificate installed!"
        echo "📝 Certificate renewal: certbot renew"
        ;;
    
    3)
        echo ""
        echo "📁 Using existing certificates..."
        read -p "Enter path to certificate file (.pem or .crt): " CERT_PATH
        read -p "Enter path to private key file (.pem or .key): " KEY_PATH
        
        if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
            echo "❌ Certificate or key file not found"
            exit 1
        fi
        
        cp "$CERT_PATH" "$SSL_DIR/cert.pem"
        cp "$KEY_PATH" "$SSL_DIR/key.pem"
        chmod 600 "$SSL_DIR/key.pem"
        
        echo "✅ Certificates copied successfully!"
        ;;
    
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "🔍 Certificate information:"
openssl x509 -in "$SSL_DIR/cert.pem" -text -noout | grep -E "(Subject:|Issuer:|Not Before|Not After)"

echo ""
echo "✅ SSL setup complete!"
echo "Certificate: $SSL_DIR/cert.pem"
echo "Private Key: $SSL_DIR/key.pem"
