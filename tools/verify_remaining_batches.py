"""Verify remaining batch files for V2 compliance."""
from pathlib import Path

project_root = Path(__file__).parent.parent

files_to_check = {
    'Batch 2': {
        'unified_discord_bot.py': Path('src/discord_commander/unified_discord_bot.py'),
    },
    'Batch 3': {
        'vector_database_service_unified.py': Path('src/services/vector_database_service_unified.py'),
        'vector_integration_unified.py': Path('src/services/vector_integration_unified.py'),
    },
    'Batch 4': {
        'unified_onboarding_service.py': Path('src/services/unified_onboarding_service.py'),
        'unified_onboarding_service (onboarding)': Path('src/services/onboarding/unified_onboarding_service.py'),
    },
}

print("=" * 80)
print("REMAINING BATCH FILES VERIFICATION")
print("=" * 80)

for batch, files in files_to_check.items():
    print(f"\n{batch}:")
    for name, filepath in files.items():
        full_path = project_root / filepath
        if full_path.exists():
            line_count = len(full_path.read_text(
                encoding='utf-8').splitlines())
            status = "✅ COMPLIANT" if line_count <= 400 else "⚠️ VIOLATION"
            print(f"  {name}: {line_count} lines {status}")
        else:
            print(f"  {name}: NOT FOUND")

print("\n" + "=" * 80)
