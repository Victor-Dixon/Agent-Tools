/**
 * File path validation utility to prevent path traversal attacks
 * 
 * This module provides secure file path validation by:
 * 1. Resolving paths to absolute paths
 * 2. Checking against allowed base directories
 * 3. Preventing directory traversal attacks
 * 4. Validating file extensions (optional)
 */

const path = require('path');
const fs = require('fs');

/**
 * Default allowed base directories for file operations
 * Can be overridden via environment variable ALLOWED_FILE_PATHS
 */
const DEFAULT_ALLOWED_PATHS = [
  process.env.HOME + '/Development',
  process.env.HOME + '/Projects'
];

/**
 * Maximum file size allowed (10MB default)
 */
const MAX_FILE_SIZE = parseInt(process.env.MAX_FILE_SIZE || '10485760', 10); // 10MB

/**
 * Allowed file extensions for task list imports
 */
const ALLOWED_EXTENSIONS = ['.md', '.txt', '.markdown'];

/**
 * Validates a file path to prevent path traversal attacks
 * 
 * @param {string} filePath - The file path to validate
 * @param {string[]} allowedBasePaths - Array of allowed base directory paths (optional)
 * @param {boolean} checkExtension - Whether to validate file extension (default: true)
 * @returns {Object} Validation result with { valid: boolean, resolvedPath: string, error: string }
 */
function validateFilePath(filePath, allowedBasePaths = null, checkExtension = true) {
  // Input validation
  if (!filePath || typeof filePath !== 'string') {
    return {
      valid: false,
      resolvedPath: null,
      error: 'File path must be a non-empty string'
    };
  }

  // Get allowed paths from parameter or environment or defaults
  const allowedPaths = allowedBasePaths || 
    (process.env.ALLOWED_FILE_PATHS ? process.env.ALLOWED_FILE_PATHS.split(',') : null) ||
    DEFAULT_ALLOWED_PATHS;

  // Resolve to absolute path to prevent relative path attacks
  let resolvedPath;
  try {
    resolvedPath = path.resolve(filePath);
  } catch (error) {
    return {
      valid: false,
      resolvedPath: null,
      error: `Invalid file path: ${error.message}`
    };
  }

  // Normalize the path (removes .. and . segments)
  resolvedPath = path.normalize(resolvedPath);

  // SECURITY: Check if resolved path is within any allowed base directory FIRST
  // This must be done BEFORE any file system access to prevent path traversal attacks
  const isWithinAllowed = allowedPaths.some(allowed => {
    const resolvedAllowed = path.resolve(allowed);
    // Check if paths are exactly the same (directory itself - will be rejected later as directory)
    if (resolvedPath === resolvedAllowed) {
      return true; // Allow through for directory check, but will reject as directory later
    }
    // Ensure the resolved path is within the allowed directory
    // Use path.relative to check if path is within allowed directory
    const relative = path.relative(resolvedAllowed, resolvedPath);
    // Path is within allowed if relative doesn't start with .. and is not absolute
    return relative && !relative.startsWith('..') && !path.isAbsolute(relative);
  });

  if (!isWithinAllowed) {
    return {
      valid: false,
      resolvedPath: null,
      error: `File path is outside allowed directories. Allowed: ${allowedPaths.join(', ')}`
    };
  }

  // Now safe to access file system (path is validated to be within allowed directories)
  let stats;
  try {
    stats = fs.statSync(resolvedPath);
  } catch (error) {
    if (error.code === 'ENOENT') {
      return {
        valid: false,
        resolvedPath: null,
        error: 'File does not exist'
      };
    }
    return {
      valid: false,
      resolvedPath: null,
      error: `Error accessing file: ${error.message}`
    };
  }

  // Check if it's a directory (must be a file, not a directory)
  if (!stats.isFile()) {
    return {
      valid: false,
      resolvedPath: null,
      error: 'Path points to a directory, not a file'
    };
  }

  // Check file extension if required
  if (checkExtension) {
    const ext = path.extname(resolvedPath).toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return {
        valid: false,
        resolvedPath: null,
        error: `File extension not allowed. Allowed extensions: ${ALLOWED_EXTENSIONS.join(', ')}`
      };
    }
  }

  // Check file size
  if (stats.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      resolvedPath: null,
      error: `File size exceeds maximum allowed size of ${MAX_FILE_SIZE} bytes`
    };
  }


  return {
    valid: true,
    resolvedPath: resolvedPath,
    error: null
  };
}

/**
 * Validates multiple file paths
 * 
 * @param {string[]} filePaths - Array of file paths to validate
 * @param {string[]} allowedBasePaths - Array of allowed base directory paths (optional)
 * @returns {Object} Validation result with { valid: boolean, results: Array, errors: Array }
 */
function validateFilePaths(filePaths, allowedBasePaths = null) {
  if (!Array.isArray(filePaths)) {
    return {
      valid: false,
      results: [],
      errors: ['filePaths must be an array']
    };
  }

  const results = [];
  const errors = [];
  let allValid = true;

  for (const filePath of filePaths) {
    const validation = validateFilePath(filePath, allowedBasePaths);
    results.push({
      path: filePath,
      ...validation
    });

    if (!validation.valid) {
      allValid = false;
      errors.push(`${filePath}: ${validation.error}`);
    }
  }

  return {
    valid: allValid,
    results: results,
    errors: errors
  };
}

module.exports = {
  validateFilePath,
  validateFilePaths,
  DEFAULT_ALLOWED_PATHS,
  MAX_FILE_SIZE,
  ALLOWED_EXTENSIONS
};

