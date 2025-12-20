# V2 Compliance Checker MCP Server

MCP server for V2 compliance validation. Enables agents to check files, functions, and get exception lists before committing.

## Configuration

Add to your MCP settings (e.g., Claude Desktop config):

```json
{
  "mcpServers": {
    "v2-compliance": {
      "command": "python",
      "args": [
        "D:/Agent_Cellphone_V2_Repository/mcp_servers/v2_compliance_server.py"
      ]
    }
  }
}
```

## Available Tools

### 1. `check_v2_compliance`
Check a file for V2 compliance (comprehensive check)

**Parameters:**
- `file_path` (required): File path to check (relative or absolute)
- `rules_file` (optional): Path to V2 rules YAML file

**Example:**
```json
{
  "name": "check_v2_compliance",
  "arguments": {
    "file_path": "src/core/messaging_template_texts.py"
  }
}
```

**Returns:**
- `is_compliant`: Whether file is compliant
- `is_exception`: Whether file is on exceptions list
- `violations`: Array of violations found
- `line_count`: Total lines in file

### 2. `validate_file_size`
Validate file size against V2 limit

**Parameters:**
- `file_path` (required): File path to check
- `max_lines` (optional): Maximum lines allowed (default: 300)

**Example:**
```json
{
  "name": "validate_file_size",
  "arguments": {
    "file_path": "src/core/new_file.py",
    "max_lines": 300
  }
}
```

### 3. `check_function_size`
Check function size against V2 limit

**Parameters:**
- `file_path` (required): Python file path
- `function_name` (optional): Specific function name to check
- `max_lines` (optional): Maximum lines per function (default: 30)

**Example:**
```json
{
  "name": "check_function_size",
  "arguments": {
    "file_path": "src/core/messaging.py",
    "function_name": "format_message",
    "max_lines": 30
  }
}
```

### 4. `get_v2_exceptions`
Get list of approved V2 compliance exceptions

**Parameters:** None

**Example:**
```json
{
  "name": "get_v2_exceptions",
  "arguments": {}
}
```

## Integration with Agent Operating Cycle

### BEFORE COMMITTING (MANDATORY)
- Check file compliance: `check_v2_compliance(file_path)`
- Validate file size: `validate_file_size(file_path)`
- Check function sizes: `check_function_size(file_path)`
- Check exceptions: `get_v2_exceptions()` if file exceeds limits

### DURING CYCLE
- Check before creating large files
- Validate refactored code

## V2 Limits

- **File size:** 300 lines (default)
- **Class size:** 200 lines (default)
- **Function size:** 30 lines (default)

## Benefits

1. **Prevent Violations** - Check before committing
2. **Exception Awareness** - Know which files are exceptions
3. **Function Validation** - Check individual functions
4. **Automated Checking** - Agents can self-validate

## Related Documents

- `scripts/validate_v2_compliance.py` - V2 compliance validator source
- `config/v2_rules.yaml` - V2 rules configuration
- `docs/V2_COMPLIANCE_EXCEPTIONS.md` - Approved exceptions list

