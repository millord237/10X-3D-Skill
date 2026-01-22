#!/usr/bin/env python3
"""
OA-3D Skills - Main Entry Point
================================

Auto-triggers the appropriate skill based on input folder:
- inputs/Glass-Skills/* → Glass Manufacturing Skill
- inputs/Boundary-Skills/* → Boundary Analysis Skill

IMPORTANT: Already processed images are flagged and skipped unless --force is used.

Usage:
    python run.py <image_path>              # Run only if not already processed
    python run.py <image_path> --force      # Force re-run even if processed
    python run.py --list                    # List all images with status
    python run.py --pending                 # List only unprocessed images
    python run.py --next                    # Run next unprocessed image
    python run.py --next glass              # Run next unprocessed glass image
    python run.py --next boundary           # Run next unprocessed boundary image

Examples:
    python run.py inputs/Glass-Skills/Glass-Skill-3.jpeg
    python run.py inputs/Glass-Skills/Glass-Skill-2.jpeg --force
    python run.py --next
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))


def load_package_config():
    """Load package.json configuration."""
    package_path = Path(__file__).parent / "package.json"
    if package_path.exists():
        with open(package_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_output_dir_for_image(image_path: str) -> str:
    """
    Get the expected output directory for an image.

    IMPORTANT: Skill type is determined ONLY by the PARENT FOLDER name,
    NOT by the filename. Any image in Glass-Skills/ folder triggers glass skill,
    any image in Boundary-Skills/ folder triggers boundary skill.
    """
    path = Path(image_path)
    path_str = str(path).replace("\\", "/").lower()

    # Get parent folder name (the immediate folder containing the image)
    parent_folder = path.parent.name.lower()

    # Extract a number from the filename for output folder naming
    match = re.search(r'(\d+)', path.stem)
    skill_num = match.group(1) if match else "1"

    # Determine skill type ONLY from parent folder
    if "glass" in parent_folder:
        return f"outputs/Glass-Skill-{skill_num}"
    elif "boundary" in parent_folder:
        return f"outputs/Boundary-Skill-{skill_num}"

    # Fallback: use parent folder name as skill type
    return f"outputs/{parent_folder.title()}-Skill-{skill_num}"


def is_image_processed(image_path: str) -> dict:
    """
    Check if an image has already been processed.

    Returns:
        dict with 'processed' (bool), 'output_dir', 'files' list
    """
    output_dir = get_output_dir_for_image(image_path)
    output_path = Path(output_dir)

    if not output_path.exists():
        return {"processed": False, "output_dir": output_dir, "files": []}

    # Check for key output files
    files = list(output_path.glob("*"))
    key_files = [f.name for f in files if f.suffix in ['.html', '.json', '.svg', '.md', '.gcode']]

    # Consider processed if has at least 3 output files
    is_processed = len(key_files) >= 3

    return {
        "processed": is_processed,
        "output_dir": output_dir,
        "files": key_files,
        "file_count": len(key_files)
    }


def detect_skill_from_path(image_path: str) -> dict:
    """
    Detect which skill to use based on image path.

    IMPORTANT: Skill detection is based ONLY on the PARENT FOLDER name,
    NOT on the filename. This allows ANY image file (regardless of naming)
    to trigger the appropriate skill based on which folder it's in.

    Returns:
        dict with 'skill_name', 'skill_config', 'output_dir', 'status'
    """
    config = load_package_config()
    path = Path(image_path)

    # Get parent folder name (the immediate folder containing the image)
    parent_folder = path.parent.name.lower()

    # Check processing status
    status = is_image_processed(image_path)

    # Determine skill based on PARENT FOLDER NAME ONLY
    skill_name = None
    if "glass" in parent_folder:
        skill_name = "glass-manufacturing"
    elif "boundary" in parent_folder:
        skill_name = "boundary-analysis"

    if skill_name:
        for skill in config.get("skills", []):
            if skill.get("name") == skill_name:
                return {
                    "skill_name": skill_name,
                    "skill_config": skill,
                    "output_dir": status["output_dir"],
                    "reference_dir": skill.get("referenceFolder", ""),
                    "status": status
                }

    # Fallback: try pattern matching if parent folder doesn't match
    path_str = str(path).replace("\\", "/")
    for rule in config.get("autoTrigger", {}).get("rules", []):
        pattern = rule.get("inputPattern", "").replace("*", ".*")
        if re.search(pattern, path_str):
            skill_name = rule.get("skill")
            for skill in config.get("skills", []):
                if skill.get("name") == skill_name:
                    return {
                        "skill_name": skill_name,
                        "skill_config": skill,
                        "output_dir": status["output_dir"],
                        "reference_dir": skill.get("referenceFolder", ""),
                        "status": status
                    }

    return None


def get_all_images_status():
    """Get status of all input images."""
    config = load_package_config()
    results = {"glass": [], "boundary": []}

    for skill in config.get("skills", []):
        input_folder = Path(skill.get("inputFolder", "inputs"))
        skill_type = "glass" if "glass" in skill.get("name", "").lower() else "boundary"

        if input_folder.exists():
            images = list(input_folder.glob("*.jpeg")) + list(input_folder.glob("*.jpg")) + list(input_folder.glob("*.png"))
            for img in sorted(images):
                status = is_image_processed(str(img))
                results[skill_type].append({
                    "name": img.name,
                    "path": str(img),
                    "processed": status["processed"],
                    "output_dir": status["output_dir"],
                    "file_count": status.get("file_count", 0)
                })

    return results


def list_available_images(show_pending_only=False):
    """List all available input images with processing status."""
    config = load_package_config()
    all_status = get_all_images_status()

    print("\n" + "=" * 70)
    print("OA-3D SKILLS - IMAGE STATUS")
    print("=" * 70)

    total_processed = 0
    total_pending = 0

    for skill in config.get("skills", []):
        skill_type = "glass" if "glass" in skill.get("name", "").lower() else "boundary"
        images = all_status.get(skill_type, [])

        processed = [i for i in images if i["processed"]]
        pending = [i for i in images if not i["processed"]]

        total_processed += len(processed)
        total_pending += len(pending)

        print(f"\n{skill.get('displayName', skill.get('name'))}:")
        print(f"  Input Folder: {skill.get('inputFolder')}")
        print(f"  Reference: {skill.get('referenceFolder')}")
        print("-" * 50)

        if not show_pending_only and processed:
            print("  [DONE] PROCESSED (outputs exist):")
            for img in processed:
                print(f"    [x] {img['name']} -> {img['output_dir']} ({img['file_count']} files)")

        if pending:
            print("  [NEW] PENDING (not yet processed):")
            for img in pending:
                print(f"    [ ] {img['name']}")
        elif not show_pending_only:
            print("  [NEW] PENDING: (none)")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {total_processed} processed, {total_pending} pending")
    print("=" * 70)

    if total_pending > 0:
        print("\nTo process next pending image: python run.py --next")
        print("To force re-process: python run.py <image_path> --force")
    else:
        print("\nAll images have been processed!")
        print("Use --force to re-process: python run.py <image_path> --force")

    print("")
    return all_status


def get_next_pending_image(skill_filter=None):
    """Get the next unprocessed image."""
    all_status = get_all_images_status()

    for skill_type in ["glass", "boundary"]:
        if skill_filter and skill_filter.lower() not in skill_type:
            continue

        for img in all_status.get(skill_type, []):
            if not img["processed"]:
                return img

    return None


def run_glass_skill(image_path: str, extraction_path: str = None, output_dir: str = None):
    """Run the glass manufacturing skill."""
    from two_agent_workflow import run_workflow

    # Load extraction if provided
    extraction = None
    if extraction_path and Path(extraction_path).exists():
        with open(extraction_path, 'r', encoding='utf-8') as f:
            extraction = json.load(f)
        print(f"Loaded extraction: {extraction_path}")

    # Determine output directory
    if not output_dir:
        output_dir = get_output_dir_for_image(image_path)

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Run workflow
    result = run_workflow(image_path, extraction, output_dir)
    return result


def run_boundary_skill(image_path: str, extraction_path: str = None, output_dir: str = None):
    """Run the boundary analysis skill."""
    if not output_dir:
        output_dir = get_output_dir_for_image(image_path)

    print("\n" + "=" * 60)
    print("BOUNDARY ANALYSIS SKILL")
    print("=" * 60)
    print(f"Image: {image_path}")
    print(f"Output: {output_dir}")
    print("\nNote: Boundary skill workflow - analyze the image following")
    print("the methodology in skills/glass-manufacturing/SKILL-boundary.md")
    print("\nReference outputs available in: assets/Boundary-Skill-1/")
    print("=" * 60 + "\n")

    return {
        "success": True,
        "skill": "boundary-analysis",
        "message": "Review SKILL-boundary.md for analysis methodology"
    }


def print_header():
    """Print the skill header."""
    print("\n" + "=" * 70)
    print("OA-3D SKILLS - Auto-Trigger System")
    print("=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        list_available_images()
        sys.exit(0)

    # Handle special commands
    if sys.argv[1] == "--list":
        list_available_images()
        sys.exit(0)

    if sys.argv[1] == "--pending":
        list_available_images(show_pending_only=True)
        sys.exit(0)

    if sys.argv[1] == "--next":
        skill_filter = sys.argv[2] if len(sys.argv) > 2 else None
        next_img = get_next_pending_image(skill_filter)

        if next_img:
            print_header()
            print(f"Running next pending image: {next_img['name']}")
            # Recursively call with the image path
            sys.argv = [sys.argv[0], next_img['path']]
        else:
            print("\n[OK] All images have been processed!")
            print("Use --force to re-process an image.")
            sys.exit(0)

    # Parse arguments
    force_run = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--force"]

    # Handle forced skill selection
    forced_skill = None
    if "--skill" in args:
        idx = args.index("--skill")
        if idx + 1 < len(args):
            forced_skill = args[idx + 1]
            args = args[:idx] + args[idx + 2:]

    if not args:
        print("Error: No image path provided")
        sys.exit(1)

    image_path = args[0]
    extraction_path = args[1] if len(args) > 1 else None

    # Check image exists
    if not Path(image_path).exists():
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)

    print_header()

    # Detect skill from path
    skill_info = detect_skill_from_path(image_path)

    if not skill_info:
        print("Error: Could not detect skill from path")
        sys.exit(1)

    # Check if already processed
    status = skill_info.get("status", {})
    if status.get("processed") and not force_run:
        print(f"[SKIP] IMAGE ALREADY PROCESSED")
        print(f"  Image: {image_path}")
        print(f"  Output: {status['output_dir']}")
        print(f"  Files: {status.get('file_count', 0)} output files exist")
        print("")
        print("To re-process, use: python run.py <image_path> --force")
        print("To see all statuses: python run.py --list")
        sys.exit(0)

    skill_name = forced_skill or skill_info["skill_name"]

    if force_run:
        print(f"[FORCE] Re-processing existing outputs")

    print(f"Skill: {skill_info['skill_config'].get('displayName', skill_name)}")
    print(f"Image: {image_path}")
    print(f"Output: {skill_info['output_dir']}")
    if skill_info.get('reference_dir'):
        print(f"Reference: {skill_info['reference_dir']}")
    print("=" * 70)

    # Run the appropriate skill
    output_dir = skill_info["output_dir"]

    if skill_name in ["glass-manufacturing", "glass"]:
        result = run_glass_skill(image_path, extraction_path, output_dir)
    elif skill_name in ["boundary-analysis", "boundary"]:
        result = run_boundary_skill(image_path, extraction_path, output_dir)
    else:
        print(f"Error: Unknown skill: {skill_name}")
        sys.exit(1)

    # Print result
    if result:
        print("\n" + "=" * 70)
        print("SKILL EXECUTION COMPLETE")
        print("=" * 70)
        if isinstance(result, dict):
            print(f"Success: {result.get('success', 'N/A')}")
            if 'confidence' in result:
                print(f"Confidence: {result['confidence']:.1f}%")
            if 'files' in result:
                print(f"Files generated: {len(result['files'])}")
        print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
