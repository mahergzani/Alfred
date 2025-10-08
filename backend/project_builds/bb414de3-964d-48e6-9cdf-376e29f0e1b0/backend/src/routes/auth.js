const express = require('express');
const { body } = require('express-validator');
const authController = require('../controllers/authController');
const { loginLimiter, registerLimiter, refreshTokenLimiter, socialLoginLimiter } = require('../middleware/rateLimiter');
const validateRequest = require('../middleware/validateRequest');

const router = express.Router();

// Registration route
router.post(
  '/register',
  registerLimiter, // Apply rate limiting to registration
  [
    body('email', 'Please include a valid email').isEmail().normalizeEmail(),
    body('password', 'Please enter a password with 8 or more characters, including uppercase, lowercase, numbers, and special characters')
      .isLength({ min: 8 })
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).*$/),
  ],
  validateRequest,
  authController.register
);

// Email/Password Login route
router.post(
  '/login',
  loginLimiter, // Apply rate limiting to login
  [
    body('email', 'Please include a valid email').isEmail().normalizeEmail(),
    body('password', 'Password is required').not().isEmpty(), // Ensure password is not empty
  ],
  validateRequest,
  authController.login
);

// Social Login route (e.g., Google, Facebook)
router.post(
  '/social-login',
  socialLoginLimiter, // Apply rate limiting to social login
  [
    body('token', 'Social authentication token is required').not().isEmpty(),
    body('provider', 'Social provider is required').isIn(['google', 'facebook']).not().isEmpty(),
  ],
  validateRequest,
  authController.socialLogin
);

// Token Refresh route
router.post(
  '/refresh-token',
  refreshTokenLimiter, // Apply rate limiting to refresh token
  [
    body('refreshToken', 'Refresh token is required').not().isEmpty(),
  ],
  validateRequest,
  authController.refreshToken
);

module.exports = router;