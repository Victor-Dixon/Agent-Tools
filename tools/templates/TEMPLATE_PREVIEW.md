# Blog Post Template Preview

## Template Structure Overview

The strategy blog post template creates a consistent, professional structure for all trading strategy analysis posts.

### Sections Included:

1. **Header**
   - Strategy name as H2
   - Analysis date and symbol

2. **Overview**
   - Brief introduction to the strategy

3. **Strategy Configuration** (Two-column layout)
   - Left: Indicators (MA periods, RSI settings)
   - Right: Risk Parameters (risk %, stop loss, profit target)

4. **Entry Logic**
   - Long entry conditions (bulleted list)
   - Short entry conditions (bulleted list)

5. **Exit Strategy**
   - Profit targets
   - Stop losses
   - Trailing stop details (if enabled)

6. **Risk Management**
   - Explanation paragraph
   - Detailed risk management features

7. **Key Features**
   - Bulleted list of strategy highlights

8. **Performance Considerations**
   - Notes about when/where strategy works best

9. **Call-to-Action**
   - Links to free and premium reports
   - Professional buttons
   - Disclaimer about hobbyist nature

### Visual Structure

```
┌─────────────────────────────────────┐
│ Strategy Analysis: [Name]           │
│ Analysis Date: [Date] | Symbol: [S] │
├─────────────────────────────────────┤
│ Overview                            │
│ [Brief description]                 │
├─────────────────────────────────────┤
│ Strategy Configuration              │
│ ┌─────────────┬─────────────┐       │
│ │ Indicators  │ Risk Params │       │
│ │ • MA 50     │ • Risk 0.5% │       │
│ │ • MA 200    │ • Stop 1%   │       │
│ │ • RSI 14    │ • Target 15%│       │
│ └─────────────┴─────────────┘       │
├─────────────────────────────────────┤
│ Entry Logic                         │
│ Long Entries:                        │
│ • Condition 1                       │
│ • Condition 2                       │
│                                     │
│ Short Entries:                       │
│ • Condition 1                       │
│ • Condition 2                       │
├─────────────────────────────────────┤
│ Exit Strategy                       │
│ • Profit Target: 15%                │
│ • Stop Loss: 1%                     │
├─────────────────────────────────────┤
│ Risk Management                     │
│ [Explanation paragraph]             │
│ • Feature 1                         │
│ • Feature 2                         │
├─────────────────────────────────────┤
│ Key Features                        │
│ • Feature 1                         │
│ • Feature 2                         │
├─────────────────────────────────────┤
│ Performance Considerations          │
│ • Note 1                            │
│ • Note 2                            │
├─────────────────────────────────────┤
│ Want the Complete Analysis?         │
│ [Button: View Free Report]          │
│ [Button: Get Premium Report]        │
│                                     │
│ [Disclaimer]                        │
└─────────────────────────────────────┘
```

### WordPress Block Format

The template uses WordPress Gutenberg block comments for proper rendering:
- `<!-- wp:heading -->` - Headings
- `<!-- wp:paragraph -->` - Paragraphs
- `<!-- wp:list -->` - Lists
- `<!-- wp:buttons -->` - Button groups
- `<!-- wp:group -->` - Column layouts
- `<!-- wp:separator -->` - Horizontal rules

### Benefits

1. **Consistency** - All posts have the same structure
2. **Professional** - Clean, organized layout
3. **SEO-Friendly** - Proper heading hierarchy
4. **Conversion-Optimized** - Clear CTAs to reports
5. **Mobile-Responsive** - WordPress blocks adapt to screen size
6. **Maintainable** - Single template file to update

### Customization

To modify the template:
1. Edit `tools/templates/strategy_blog_post_template.html`
2. Update variable filling in `generate_blog_post_content()`
3. Test with a new post generation

