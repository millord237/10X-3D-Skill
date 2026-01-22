#!/usr/bin/env python3
"""
Validate Extraction Command

Validates an existing extraction JSON file without reprocessing the image.
Useful for checking saved extractions or debugging validation issues.
"""

import argparse
import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from precision_calculator import (
    calculate_section_positions,
    calculate_hole_positions,
    calculate_geometric_feasibility
)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate an existing extraction JSON file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate-extraction.py outputs/validation_report.json
  python validate-extraction.py my_extraction.json --verbose
        """
    )
    
    parser.add_argument(
        "json_path",
        type=str,
        help="Path to the extraction JSON file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed output"
    )
    
    return parser.parse_args()


def load_extraction(json_path):
    """Load extraction data from JSON file."""
    path = Path(json_path)
    
    if not path.exists():
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)
    
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("extraction", data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file: {e}")
        sys.exit(1)


def validate_extraction(args):
    """Run validation on extraction data."""
    extraction = load_extraction(args.json_path)
    
    if args.verbose:
        print(f"Validating: {args.json_path}")
        print(f"Dimensions: {extraction.get('dimensions', {})}")
    
    # Run all validations
    results = {
        "section_positions": calculate_section_positions(extraction),
        "hole_positions": calculate_hole_positions(extraction),
        "geometric_feasibility": calculate_geometric_feasibility(extraction)
    }
    
    # Print results
    print("\nValidation Results:")
    print("-" * 40)
    
    all_passed = True
    for check, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {check}: {status}")
        if not passed:
            all_passed = False
    
    print("-" * 40)
    overall = "PASSED" if all_passed else "FAILED"
    print(f"Overall: {overall}")
    
    return 0 if all_passed else 1


def main():
    """Main entry point."""
    args = parse_arguments()
    return validate_extraction(args)


if __name__ == "__main__":
    sys.exit(main())
