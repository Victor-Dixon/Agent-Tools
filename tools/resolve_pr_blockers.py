"""
Fix script for MeTuber webcam errors:
- Handles 2D (grayscale) vs 3D (BGR) image arrays
- Fixes IndexError in webcam_threading.py line 628
- Fixes ValueError in webcam_filter_pyqt5.py line 690
"""

from pathlib import Path


def fix_webcam_threading(file_path: str) -> bool:
    """
    Fix the _push_output method in webcam_threading.py
    Handles both grayscale (2D) and color (3D) images.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        has_cv2_import = False

        # Check if cv2 is already imported
        for line in lines:
            if 'import cv2' in line or 'from cv2' in line:
                has_cv2_import = True
                break

        # Find and fix the problematic line
        for i, line in enumerate(lines):
            # Look for: rgb = bgr[:, :, ::-1].copy()
            if 'rgb' in line and 'bgr[:, :, ::-1]' in line and '.copy()' in line:
                # Get indentation
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent

                # Insert shape checking before the rgb assignment
                fix_lines = [
                    f"{indent_str}# Handle both grayscale (2D) and color (3D) images\n",
                    f"{indent_str}if len(bgr.shape) == 2:\n",
                    f"{indent_str}    # Convert grayscale to BGR\n",
                    f"{indent_str}    bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)\n",
                    f"{indent_str}elif len(bgr.shape) == 3 and bgr.shape[2] == 1:\n",
                    f"{indent_str}    # Convert single channel to BGR\n",
                    f"{indent_str}    bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)\n",
                ]

                lines[i:i+1] = fix_lines + [line]
                modified = True
                break

        # Add cv2 import if needed
        if modified and not has_cv2_import:
            # Find the first import statement
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    # Insert cv2 import after this line
                    lines.insert(i + 1, 'import cv2\n')
                    break

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

    return False


def fix_webcam_filter_pyqt5(file_path: str) -> bool:
    """
    Fix the _show_bgr_on_preview method in webcam_filter_pyqt5.py
    Handles both grayscale (2D) and color (3D) images.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        modified = False
        has_cv2_import = False

        # Check if cv2 is already imported
        for line in lines:
            if 'import cv2' in line or 'from cv2' in line:
                has_cv2_import = True
                break

        # Find and fix the problematic line
        for i, line in enumerate(lines):
            # Look for: h, w, c = bgr.shape
            if 'h, w, c = bgr.shape' in line or ('h' in line and 'w' in line and 'c' in line and 'bgr.shape' in line):
                # Get indentation
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent

                # Insert shape checking before the unpacking
                fix_lines = [
                    f"{indent_str}# Handle both grayscale (2D) and color (3D) images\n",
                    f"{indent_str}if len(bgr.shape) == 2:\n",
                    f"{indent_str}    # Convert grayscale to BGR\n",
                    f"{indent_str}    bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)\n",
                    f"{indent_str}elif len(bgr.shape) == 3 and bgr.shape[2] == 1:\n",
                    f"{indent_str}    # Convert single channel to BGR\n",
                    f"{indent_str}    bgr = cv2.cvtColor(bgr, cv2.COLOR_GRAY2BGR)\n",
                ]

                lines[i:i+1] = fix_lines + [line]
                modified = True
                break

        # Add cv2 import if needed
        if modified and not has_cv2_import:
            # Find the first import statement
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    # Insert cv2 import after this line
                    lines.insert(i + 1, 'import cv2\n')
                    break

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

    return False


def main():
    """Main function to fix both files."""
    metuber_path = Path("d:/MeTuber")

    if not metuber_path.exists():
        print("❌ MeTuber directory not found at d:/MeTuber")
        print("Please update the path in this script or run manually.")
        return

    webcam_threading = metuber_path / "webcam_threading.py"
    webcam_filter = metuber_path / "webcam_filter_pyqt5.py"

    fixes_applied = []

    if webcam_threading.exists():
        print(f"🔧 Fixing {webcam_threading}...")
        if fix_webcam_threading(str(webcam_threading)):
            fixes_applied.append("webcam_threading.py")
            print("✅ Fixed webcam_threading.py")
        else:
            print("⚠️  No changes needed or pattern not found in webcam_threading.py")
    else:
        print(f"⚠️  File not found: {webcam_threading}")

    if webcam_filter.exists():
        print(f"🔧 Fixing {webcam_filter}...")
        if fix_webcam_filter_pyqt5(str(webcam_filter)):
            fixes_applied.append("webcam_filter_pyqt5.py")
            print("✅ Fixed webcam_filter_pyqt5.py")
        else:
            print("⚠️  No changes needed or pattern not found in webcam_filter_pyqt5.py")
    else:
        print(f"⚠️  File not found: {webcam_filter}")

    if fixes_applied:
        print(f"\n✅ Successfully fixed {len(fixes_applied)} file(s):")
        for f in fixes_applied:
            print(f"   - {f}")
        print("\n⚠️  Please review the changes and test the application.")
    else:
        print("\n⚠️  No fixes were applied. The error patterns may have changed.")


if __name__ == "__main__":
    main()
