#!/usr/bin/env python3
"""
Process Glass Sketch Command

Main entry point for processing glass sketch images into manufacturing specifications.
Uses a two-agent system with Python precision validation.
"""

import argparse
import sys
import os
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from agent1_creator import CreatorAgent
from agent2_judge import JudgeAgent
from precision_calculator import (
    calculate_section_positions,
    calculate_hole_positions,
    calculate_geometric_feasibility
)
from output_generator import OutputGenerator


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process glass sketch images into manufacturing specifications.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process-glass-sketch.py inputs/sketch.jpg
  python process-glass-sketch.py inputs/sketch.jpg --max-iterations 5
  python process-glass-sketch.py inputs/sketch.jpg --output-dir ./custom_output
        """
    )
    
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to the glass sketch image"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum validation iterations (default: 3)"
    )
    
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.1,
        help="Dimensional tolerance in mm (default: 0.1)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Output directory (default: outputs/)"
    )
    
    parser.add_argument(
        "--skip-3d",
        action="store_true",
        help="Skip 3D model generation"
    )
    
    parser.add_argument(
        "--skip-gcode",
        action="store_true",
        help="Skip CNC G-code generation"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed output"
    )
    
    return parser.parse_args()


def validate_image_path(image_path):
    """Validate that image file exists and is supported format."""
    path = Path(image_path)
    
    if not path.exists():
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    supported_formats = {".jpg", ".jpeg", ".png", ".webp"}
    if path.suffix.lower() not in supported_formats:
        print(f"Error: Unsupported image format: {path.suffix}")
        print(f"Supported formats: {', '.join(supported_formats)}")
        sys.exit(1)
    
    return path


def process_sketch(args):
    """Main processing workflow."""
    image_path = validate_image_path(args.image_path)
    
    if args.verbose:
        print(f"Processing: {image_path}")
        print(f"Max iterations: {args.max_iterations}")
        print(f"Tolerance: {args.tolerance}mm")
    
    # Initialize agents
    creator = CreatorAgent(image_path)
    judge = JudgeAgent()
    output_gen = OutputGenerator(args.output_dir)
    
    # Processing loop
    iteration = 0
    validated = False
    extraction = None
    
    while iteration < args.max_iterations and not validated:
        iteration += 1
        
        if args.verbose:
            print(f"\n--- Iteration {iteration} ---")
        
        # Step 1: Creator extracts specifications
        extraction = creator.extract_specifications()
        
        if args.verbose:
            print("Extraction complete")
        
        # Step 2: Python validation (no AI)
        section_valid = calculate_section_positions(extraction)
        hole_valid = calculate_hole_positions(extraction)
        feasibility = calculate_geometric_feasibility(extraction)
        
        if args.verbose:
            print(f"Section validation: {'PASS' if section_valid else 'FAIL'}")
            print(f"Hole validation: {'PASS' if hole_valid else 'FAIL'}")
            print(f"Feasibility: {'PASS' if feasibility else 'FAIL'}")
        
        # Step 3: Judge reviews
        judgment = judge.review(extraction, {
            "section_valid": section_valid,
            "hole_valid": hole_valid,
            "feasibility": feasibility
        })
        
        if judgment["approved"]:
            validated = True
            if args.verbose:
                print("Validation: APPROVED")
        else:
            if args.verbose:
                print(f"Validation: REJECTED - {judgment['feedback']}")
            creator.apply_feedback(judgment["feedback"])
    
    if not validated:
        print(f"Warning: Could not validate after {args.max_iterations} iterations")
        print("Generating outputs with best available extraction...")
    
    # Generate outputs
    outputs = output_gen.generate_all(
        extraction,
        skip_3d=args.skip_3d,
        skip_gcode=args.skip_gcode
    )
    
    print(f"\nGenerated files in {args.output_dir}/:")
    for output_file in outputs:
        print(f"  - {output_file}")
    
    return 0


def main():
    """Main entry point."""
    args = parse_arguments()
    return process_sketch(args)


if __name__ == "__main__":
    sys.exit(main())
