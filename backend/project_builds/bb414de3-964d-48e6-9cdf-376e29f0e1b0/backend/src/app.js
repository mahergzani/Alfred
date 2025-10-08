const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const connectDB = require('./config/db');
const apiRoutes = require('./routes/index');

const app = express();

// Security Middleware: Helmet helps secure Express apps by setting various HTTP headers.
app.use(helmet());

// Logging Middleware: Morgan for logging HTTP requests. 'dev' is a concise output colored by response status.
if (process.env.NODE_ENV === 'development') {
    app.use(morgan('dev'));
} else {
    // For production, a more structured logger or a less verbose morgan format might be preferred.
    app.use(morgan('combined'));
}


// CORS Middleware: Enable Cross-Origin Resource Sharing.
// In production, restrict 'origin' to your frontend's domain(s) for security.
const corsOptions = {
    origin: process.env.CORS_ORIGIN ? process.env.CORS_ORIGIN.split(',') : ['http://localhost:3000'], // Allows multiple origins from env
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
    credentials: true, // Allow cookies to be sent
    optionsSuccessStatus: 204
};
app.use(cors(corsOptions));

// Body Parsing Middleware: Parse incoming request bodies in a middleware before your handlers.
// Parses JSON payloads.
app.use(express.json());
// Parses URL-encoded payloads (e.g., from HTML forms).
app.use(express.urlencoded({ extended: true }));

// Establish Database Connection
connectDB();

// Register API Routes
app.use('/api/v1', apiRoutes); // All API routes will be prefixed with /api/v1

// Basic route for health check or root access
app.get('/', (req, res) => {
    res.status(200).json({ message: 'Welcome to the API! Visit /api/v1 for available endpoints.' });
});

// Error Handling Middleware:
// 1. 404 Not Found Middleware
app.use((req, res, next) => {
    const error = new Error(`Not Found - ${req.originalUrl}`);
    res.status(404);
    next(error); // Pass the error to the next error handling middleware
});

// 2. General Error Handling Middleware
app.use((err, req, res, next) => {
    // Determine the status code; if it's 200 (OK), it means an error occurred but
    // was not explicitly set with an error status code, so default to 500.
    const statusCode = res.statusCode === 200 ? 500 : res.statusCode;
    res.status(statusCode);

    res.json({
        message: err.message,
        // In production, do not send stack traces to the client for security reasons.
        stack: process.env.NODE_ENV === 'production' ? '🥞' : err.stack,
    });
});

module.exports = app;