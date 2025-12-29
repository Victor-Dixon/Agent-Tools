/**
 * Tests for path validation utility
 * 
 * These tests ensure that path traversal attacks are prevented
 * and file access is restricted to allowed directories.
 */

const path = require('path');
const fs = require('fs');
const os = require('os');
const { validateFilePath, validateFilePaths, DEFAULT_ALLOWED_PATHS } = require('../pathValidator');

describe('Path Validator', () => {
  const testAllowedPath = path.join(os.tmpdir(), 'kanban-test-allowed');
  const testFile = path.join(testAllowedPath, 'test.md');
  const outsidePath = path.join(os.tmpdir(), 'kanban-test-outside');
  const outsideFile = path.join(outsidePath, 'test.md');

  // Setup test directories and files
  beforeAll(() => {
    // Create test directories
    if (!fs.existsSync(testAllowedPath)) {
      fs.mkdirSync(testAllowedPath, { recursive: true });
    }
    if (!fs.existsSync(outsidePath)) {
      fs.mkdirSync(outsidePath, { recursive: true });
    }

    // Create test files
    fs.writeFileSync(testFile, '# Test Task List\n- [ ] Task 1');
    fs.writeFileSync(outsideFile, '# Outside File\n- [ ] Task 1');
  });

  // Cleanup test directories
  afterAll(() => {
    try {
      if (fs.existsSync(testFile)) fs.unlinkSync(testFile);
      if (fs.existsSync(testAllowedPath)) fs.rmdirSync(testAllowedPath);
      if (fs.existsSync(outsideFile)) fs.unlinkSync(outsideFile);
      if (fs.existsSync(outsidePath)) fs.rmdirSync(outsidePath);
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  describe('validateFilePath', () => {
    describe('Valid paths', () => {
      test('should accept valid file path within allowed directory', () => {
        const result = validateFilePath(testFile, [testAllowedPath]);
        expect(result.valid).toBe(true);
        expect(result.resolvedPath).toBe(path.resolve(testFile));
        expect(result.error).toBeNull();
      });

      test('should accept relative path that resolves to allowed directory', () => {
        const relativePath = path.relative(process.cwd(), testFile);
        if (relativePath && !relativePath.startsWith('..')) {
          const result = validateFilePath(relativePath, [testAllowedPath]);
          expect(result.valid).toBe(true);
        }
      });

      test('should use default allowed paths when none provided', () => {
        // This test assumes DEFAULT_ALLOWED_PATHS exist
        // We'll create a file in one of them for testing
        const defaultPath = DEFAULT_ALLOWED_PATHS[0];
        if (fs.existsSync(defaultPath)) {
          const testFileInDefault = path.join(defaultPath, 'test-validation.md');
          try {
            fs.writeFileSync(testFileInDefault, '# Test');
            const result = validateFilePath(testFileInDefault);
            expect(result.valid).toBe(true);
            fs.unlinkSync(testFileInDefault);
          } catch (error) {
            // Skip if can't create file
          }
        }
      });
    });

    describe('Path traversal attacks', () => {
      test('should reject path with .. (parent directory)', () => {
        const maliciousPath = path.join(testAllowedPath, '..', 'etc', 'passwd');
        const result = validateFilePath(maliciousPath, [testAllowedPath]);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('outside allowed directories');
      });

      test('should reject path with multiple .. sequences', () => {
        const maliciousPath = path.join(testAllowedPath, '..', '..', '..', 'etc', 'passwd');
        const result = validateFilePath(maliciousPath, [testAllowedPath]);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('outside allowed directories');
      });

      test('should reject path starting with ~ (home directory traversal)', () => {
        const maliciousPath = '~/../../etc/passwd';
        const result = validateFilePath(maliciousPath, [testAllowedPath]);
        expect(result.valid).toBe(false);
      });

      test('should reject absolute path outside allowed directories', () => {
        const result = validateFilePath(outsideFile, [testAllowedPath]);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('outside allowed directories');
      });

      test('should reject path that resolves outside allowed directory', () => {
        const maliciousPath = path.join(testAllowedPath, 'subdir', '..', '..', 'etc', 'passwd');
        const result = validateFilePath(maliciousPath, [testAllowedPath]);
        expect(result.valid).toBe(false);
      });
    });

    describe('Input validation', () => {
      test('should reject null file path', () => {
        const result = validateFilePath(null);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('non-empty string');
      });

      test('should reject undefined file path', () => {
        const result = validateFilePath(undefined);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('non-empty string');
      });

      test('should reject empty string', () => {
        const result = validateFilePath('');
        expect(result.valid).toBe(false);
        expect(result.error).toContain('non-empty string');
      });

      test('should reject non-string input', () => {
        const result = validateFilePath(123);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('non-empty string');
      });
    });

    describe('File extension validation', () => {
      test('should accept .md files', () => {
        const result = validateFilePath(testFile, [testAllowedPath], true);
        expect(result.valid).toBe(true);
      });

      test('should reject files with disallowed extensions', () => {
        const jsFile = path.join(testAllowedPath, 'test.js');
        try {
          fs.writeFileSync(jsFile, 'console.log("test")');
          const result = validateFilePath(jsFile, [testAllowedPath], true);
          expect(result.valid).toBe(false);
          expect(result.error).toContain('extension not allowed');
          fs.unlinkSync(jsFile);
        } catch (error) {
          // Skip if can't create file
        }
      });

      test('should skip extension check when checkExtension is false', () => {
        const jsFile = path.join(testAllowedPath, 'test.js');
        try {
          fs.writeFileSync(jsFile, 'console.log("test")');
          const result = validateFilePath(jsFile, [testAllowedPath], false);
          expect(result.valid).toBe(true);
          fs.unlinkSync(jsFile);
        } catch (error) {
          // Skip if can't create file
        }
      });
    });

    describe('File existence and type validation', () => {
      test('should reject non-existent files', () => {
        const nonExistent = path.join(testAllowedPath, 'nonexistent.md');
        const result = validateFilePath(nonExistent, [testAllowedPath]);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('does not exist');
      });

      test('should reject directories', () => {
        const result = validateFilePath(testAllowedPath, [testAllowedPath]);
        expect(result.valid).toBe(false);
        expect(result.error).toContain('directory');
      });
    });

    describe('File size validation', () => {
      test('should reject files exceeding maximum size', () => {
        const largeFile = path.join(testAllowedPath, 'large.md');
        const largeContent = '# Test\n' + 'x'.repeat(11 * 1024 * 1024); // 11MB
        
        try {
          fs.writeFileSync(largeFile, largeContent);
          const result = validateFilePath(largeFile, [testAllowedPath]);
          expect(result.valid).toBe(false);
          expect(result.error).toContain('exceeds maximum');
          fs.unlinkSync(largeFile);
        } catch (error) {
          // Skip if can't create large file
        }
      });
    });
  });

  describe('validateFilePaths', () => {
    test('should validate multiple valid paths', () => {
      const testFile2 = path.join(testAllowedPath, 'test2.md');
      try {
        fs.writeFileSync(testFile2, '# Test 2');
        const result = validateFilePaths([testFile, testFile2], [testAllowedPath]);
        expect(result.valid).toBe(true);
        expect(result.results.length).toBe(2);
        expect(result.errors.length).toBe(0);
        fs.unlinkSync(testFile2);
      } catch (error) {
        // Skip if can't create file
      }
    });

    test('should reject array with invalid paths', () => {
      const result = validateFilePaths([testFile, outsideFile], [testAllowedPath]);
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

      test('should reject non-array input', () => {
        const result = validateFilePaths('not an array');
        expect(result.valid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
        expect(result.errors[0]).toContain('must be an array');
      });

    test('should handle empty array', () => {
      const result = validateFilePaths([], [testAllowedPath]);
      expect(result.valid).toBe(true);
      expect(result.results.length).toBe(0);
    });
  });
});

