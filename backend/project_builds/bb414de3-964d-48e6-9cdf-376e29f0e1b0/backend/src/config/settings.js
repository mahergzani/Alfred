/**
 * @fileoverview Configuration settings for environment variables.
 * This file centralizes access to environment variables, providing default values for development
 * and ensuring required variables are clearly defined.
 *
 * IMPORTANT: In production environments, these variables MUST be set via environment variables
 * and not hardcoded here. Use robust methods for secret management (e.g., AWS Secrets Manager,
 * Azure Key Vault, Google Secret Manager, Kubernetes Secrets) instead of .env files in production.
 */

require('dotenv').config(); // Ensure dotenv is loaded to access .env file variables

module.exports = {
  /**
   * Application Environment Settings
   */
  NODE_ENV: process.env.NODE_ENV || 'development',
  PORT: parseInt(process.env.PORT || '3000', 10),

  /**
   * Database Connection Settings (e.g., PostgreSQL, MongoDB)
   * Example for PostgreSQL:
   */
  DATABASE: {
    HOST: process.env.DB_HOST || 'localhost',
    PORT: parseInt(process.env.DB_PORT || '5432', 10),
    USER: process.env.DB_USER || 'user',
    PASSWORD: process.env.DB_PASSWORD || 'password',
    NAME: process.env.DB_NAME || 'docudex_db',
    SSL_ENABLED: process.env.DB_SSL_ENABLED === 'true',
    // Additional settings like `URL` can be added if preferred for ORMs
    // URL: process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/docudex_db',
  },

  /**
   * JSON Web Token (JWT) Secret Keys
   * These keys are critical for signing and verifying JWTs.
   * MUST be long, random, and kept secret.
   * Use separate keys for access and refresh tokens to enhance security.
   */
  JWT: {
    ACCESS_SECRET: process.env.JWT_ACCESS_SECRET || 'supersecretaccesskeyforlocaldevchangeintoprod!',
    REFRESH_SECRET: process.env.JWT_REFRESH_SECRET || 'evenmoresecretrefreshkeyforlocaldevchangeintoprod!!',
    ACCESS_TOKEN_EXPIRES_IN: process.env.JWT_ACCESS_TOKEN_EXPIRES_IN || '15m', // e.g., '15m', '1h', '7d'
    REFRESH_TOKEN_EXPIRES_IN: process.env.JWT_REFRESH_TOKEN_EXPIRES_IN || '7d', // e.g., '7d', '30d'
  },

  /**
   * Social Login Credentials
   * Client IDs and Secrets for OAuth providers.
   * Redirect URIs should also be configured with the providers.
   */
  SOCIAL_LOGIN: {
    GOOGLE: {
      CLIENT_ID: process.env.GOOGLE_CLIENT_ID || 'your-google-client-id-for-dev',
      CLIENT_SECRET: process.env.GOOGLE_CLIENT_SECRET || 'your-google-client-secret-for-dev',
      REDIRECT_URI: process.env.GOOGLE_REDIRECT_URI || 'http://localhost:3000/api/auth/google/callback',
    },
    APPLE: {
      CLIENT_ID: process.env.APPLE_CLIENT_ID || 'your-apple-client-id-for-dev',
      TEAM_ID: process.env.APPLE_TEAM_ID || 'your-apple-team-id-for-dev', // Required for generating client secret
      KEY_ID: process.env.APPLE_KEY_ID || 'your-apple-key-id-for-dev', // Required for generating client secret
      PRIVATE_KEY: process.env.APPLE_PRIVATE_KEY ? Buffer.from(process.env.APPLE_PRIVATE_KEY, 'base64').toString('utf8') : 'your-apple-private-key-content-for-dev', // Base64 encoded private key
      REDIRECT_URI: process.env.APPLE_REDIRECT_URI || 'http://localhost:3000/api/auth/apple/callback',
    },
    MICROSOFT: {
      CLIENT_ID: process.env.MICROSOFT_CLIENT_ID || 'your-microsoft-client-id-for-dev',
      CLIENT_SECRET: process.env.MICROSOFT_CLIENT_SECRET || 'your-microsoft-client-secret-for-dev',
      REDIRECT_URI: process.env.MICROSOFT_REDIRECT_URI || 'http://localhost:3000/api/auth/microsoft/callback',
    },
    // Add other social providers as needed (e.g., GitHub, Facebook)
  },

  /**
   * External API Keys
   * Keys for third-party services like OCR and Calendar integration.
   */
  EXTERNAL_APIS: {
    OCR: {
      // Example: Google Cloud Vision API, AWS Textract, Tesseract
      API_KEY: process.env.OCR_API_KEY || 'your-ocr-service-api-key-for-dev',
      ENDPOINT: process.env.OCR_API_ENDPOINT || 'https://vision.googleapis.com/v1/images:annotate', // Example for Google Vision
      // If using a specific cloud provider's SDK, credentials might be handled differently (e.g., service account keys)
      // GOOGLE_SERVICE_ACCOUNT_KEY: process.env.GOOGLE_SERVICE_ACCOUNT_KEY ? JSON.parse(Buffer.from(process.env.GOOGLE_SERVICE_ACCOUNT_KEY, 'base64').toString('utf8')) : null,
    },
    CALENDAR: {
      // Example: Google Calendar API, Microsoft Graph Calendar API
      API_KEY: process.env.CALENDAR_API_KEY || 'your-calendar-service-api-key-for-dev',
      // For user-based calendar access (e.g., OAuth), this might be handled via social login credentials and user tokens.
      // The API_KEY here might be for service-level access if applicable.
    },
    // Add other external APIs as needed
  },

  /**
   * Security & Rate Limiting
   */
  RATE_LIMIT_WINDOW_MS: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000', 10), // 1 minute
  RATE_LIMIT_MAX_REQUESTS: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100', 10), // Max 100 requests per window

  /**
   * CORS Settings
   */
  CORS_ORIGIN: process.env.CORS_ORIGIN || 'http://localhost:3001', // Your frontend URL(s)
};