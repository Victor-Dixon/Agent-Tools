# Blog Post Templates

This directory contains templates for automated blog post generation.

## Strategy Blog Post Template

**File:** `strategy_blog_post_template.html`

### Purpose
A standardized template for all trading strategy analysis blog posts. Ensures consistent formatting and structure across all posts.

### Template Variables

The template uses Python string formatting with the following variables:

- `{strategy_name}` - Name of the trading strategy
- `{analysis_date}` - Date of analysis (YYYY-MM-DD format)
- `{symbol}` - Trading symbol (e.g., TSLA, AAPL)
- `{strategy_type}` - Type of strategy (e.g., "trend-following", "mean-reversion")
- `{indicators_list}` - HTML list of indicators and their values
- `{risk_parameters_list}` - HTML list of risk management parameters
- `{long_entry_conditions}` - HTML list of long entry conditions
- `{short_entry_conditions}` - HTML list of short entry conditions
- `{exit_strategy_list}` - HTML list of exit strategy details
- `{risk_management_list}` - HTML list of risk management features
- `{key_features_list}` - HTML list of key strategy features
- `{performance_notes_list}` - HTML list of performance considerations
- `{report_slug}` - URL slug for free report (e.g., "tsla-strategy-report")
- `{premium_report_slug}` - URL slug for premium report (e.g., "tsla-strategy-report-premium")

### Template Structure

1. **Header Section**
   - Strategy name and analysis date
   - Symbol information

2. **Overview**
   - Brief description of the strategy

3. **Strategy Configuration**
   - Two-column layout with Indicators and Risk Parameters

4. **Entry Logic**
   - Separate sections for Long and Short entries

5. **Exit Strategy**
   - Profit targets, stop losses, trailing stops

6. **Risk Management**
   - Detailed risk management explanation

7. **Key Features**
   - Bullet list of strategy features

8. **Performance Considerations**
   - Notes about when strategy works best

9. **Call-to-Action**
   - Links to free and premium reports
   - Disclaimer about hobbyist nature

### Usage

The template is automatically used by `strategy_blog_automation.py` when generating blog posts. No manual intervention needed.

### Customization

To modify the template:
1. Edit `strategy_blog_post_template.html`
2. Ensure all template variables are properly filled in `generate_blog_post_content()`
3. Test with: `python tools/strategy_blog_automation.py --site tradingrobotplug.com --generate-post`

### WordPress Block Format

The template uses WordPress Gutenberg block format comments (e.g., `<!-- wp:heading -->`) for proper rendering in the WordPress editor.

