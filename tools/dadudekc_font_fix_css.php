<?php

/**
 * Font Rendering Fix for dadudekc.com
 * 
 * Fixes missing letter 's' character issue by adding CSS with proper font fallbacks.
 * This file should be included in functions.php or deployed as a plugin.
 * 
 * Applied: 2025-12-17
 */

// Prevent direct access
if (!defined('ABSPATH')) {
    exit;
}

function dadudekc_font_rendering_fix()
{
?>
    <style id="dadudekc-font-fix">
        /* Font Rendering Fix for dadudekc.com - Fixes missing 's' character issue */
        /* Applied: 2025-12-17 */

        /* Override any problematic font-face declarations with proper fallbacks */
        body,
        body *,
        .wp-block-post-content,
        .wp-block-post-excerpt,
        .wp-block-group,
        .wp-block-cover,
        h1,
        h2,
        h3,
        h4,
        h5,
        h6,
        p,
        span,
        div,
        a,
        li,
        td,
        th {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol" !important;
        }

        /* Ensure all headings use safe fonts */
        .wp-block-heading,
        h1.wp-block-heading,
        h2.wp-block-heading,
        h3.wp-block-heading,
        h4.wp-block-heading,
        h5.wp-block-heading,
        h6.wp-block-heading {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }

        /* Fix site title and navigation */
        .wp-block-site-title,
        .wp-block-site-title a,
        .wp-block-navigation-item,
        .wp-block-navigation-item__content {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }

        /* Fix footer text */
        footer,
        footer * {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
        }

        /* Ensure proper font rendering */
        * {
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
    </style>
<?php
}
add_action('wp_head', 'dadudekc_font_rendering_fix', 999);

