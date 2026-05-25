import express from 'express';
import { Octokit } from '@octokit/rest';
import { validateManualControl } from '../middleware/validation.js';
import { logAction, getLogs } from '../utils/logger.js';

const router = express.Router();

// Helper to initialize Octokit with the GITHUB_TOKEN env variable
function getOctokit() {
  const token = process.env.GITHUB_TOKEN;
  if (!token || token.trim() === "") {
    throw new Error("GITHUB_TOKEN is missing or empty in backend environment variables (.env). Please configure your Personal Access Token (PAT).");
  }
  return new Octokit({ auth: token });
}

// Ensure database parameters exist
const getRepoParams = () => {
  return {
    owner: process.env.GITHUB_OWNER || 'anandsinghrathore324-cmyk',
    repo: process.env.GITHUB_REPO || 'Anandsinghrathore-Mental-Health-Monitoring'
  };
};

/**
 * Endpoint to retrieve secure audit log trails for the frontend.
 */
router.get('/logs', (req, res) => {
  try {
    const logs = getLogs();
    res.json({ success: true, logs });
  } catch (error) {
    res.status(500).json({ success: false, message: error.message });
  }
});

/**
 * 1. Post Comment to an Issue or PR
 * Command: "comment on GitHub" or "post this issue reply"
 */
router.post('/comment', validateManualControl, async (req, res) => {
  const { role, details } = req.body;
  const { issueNumber, commentText } = details || {};
  const { owner, repo } = getRepoParams();
  const repository = `${owner}/${repo}`;

  if (!issueNumber || !commentText) {
    return res.status(400).json({
      success: false,
      message: "Required parameters missing: issueNumber and commentText are mandatory."
    });
  }

  try {
    const octokit = getOctokit();
    const response = await octokit.issues.createComment({
      owner,
      repo,
      issue_number: parseInt(issueNumber, 10),
      body: commentText
    });

    logAction(role, 'comment_on_github', repository, { issueNumber, commentText }, true);
    res.json({
      success: true,
      message: `Comment successfully posted on Issue/PR #${issueNumber}!`,
      data: response.data
    });
  } catch (error) {
    logAction(role, 'comment_on_github', repository, { issueNumber, commentText }, false, error.message);
    res.status(error.message.includes("GITHUB_TOKEN") ? 500 : 400).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * 2. Create a new GitHub Issue
 * Command: "create issue"
 */
router.post('/issue', validateManualControl, async (req, res) => {
  const { role, details } = req.body;
  const { title, body, labels } = details || {};
  const { owner, repo } = getRepoParams();
  const repository = `${owner}/${repo}`;

  if (!title) {
    return res.status(400).json({
      success: false,
      message: "Required parameter missing: title is mandatory."
    });
  }

  try {
    const octokit = getOctokit();
    const response = await octokit.issues.create({
      owner,
      repo,
      title,
      body: body || "",
      labels: labels || []
    });

    logAction(role, 'create_issue', repository, { title, body, labels }, true);
    res.json({
      success: true,
      message: `Issue #${response.data.number} created successfully!`,
      data: response.data
    });
  } catch (error) {
    logAction(role, 'create_issue', repository, { title, body, labels }, false, error.message);
    res.status(error.message.includes("GITHUB_TOKEN") ? 500 : 400).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * 3. Push Commit (Creates or updates a file)
 * Command: "push these changes"
 */
router.post('/commit', validateManualControl, async (req, res) => {
  const { role, details } = req.body;
  const { filePath, fileContent, commitMessage, branch } = details || {};
  const { owner, repo } = getRepoParams();
  const repository = `${owner}/${repo}`;

  if (!filePath || !fileContent || !commitMessage) {
    return res.status(400).json({
      success: false,
      message: "Required parameters missing: filePath, fileContent, and commitMessage are mandatory."
    });
  }

  try {
    const octokit = getOctokit();
    const targetBranch = branch || 'main';
    
    // Check if the file exists to get its SHA hash (required for updates)
    let sha = undefined;
    try {
      const existingFile = await octokit.repos.getContent({
        owner,
        repo,
        path: filePath,
        ref: targetBranch
      });
      if (existingFile && !Array.isArray(existingFile.data)) {
        sha = existingFile.data.sha;
      }
    } catch (e) {
      // File doesn't exist, which is fine for creation
    }

    const response = await octokit.repos.createOrUpdateFileContents({
      owner,
      repo,
      path: filePath,
      message: commitMessage,
      content: Buffer.from(fileContent).toString('base64'),
      sha,
      branch: targetBranch
    });

    logAction(role, 'push_commit', repository, { filePath, commitMessage, branch: targetBranch }, true);
    res.json({
      success: true,
      message: `Changes pushed successfully to ${filePath} on branch ${targetBranch}!`,
      data: response.data
    });
  } catch (error) {
    logAction(role, 'push_commit', repository, { filePath, commitMessage, branch: branch || 'main' }, false, error.message);
    res.status(error.message.includes("GITHUB_TOKEN") ? 500 : 400).json({
      success: false,
      message: error.message
    });
  }
});

/**
 * 4. Add Review Comment on a Pull Request (PR)
 * Command: "create PR comment"
 */
router.post('/pr-comment', validateManualControl, async (req, res) => {
  const { role, details } = req.body;
  const { prNumber, commentText } = details || {};
  const { owner, repo } = getRepoParams();
  const repository = `${owner}/${repo}`;

  if (!prNumber || !commentText) {
    return res.status(400).json({
      success: false,
      message: "Required parameters missing: prNumber and commentText are mandatory."
    });
  }

  try {
    const octokit = getOctokit();
    // PR comments can be added as general comments under the PR's issue thread
    const response = await octokit.issues.createComment({
      owner,
      repo,
      issue_number: parseInt(prNumber, 10),
      body: commentText
    });

    logAction(role, 'pr_comment', repository, { prNumber, commentText }, true);
    res.json({
      success: true,
      message: `Pull Request Comment successfully posted on PR #${prNumber}!`,
      data: response.data
    });
  } catch (error) {
    logAction(role, 'pr_comment', repository, { prNumber, commentText }, false, error.message);
    res.status(error.message.includes("GITHUB_TOKEN") ? 500 : 400).json({
      success: false,
      message: error.message
    });
  }
});

export default router;
