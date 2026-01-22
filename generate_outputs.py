#!/usr/bin/env python3
"""
Generate all manufacturing outputs from confirmed extraction data.
Handles both numeric hole coordinates and descriptive positions.
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from output_generator import OutputGenerator

def process_holes(extraction):
    """
    Process holes - convert descriptive positions to numeric if possible,
    or mark as 'position-only' if exact coordinates not specified.
    """
    holes = extraction.get("holes", [])
    sections = extraction.get("sections", [])
    processed_holes = []

    for hole in holes:
        # Check if hole has numeric coordinates
        if "x" in hole and "y" in hole:
            processed_holes.append(hole)
        elif "position" in hole and "section" in hole:
            # Descriptive position - try to estimate based on section
            section_name = hole.get("section", "")
            position = hole.get("position", "")

            # Find the section
            for sec in sections:
                if sec.get("name") == section_name:
                    x_offset = sec.get("x_offset", 0)
                    width = sec.get("width", 0)
                    height = sec.get("height", 0)

                    # Estimate position based on description
                    if "left" in position.lower():
                        x = x_offset + 8  # 8mm from left edge
                    elif "right" in position.lower():
                        x = x_offset + width - 8  # 8mm from right edge
                    else:
                        x = x_offset + width / 2  # center

                    if "bottom" in position.lower():
                        y = 10  # 10mm from bottom (estimated)
                    elif "top" in position.lower():
                        y = height - 10
                    else:
                        y = height / 2

                    processed_holes.append({
                        "x": x,
                        "y": y,
                        "diameter": hole.get("diameter", 8),
                        "purpose": hole.get("purpose", "mounting"),
                        "section": section_name,
                        "position_note": position
                    })
                    break

    return processed_holes

def main():
    # Load confirmed extraction
    extraction_path = Path(__file__).parent / "outputs" / "confirmed_extraction.json"

    if not extraction_path.exists():
        print(f"Error: Extraction file not found at {extraction_path}")
        return 1

    with open(extraction_path, 'r', encoding='utf-8') as f:
        extraction = json.load(f)

    print("=" * 60)
    print("GLASS MANUFACTURING OUTPUT GENERATOR")
    print("=" * 60)
    print()
    print("Extraction Data Summary:")
    dims = extraction.get("dimensions", {})
    print(f"  - Dimensions: {dims.get('width')} x {dims.get('height')} x {dims.get('thickness')} mm")
    print(f"  - Sections: {len(extraction.get('sections', []))}")
    print(f"  - Holes: {len(extraction.get('holes', []))}")
    print(f"  - Edge Type: {extraction.get('edge_type', 'N/A')}")
    print(f"  - Glass Type: {extraction.get('glass_type', 'N/A')}")
    print(f"  - User Confirmed: {extraction.get('user_confirmed', False)}")
    print()

    # Print section details
    print("Section Details:")
    for section in extraction.get('sections', []):
        notch_info = f", Notch: {section.get('notch_depth')}mm" if section.get('has_notch') else ""
        print(f"  - {section.get('name')} ({section.get('type')}): {section.get('width')} x {section.get('height')} mm{notch_info}")
    print()

    # Process holes (handle descriptive positions)
    processed_holes = process_holes(extraction)

    # Print hole details
    print("Hole Details:")
    if processed_holes:
        for i, hole in enumerate(processed_holes, 1):
            if "x" in hole and "y" in hole:
                pos_note = f" ({hole.get('position_note', '')})" if hole.get('position_note') else ""
                print(f"  - Hole {i}: X={hole['x']:.1f}mm, Y={hole['y']:.1f}mm, D={hole.get('diameter', 8)}mm - {hole.get('section', 'N/A')}{pos_note}")
            else:
                print(f"  - Hole {i}: {hole.get('position', 'unknown')} - {hole.get('section', 'N/A')}")
    else:
        print("  - No holes with numeric coordinates")
    print()

    # Update extraction with processed holes
    extraction_for_output = extraction.copy()
    extraction_for_output["holes"] = processed_holes

    # Generate outputs
    print("Generating outputs...")
    generator = OutputGenerator(output_dir="outputs")
    files = generator.generate_all(extraction_for_output)

    print()
    print("Generated Files:")
    for f in files:
        print(f"  - {f}")

    print()
    print("=" * 60)
    print("OUTPUT GENERATION COMPLETE")
    print("=" * 60)

    return 0

if __name__ == "__main__":
    sys.exit(main())
