import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import morgan from 'morgan';
import githubRouter from './routes/github.js';

// Load environment configurations
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Enable CORS for connection with the React/Tailwind frontend
app.use(cors({
  origin: '*', // For local testing
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type']
}));

// Setup json payload and logger middlewares
app.use(express.json());
app.use(morgan('dev'));

// Register secure manual-first routing paths
app.use('/api/github', githubRouter);

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    status: 'operational',
    repository: `${process.env.GITHUB_OWNER}/${process.env.GITHUB_REPO}`
  });
});

// Primary global error handler middleware
app.use((err, req, res, next) => {
  console.error('[SERVER ERROR]', err);
  res.status(500).json({
    success: false,
    message: err.message || 'An internal server error occurred.'
  });
});

// Startup listening port binding
app.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(` STRICT MANUAL-FIRST GITHUB CONTROL CENTER ACTIVE`);
  console.log(` Running on Port: http://localhost:${PORT}`);
  console.log(` Target Owner:   ${process.env.GITHUB_OWNER}`);
  console.log(` Target Repo:    ${process.env.GITHUB_REPO}`);
  console.log(`=======================================================`);
});
