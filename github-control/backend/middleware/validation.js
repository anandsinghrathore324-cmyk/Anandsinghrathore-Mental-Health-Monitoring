import { logAction } from '../utils/logger.js';

// Approved list of strict explicit commands matching user requirements
const APPROVED_EXPLICIT_COMMANDS = [
  "comment on GitHub",
  "post this issue reply",
  "push these changes",
  "create issue",
  "create PR comment"
];

/**
 * Express middleware to validate manual control execution requirements.
 */
export function validateManualControl(req, res, next) {
  const { command, confirmExplicit, role, details } = req.body;
  const repository = `${process.env.GITHUB_OWNER}/${process.env.GITHUB_REPO}`;

  // 1. Role-Based Safety Check
  const allowedRoles = ["admin", "operator"];
  if (!role || !allowedRoles.includes(role.toLowerCase())) {
    const errorMsg = `Unauthorized Role: '${role}'. Action denied by role-based safety check.`;
    logAction(
      role || 'unknown_user',
      'BLOCKED_ATTEMPT',
      repository,
      { details, command, reason: 'role_violation' },
      false,
      errorMsg
    );
    return res.status(403).json({
      success: false,
      message: errorMsg,
      code: 'ROLE_BLOCKED'
    });
  }

  // 2. Explicit User Command Check
  if (!command || !APPROVED_EXPLICIT_COMMANDS.includes(command)) {
    const errorMsg = `Command rejected: '${command}'. Command must match one of the strict explicit commands.`;
    logAction(
      role,
      'BLOCKED_ATTEMPT',
      repository,
      { details, command, reason: 'command_violation' },
      false,
      errorMsg
    );
    return res.status(400).json({
      success: false,
      message: errorMsg,
      code: 'COMMAND_BLOCKED'
    });
  }

  // 3. Explicit User Confirmation Check
  if (confirmExplicit !== true) {
    const errorMsg = "Action blocked: Missing explicit confirmation parameter.";
    logAction(
      role,
      'BLOCKED_ATTEMPT',
      repository,
      { details, command, reason: 'missing_confirmation' },
      false,
      errorMsg
    );
    return res.status(400).json({
      success: false,
      message: errorMsg,
      code: 'CONFIRMATION_BLOCKED'
    });
  }

  // All manual gates passed! Proceed to execute.
  next();
}
