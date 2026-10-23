#!/usr/bin/env python3
"""Read-only validation of this corrected independent desk, not source recertification."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

if __name__=="__main__":
    suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"/"pipeline"),pattern="test_desk_455acb16.py")
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    print("Desk structural/evidence gate: "+("PASS" if result.wasSuccessful() else "FAIL")+". External truth is limited to retained source observations.")
    sys.exit(0 if result.wasSuccessful() else 1)
