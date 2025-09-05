#!/usr/bin/env python3
import sys
import traceback
from tests.enhanced_3d import test_interactive_dataset as t


def run():
    print("Interactive Dataset Tests")
    print("=" * 40)
    passed = 0
    total = 2

    try:
        t.test_dataset_export_import()
        print("✅ test_dataset_export_import PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ test_dataset_export_import FAILED: {e}")
        traceback.print_exc()

    try:
        t.test_cross_section_render_save()
        print("✅ test_cross_section_render_save PASSED")
        passed += 1
    except Exception as e:
        print(f"❌ test_cross_section_render_save FAILED: {e}")
        traceback.print_exc()

    print("\nSummary:")
    print(f"Passed: {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run())

