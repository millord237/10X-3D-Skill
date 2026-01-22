#!/usr/bin/env python3
"""
Precision Calculator Module

Contains the three Python functions for validating glass specifications.
NO AI is used in these calculations - pure Python math only.
"""

from typing import Dict, List, Any, Tuple
import math


def calculate_section_positions(extraction: Dict[str, Any]) -> bool:
    """
    Validate that section positions and widths sum to total panel width.
    
    Args:
        extraction: Dictionary containing extracted specifications
    
    Returns:
        bool: True if sections are valid, False otherwise
    """
    dimensions = extraction.get("dimensions", {})
    sections = extraction.get("sections", [])
    
    total_width = dimensions.get("width", 0)
    total_height = dimensions.get("height", 0)
    
    # If no sections defined, panel is valid as single section
    if not sections:
        return total_width > 0 and total_height > 0
    
    # Calculate sum of section widths
    section_width_sum = sum(s.get("width", 0) for s in sections)
    
    # Check if sum matches total width (within tolerance)
    tolerance = 0.1  # mm
    width_valid = abs(section_width_sum - total_width) <= tolerance
    
    # Check section continuity
    sorted_sections = sorted(sections, key=lambda s: s.get("x_offset", 0))
    continuity_valid = True
    expected_offset = 0.0
    
    for section in sorted_sections:
        offset = section.get("x_offset", 0)
        width = section.get("width", 0)
        if abs(offset - expected_offset) > tolerance:
            continuity_valid = False
            break
        expected_offset = offset + width
    
    if abs(expected_offset - total_width) > tolerance:
        continuity_valid = False
    
    return width_valid and continuity_valid


def calculate_hole_positions(extraction: Dict[str, Any]) -> bool:
    """
    Calculate and validate exact hole coordinates.
    
    Args:
        extraction: Dictionary containing extracted specifications
    
    Returns:
        bool: True if all hole positions are valid, False otherwise
    """
    dimensions = extraction.get("dimensions", {})
    holes = extraction.get("holes", [])
    
    width = dimensions.get("width", 0)
    height = dimensions.get("height", 0)
    thickness = dimensions.get("thickness", 0)
    
    if not holes:
        return True
    
    min_edge_distance = max(thickness * 2, 25.0) if thickness > 0 else 25.0
    
    for i, hole in enumerate(holes):
        x = hole.get("x", 0)
        y = hole.get("y", 0)
        diameter = hole.get("diameter", 0)
        radius = diameter / 2
        
        if x <= 0 or y <= 0:
            return False
        if x - radius < min_edge_distance:
            return False
        if x + radius > width - min_edge_distance:
            return False
        if y - radius < min_edge_distance:
            return False
        if y + radius > height - min_edge_distance:
            return False
        
        # Check hole spacing
        for j, other in enumerate(holes):
            if i >= j:
                continue
            ox = other.get("x", 0)
            oy = other.get("y", 0)
            od = other.get("diameter", 0)
            distance = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
            min_spacing = max(diameter, od) * 2
            if distance < min_spacing:
                return False
    
    return True


def calculate_geometric_feasibility(extraction: Dict[str, Any]) -> bool:
    """
    Check manufacturing constraints and geometric feasibility.
    
    Args:
        extraction: Dictionary containing extracted specifications
    
    Returns:
        bool: True if geometry is feasible, False otherwise
    """
    dimensions = extraction.get("dimensions", {})
    holes = extraction.get("holes", [])
    edge_type = extraction.get("edge_type", "flat_polished")
    glass_type = extraction.get("glass_type", "clear_tempered")
    
    width = dimensions.get("width", 0)
    height = dimensions.get("height", 0)
    thickness = dimensions.get("thickness", 0)
    
    if width <= 0 or height <= 0 or thickness <= 0:
        return False
    
    # Check aspect ratio
    aspect_ratio = max(width, height) / min(width, height)
    if aspect_ratio > 10.0:
        return False
    
    # Check thickness vs panel size
    panel_area = width * height
    min_thickness_map = {
        1000000: 4, 2000000: 6, 4000000: 8,
        8000000: 10, float("inf"): 12
    }
    
    min_thickness = 4
    for area_limit, min_t in min_thickness_map.items():
        if panel_area <= area_limit:
            min_thickness = min_t
            break
    
    if thickness < min_thickness:
        return False
    
    # Check hole feasibility
    for hole in holes:
        diameter = hole.get("diameter", 0)
        if diameter <= 0:
            continue
        if diameter < thickness:
            return False
        max_hole = min(width, height) / 3
        if diameter > max_hole:
            return False
    
    # Check edge type
    edge_requirements = {
        "flat_polished": 3, "beveled": 6, "pencil_polished": 3,
        "mitered": 10, "ogee": 12
    }
    min_edge_t = edge_requirements.get(edge_type, 3)
    if thickness < min_edge_t:
        return False
    
    # Tempered glass constraints
    if "tempered" in glass_type.lower():
        if width < 100 or height < 100:
            return False
    
    return True


def calculate_weight(extraction: Dict[str, Any], density: float = 2500.0) -> float:
    """Calculate panel weight in kg."""
    dims = extraction.get("dimensions", {})
    holes = extraction.get("holes", [])
    
    w = dims.get("width", 0) / 1000
    h = dims.get("height", 0) / 1000
    t = dims.get("thickness", 0) / 1000
    
    volume = w * h * t
    for hole in holes:
        d = hole.get("diameter", 0) / 1000
        hole_vol = math.pi * (d/2) ** 2 * t
        volume -= hole_vol
    
    return volume * density
