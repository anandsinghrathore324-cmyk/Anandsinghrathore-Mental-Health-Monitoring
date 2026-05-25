import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const LOG_DIR = path.join(__dirname, '../logs');
const LOG_FILE = path.join(LOG_DIR, 'audit-actions.log');

// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

/**
 * Appends a structured audit entry to the log file.
 * @param {string} operator - The username or role who triggered the action.
 * @param {string} actionType - The type of action (e.g. comment_on_github, create_issue, push_commit).
 * @param {string} repository - The repository affected.
 * @param {object} details - Additional contextual details.
 * @param {boolean} success - Whether the operation succeeded.
 * @param {string} error - Error message, if failed.
 */
export function logAction(operator, actionType, repository, details = {}, success = true, error = '') {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    operator,
    actionType,
    repository,
    details,
    success,
    error: error || null
  };

  const logString = JSON.stringify(logEntry) + '\n';
  
  try {
    fs.appendFileSync(LOG_FILE, logString, 'utf8');
    console.log(`[AUDIT LOG] Action: ${actionType} | Operator: ${operator} | Success: ${success}`);
  } catch (err) {
    console.error('Failed to write audit log:', err);
  }
}

/**
 * Reads and parses the list of recent audit logs.
 * @returns {Array<object>} Array of log objects.
 */
export function getLogs() {
  if (!fs.existsSync(LOG_FILE)) {
    return [];
  }
  
  try {
    const rawContent = fs.readFileSync(LOG_FILE, 'utf8').trim();
    if (!rawContent) return [];
    
    return rawContent
      .split('\n')
      .map(line => {
        try {
          return JSON.parse(line);
        } catch {
          return null;
        }
      })
      .filter(entry => entry !== null);
  } catch (err) {
    console.error('Failed to read audit logs:', err);
    return [];
  }
}
