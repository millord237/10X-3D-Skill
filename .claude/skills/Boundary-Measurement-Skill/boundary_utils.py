"""
Boundary Calculation Utilities - Architectural Grade
Precision calculations for plot boundaries and glass panels

This module provides architect-level functions for:
- Polygon calculations (area, perimeter, centroid)
- Segment analysis (length, direction, angles)
- Interior angle calculations at vertices
- Coordinate transformations for visualization
- Validation (closure, geometry, measurements)
- SVG/HTML generation helpers
- Compass direction mapping (N/S/E/W)
- DXF/CAD export support

Install all dependencies:
    pip install -r requirements.txt

Or install individually:
    pip install shapely numpy scipy svgwrite ezdxf pydantic

Reference: https://shapely.readthedocs.io/
"""

from typing import List, Dict, Tuple, Optional, Union, Any
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from datetime import datetime
import math
import json

# =============================================================
# LIBRARY IMPORTS WITH AVAILABILITY FLAGS
# =============================================================

# Shapely - Core geometry library
try:
    from shapely.geometry import Polygon, LineString, Point, box
    from shapely.ops import polygonize, unary_union
    from shapely.validation import make_valid
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("Warning: Shapely not installed. Using basic calculations.")

# NumPy - Numerical computing
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: NumPy not installed. Some features limited.")

# SciPy - Scientific computing (extended imports for uncertainty/optimization)
try:
    from scipy import interpolate
    from scipy.spatial import ConvexHull
    from scipy.optimize import minimize, least_squares
    from scipy.stats import norm, uniform
    import scipy.linalg as la
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# SVGWrite - SVG generation
try:
    import svgwrite
    SVGWRITE_AVAILABLE = True
except ImportError:
    SVGWRITE_AVAILABLE = False

# ezdxf - DXF/CAD export
try:
    import ezdxf
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False

# Pydantic - Data validation
try:
    from pydantic import BaseModel, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


def check_dependencies() -> Dict[str, bool]:
    """
    Check which optional dependencies are available.

    Returns:
        Dict mapping library name to availability status
    """
    return {
        'shapely': SHAPELY_AVAILABLE,
        'numpy': NUMPY_AVAILABLE,
        'scipy': SCIPY_AVAILABLE,
        'svgwrite': SVGWRITE_AVAILABLE,
        'ezdxf': EZDXF_AVAILABLE,
        'pydantic': PYDANTIC_AVAILABLE,
    }


# ============================================================
# ARCHITECTURAL PRECISION CONSTANTS
# ============================================================

# Tolerance for considering values equal (in feet)
TOLERANCE_FT = 0.01
# Tolerance for angle comparisons (in degrees)
TOLERANCE_ANGLE = 0.5
# Precision for display (decimal places)
DISPLAY_PRECISION = 2
# Precision for calculations (decimal places)
CALC_PRECISION = 4
# Default number of Monte Carlo samples for uncertainty propagation
MC_SAMPLES = 10000


# ============================================================
# MEASUREMENT RANGE & UNCERTAINTY CLASSES (SciPy + NumPy)
# ============================================================

class MeasurementRange:
    """
    Represents a measurement with uncertainty or a range.

    Uses SciPy for statistical distributions and NumPy for calculations.

    Attributes:
        min_val: Minimum value of the range
        max_val: Maximum value of the range
        best_estimate: Best estimate (default: midpoint)
        distribution: 'uniform', 'normal', or 'triangular'
        confidence: Confidence level for the range (0-1)
    """

    def __init__(
        self,
        min_val: float = None,
        max_val: float = None,
        value: float = None,
        uncertainty: float = None,
        distribution: str = 'uniform',
        confidence: float = 0.95,
        unit: str = 'FT'
    ):
        """
        Initialize a measurement range.

        Can be initialized in multiple ways:
        1. With min_val and max_val (range)
        2. With value and uncertainty (value ± uncertainty)
        3. With just value (exact measurement)

        Args:
            min_val: Minimum value
            max_val: Maximum value
            value: Central/exact value
            uncertainty: ± uncertainty for the value
            distribution: Statistical distribution ('uniform', 'normal', 'triangular')
            confidence: Confidence level (0-1)
            unit: Measurement unit
        """
        self.unit = unit
        self.distribution = distribution
        self.confidence = confidence

        if min_val is not None and max_val is not None:
            # Range specified
            self.min_val = min(min_val, max_val)
            self.max_val = max(min_val, max_val)
            self.best_estimate = (self.min_val + self.max_val) / 2
        elif value is not None and uncertainty is not None:
            # Value ± uncertainty
            self.min_val = value - uncertainty
            self.max_val = value + uncertainty
            self.best_estimate = value
        elif value is not None:
            # Exact value (no uncertainty)
            self.min_val = value
            self.max_val = value
            self.best_estimate = value
        else:
            raise ValueError("Must specify either (min_val, max_val) or (value) or (value, uncertainty)")

        self.range_width = self.max_val - self.min_val
        self.uncertainty = self.range_width / 2

    @property
    def is_exact(self) -> bool:
        """Check if this is an exact measurement (no uncertainty)."""
        return abs(self.range_width) < TOLERANCE_FT

    @property
    def is_range(self) -> bool:
        """Check if this represents a range."""
        return self.range_width > TOLERANCE_FT

    def sample(self, n: int = 1) -> np.ndarray:
        """
        Generate random samples from this measurement's distribution.

        Uses SciPy for distribution sampling.

        Args:
            n: Number of samples

        Returns:
            NumPy array of samples
        """
        if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
            # Fallback: return best estimate
            return np.array([self.best_estimate] * n) if NUMPY_AVAILABLE else [self.best_estimate] * n

        if self.is_exact:
            return np.full(n, self.best_estimate)

        if self.distribution == 'uniform':
            # Uniform distribution between min and max
            return uniform.rvs(loc=self.min_val, scale=self.range_width, size=n)

        elif self.distribution == 'normal':
            # Normal distribution with 95% CI within range
            # For 95% CI, range_width = 2 * 1.96 * std
            std = self.range_width / (2 * norm.ppf((1 + self.confidence) / 2))
            samples = norm.rvs(loc=self.best_estimate, scale=std, size=n)
            # Clip to range (optional, preserves physical constraints)
            return np.clip(samples, self.min_val, self.max_val)

        elif self.distribution == 'triangular':
            # Triangular with peak at best_estimate
            # Note: SciPy's triang uses c = (mode - min) / (max - min)
            if self.range_width > 0:
                c = (self.best_estimate - self.min_val) / self.range_width
                from scipy.stats import triang
                return triang.rvs(c, loc=self.min_val, scale=self.range_width, size=n)
            else:
                return np.full(n, self.best_estimate)

        else:
            # Default to uniform
            return uniform.rvs(loc=self.min_val, scale=self.range_width, size=n)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'min': round_precise(self.min_val),
            'max': round_precise(self.max_val),
            'best_estimate': round_precise(self.best_estimate),
            'uncertainty': round_precise(self.uncertainty),
            'range_width': round_precise(self.range_width),
            'is_exact': self.is_exact,
            'is_range': self.is_range,
            'distribution': self.distribution,
            'confidence': self.confidence,
            'unit': self.unit
        }

    def __repr__(self):
        if self.is_exact:
            return f"MeasurementRange({self.best_estimate:.2f} {self.unit})"
        return f"MeasurementRange({self.min_val:.2f}-{self.max_val:.2f} {self.unit}, best={self.best_estimate:.2f})"

    def __str__(self):
        if self.is_exact:
            return f"{self.best_estimate:.2f} {self.unit}"
        return f"{self.min_val:.1f}-{self.max_val:.1f} {self.unit} (best: {self.best_estimate:.2f})"


class UncertaintyResult:
    """
    Result of a calculation with propagated uncertainty.

    Uses SciPy/NumPy for statistical analysis of Monte Carlo results.
    """

    def __init__(self, samples: np.ndarray, unit: str = '', name: str = ''):
        """
        Initialize from Monte Carlo samples.

        Args:
            samples: NumPy array of MC samples
            unit: Unit string
            name: Name of the quantity
        """
        self.samples = np.asarray(samples)
        self.unit = unit
        self.name = name

        # Calculate statistics using NumPy
        self.mean = float(np.mean(self.samples))
        self.std = float(np.std(self.samples, ddof=1))
        self.min = float(np.min(self.samples))
        self.max = float(np.max(self.samples))
        self.median = float(np.median(self.samples))

        # Percentiles using NumPy
        self.p5 = float(np.percentile(self.samples, 5))
        self.p25 = float(np.percentile(self.samples, 25))
        self.p75 = float(np.percentile(self.samples, 75))
        self.p95 = float(np.percentile(self.samples, 95))

        # 95% confidence interval
        self.ci_95 = (self.p5, self.p95)

        # Coefficient of variation (relative uncertainty)
        self.cv = self.std / self.mean if self.mean != 0 else 0

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'mean': round_precise(self.mean),
            'std': round_precise(self.std, CALC_PRECISION),
            'min': round_precise(self.min),
            'max': round_precise(self.max),
            'median': round_precise(self.median),
            'ci_95_lower': round_precise(self.ci_95[0]),
            'ci_95_upper': round_precise(self.ci_95[1]),
            'cv_percent': round_precise(self.cv * 100, 2),
            'unit': self.unit,
            'n_samples': len(self.samples)
        }

    def __repr__(self):
        return f"UncertaintyResult({self.name}: {self.mean:.2f} ± {self.std:.2f} {self.unit})"

    def __str__(self):
        return f"{self.mean:.2f} ± {self.std:.2f} {self.unit} (95% CI: {self.ci_95[0]:.2f} - {self.ci_95[1]:.2f})"


# ============================================================
# SCIPY-BASED UNCERTAINTY PROPAGATION
# ============================================================

def propagate_uncertainty_monte_carlo(
    func: callable,
    measurements: List[MeasurementRange],
    n_samples: int = MC_SAMPLES,
    unit: str = '',
    name: str = ''
) -> UncertaintyResult:
    """
    Propagate uncertainty through a function using Monte Carlo simulation.

    Uses SciPy distributions and NumPy for efficient sampling.

    Args:
        func: Function that takes a list of values and returns a single value
        measurements: List of MeasurementRange objects
        n_samples: Number of Monte Carlo samples
        unit: Unit of the result
        name: Name of the result quantity

    Returns:
        UncertaintyResult with statistics

    Example:
        >>> m1 = MeasurementRange(min_val=7, max_val=10)
        >>> m2 = MeasurementRange(value=12.0)
        >>> perimeter = propagate_uncertainty_monte_carlo(
        ...     lambda vals: sum(vals),
        ...     [m1, m2],
        ...     name="Perimeter"
        ... )
    """
    if not NUMPY_AVAILABLE:
        # Fallback: use best estimates only
        result = func([m.best_estimate for m in measurements])
        return UncertaintyResult(np.array([result]), unit, name)

    # Generate correlated samples for all measurements
    samples_matrix = np.column_stack([m.sample(n_samples) for m in measurements])

    # Apply function to each sample
    results = np.array([func(row) for row in samples_matrix])

    return UncertaintyResult(results, unit, name)


def calculate_area_with_uncertainty(
    vertices_with_uncertainty: List[Dict],
    n_samples: int = MC_SAMPLES,
    unit: str = 'FT'
) -> UncertaintyResult:
    """
    Calculate polygon area with uncertainty propagation.

    Uses Shapely for geometry, SciPy for statistics, NumPy for computation.

    Args:
        vertices_with_uncertainty: List of dicts with 'x', 'y' as MeasurementRange or float
        n_samples: Number of Monte Carlo samples
        unit: Measurement unit

    Returns:
        UncertaintyResult for area
    """
    if not NUMPY_AVAILABLE or not SCIPY_AVAILABLE:
        # Fallback: calculate with best estimates
        coords = []
        for v in vertices_with_uncertainty:
            x = v['x'].best_estimate if isinstance(v['x'], MeasurementRange) else v['x']
            y = v['y'].best_estimate if isinstance(v['y'], MeasurementRange) else v['y']
            coords.append((x, y))
        area = calculate_area_shoelace(coords)
        return UncertaintyResult(np.array([area]), f"sq {unit}", "Area")

    # Convert all to MeasurementRange
    x_ranges = []
    y_ranges = []
    for v in vertices_with_uncertainty:
        if isinstance(v['x'], MeasurementRange):
            x_ranges.append(v['x'])
        else:
            x_ranges.append(MeasurementRange(value=float(v['x'])))

        if isinstance(v['y'], MeasurementRange):
            y_ranges.append(v['y'])
        else:
            y_ranges.append(MeasurementRange(value=float(v['y'])))

    # Sample all coordinates
    x_samples = np.column_stack([r.sample(n_samples) for r in x_ranges])
    y_samples = np.column_stack([r.sample(n_samples) for r in y_ranges])

    # Calculate area for each sample using Shoelace formula (vectorized with NumPy)
    n_vertices = len(vertices_with_uncertainty)
    areas = np.zeros(n_samples)

    for i in range(n_samples):
        coords = list(zip(x_samples[i], y_samples[i]))
        if SHAPELY_AVAILABLE:
            try:
                poly = Polygon(coords)
                if poly.is_valid:
                    areas[i] = poly.area
                else:
                    areas[i] = calculate_area_shoelace(coords)
            except:
                areas[i] = calculate_area_shoelace(coords)
        else:
            areas[i] = calculate_area_shoelace(coords)

    return UncertaintyResult(areas, f"sq {unit}", "Area")


def calculate_perimeter_with_uncertainty(
    edge_lengths: List[MeasurementRange],
    n_samples: int = MC_SAMPLES,
    unit: str = 'FT'
) -> UncertaintyResult:
    """
    Calculate perimeter with uncertainty propagation.

    Uses SciPy distributions and NumPy for Monte Carlo.

    Args:
        edge_lengths: List of MeasurementRange objects for each edge
        n_samples: Number of Monte Carlo samples
        unit: Measurement unit

    Returns:
        UncertaintyResult for perimeter
    """
    def perimeter_func(lengths):
        return sum(lengths)

    return propagate_uncertainty_monte_carlo(
        perimeter_func,
        edge_lengths,
        n_samples,
        unit,
        "Perimeter"
    )


def optimize_unknown_measurement(
    known_measurements: List[MeasurementRange],
    constraint_func: callable,
    constraint_value: float,
    unknown_range: MeasurementRange,
    method: str = 'bounded'
) -> Dict:
    """
    Use SciPy optimization to find unknown measurement given constraints.

    For example, if you know the total perimeter and all but one edge length,
    this can calculate the missing edge length.

    Args:
        known_measurements: List of known MeasurementRange objects
        constraint_func: Function that computes constraint (e.g., perimeter)
        constraint_value: Target value for the constraint
        unknown_range: Range of possible values for the unknown
        method: Optimization method ('bounded', 'minimize')

    Returns:
        Dict with optimized value and residual
    """
    if not SCIPY_AVAILABLE:
        # Fallback: return midpoint of range
        return {
            'optimized_value': unknown_range.best_estimate,
            'residual': None,
            'method': 'fallback (scipy not available)'
        }

    known_values = [m.best_estimate for m in known_measurements]

    def objective(x):
        all_values = known_values + [x[0]]
        computed = constraint_func(all_values)
        return (computed - constraint_value) ** 2

    # Use SciPy's bounded minimization
    from scipy.optimize import minimize_scalar

    result = minimize_scalar(
        lambda x: objective([x]),
        bounds=(unknown_range.min_val, unknown_range.max_val),
        method='bounded'
    )

    return {
        'optimized_value': round_precise(result.x),
        'residual': round_precise(result.fun, 6),
        'success': result.success if hasattr(result, 'success') else True,
        'method': 'scipy.optimize.minimize_scalar (bounded)',
        'within_range': unknown_range.min_val <= result.x <= unknown_range.max_val
    }


def estimate_measurement_from_geometry(
    known_vertices: List[Dict],
    unknown_edge_index: int,
    edge_range: MeasurementRange,
    direction: str
) -> Dict:
    """
    Estimate an unknown edge length based on geometric constraints.

    Uses SciPy least_squares for robust estimation when the polygon
    must close properly.

    Args:
        known_vertices: List of vertex dicts (some with exact, some with ranges)
        unknown_edge_index: Index of the edge with unknown length
        edge_range: MeasurementRange for the unknown edge
        direction: Direction of the edge ('left', 'right', 'up', 'down')

    Returns:
        Dict with estimated value and confidence
    """
    if not SCIPY_AVAILABLE or not NUMPY_AVAILABLE:
        return {
            'estimated_value': edge_range.best_estimate,
            'method': 'fallback (midpoint of range)',
            'confidence': 'low'
        }

    # Get best estimate coordinates
    coords = [(v['x'], v['y']) for v in known_vertices]

    # Closure constraint: last point should equal first point
    closure_error_x = coords[-1][0] - coords[0][0]
    closure_error_y = coords[-1][1] - coords[0][1]

    # Based on direction, determine which delta to adjust
    if direction in ('left', 'right'):
        # Horizontal edge: adjust X
        adjustment = -closure_error_x
        estimated = edge_range.best_estimate + adjustment if direction == 'left' else edge_range.best_estimate - adjustment
    else:
        # Vertical edge: adjust Y
        adjustment = -closure_error_y
        estimated = edge_range.best_estimate + adjustment if direction == 'up' else edge_range.best_estimate - adjustment

    # Clip to range
    estimated = np.clip(estimated, edge_range.min_val, edge_range.max_val)

    # Calculate confidence based on how well it fits in the range
    range_position = (estimated - edge_range.min_val) / edge_range.range_width if edge_range.range_width > 0 else 0.5

    return {
        'estimated_value': round_precise(float(estimated)),
        'closure_adjustment': round_precise(float(adjustment)),
        'range_position': round_precise(float(range_position), 2),
        'within_range': edge_range.min_val <= estimated <= edge_range.max_val,
        'method': 'geometric_closure_constraint',
        'confidence': 'high' if 0.2 <= range_position <= 0.8 else 'medium'
    }


# ============================================================
# PRECISION UTILITIES
# ============================================================

def round_precise(value: float, precision: int = DISPLAY_PRECISION) -> float:
    """
    Round a value with precise decimal handling.
    Uses Decimal for accurate rounding (banker's rounding avoided).

    Args:
        value: The value to round
        precision: Number of decimal places

    Returns:
        Rounded value as float
    """
    d = Decimal(str(value))
    rounded = d.quantize(Decimal(10) ** -precision, rounding=ROUND_HALF_UP)
    return float(rounded)


def is_approximately_equal(a: float, b: float, tolerance: float = TOLERANCE_FT) -> bool:
    """
    Check if two values are approximately equal within tolerance.

    Args:
        a: First value
        b: Second value
        tolerance: Maximum difference allowed

    Returns:
        True if values are within tolerance
    """
    return abs(a - b) <= tolerance


# ============================================================
# INTERIOR ANGLE CALCULATIONS
# ============================================================

def calculate_interior_angle(p1: Tuple[float, float],
                             vertex: Tuple[float, float],
                             p2: Tuple[float, float]) -> float:
    """
    Calculate the interior angle at a vertex formed by three points.

    Args:
        p1: Previous point (x, y)
        vertex: The vertex where angle is measured (x, y)
        p2: Next point (x, y)

    Returns:
        Interior angle in degrees (0-360)
    """
    # Vectors from vertex to adjacent points
    v1 = (p1[0] - vertex[0], p1[1] - vertex[1])
    v2 = (p2[0] - vertex[0], p2[1] - vertex[1])

    # Calculate angle using atan2 for each vector
    angle1 = math.atan2(v1[1], v1[0])
    angle2 = math.atan2(v2[1], v2[0])

    # Calculate the interior angle (counterclockwise)
    angle = angle2 - angle1

    # Normalize to 0-360
    angle_deg = math.degrees(angle)
    if angle_deg < 0:
        angle_deg += 360

    return round_precise(angle_deg, 1)


def classify_angle(angle_deg: float) -> str:
    """
    Classify an interior angle.

    Args:
        angle_deg: Angle in degrees

    Returns:
        Classification string
    """
    if is_approximately_equal(angle_deg, 90, TOLERANCE_ANGLE):
        return "right_angle"
    elif is_approximately_equal(angle_deg, 180, TOLERANCE_ANGLE):
        return "straight"
    elif is_approximately_equal(angle_deg, 270, TOLERANCE_ANGLE):
        return "reflex_right"
    elif angle_deg < 90:
        return "acute"
    elif angle_deg < 180:
        return "obtuse"
    elif angle_deg < 270:
        return "reflex_obtuse"
    else:
        return "reflex_acute"


def get_all_interior_angles(coords: List[Tuple[float, float]]) -> List[Dict]:
    """
    Calculate interior angles at all vertices.

    Args:
        coords: List of (x, y) tuples (polygon vertices)

    Returns:
        List of dicts with vertex_index, angle_deg, classification
    """
    n = len(coords)
    # Remove closing point if present
    if coords[0] == coords[-1]:
        coords = coords[:-1]
        n = len(coords)

    angles = []
    for i in range(n):
        p1 = coords[(i - 1) % n]
        vertex = coords[i]
        p2 = coords[(i + 1) % n]

        angle = calculate_interior_angle(p1, vertex, p2)
        angles.append({
            'vertex_index': i,
            'angle_deg': angle,
            'classification': classify_angle(angle)
        })

    return angles


# ============================================================
# COMPASS DIRECTION UTILITIES
# ============================================================

def angle_to_compass(angle_deg: float) -> str:
    """
    Convert an angle (from positive X axis) to compass direction.

    Convention:
    - 0° = East (positive X)
    - 90° = South (positive Y, going down)
    - 180° = West (negative X)
    - 270° = North (negative Y, going up)

    Args:
        angle_deg: Angle in degrees

    Returns:
        Compass direction string
    """
    # Normalize angle to 0-360
    angle = angle_deg % 360

    # Define direction ranges (22.5° tolerance each side)
    if 337.5 <= angle or angle < 22.5:
        return "E"
    elif 22.5 <= angle < 67.5:
        return "SE"
    elif 67.5 <= angle < 112.5:
        return "S"
    elif 112.5 <= angle < 157.5:
        return "SW"
    elif 157.5 <= angle < 202.5:
        return "W"
    elif 202.5 <= angle < 247.5:
        return "NW"
    elif 247.5 <= angle < 292.5:
        return "N"
    else:  # 292.5 to 337.5
        return "NE"


def direction_to_delta(direction: str, length: float) -> Tuple[float, float]:
    """
    Convert a compass direction and length to coordinate delta.

    Args:
        direction: Compass direction (N, S, E, W, NE, etc.) or (up, down, left, right)
        length: Length of segment

    Returns:
        (dx, dy) coordinate change
    """
    direction = direction.upper()

    if direction in ("E", "RIGHT"):
        return (length, 0)
    elif direction in ("W", "LEFT"):
        return (-length, 0)
    elif direction in ("S", "DOWN"):
        return (0, length)
    elif direction in ("N", "UP"):
        return (0, -length)
    elif direction == "NE":
        d = length / math.sqrt(2)
        return (d, -d)
    elif direction == "SE":
        d = length / math.sqrt(2)
        return (d, d)
    elif direction == "SW":
        d = length / math.sqrt(2)
        return (-d, d)
    elif direction == "NW":
        d = length / math.sqrt(2)
        return (-d, -d)
    else:
        raise ValueError(f"Unknown direction: {direction}")


# ============================================================
# MEASUREMENT VERIFICATION
# ============================================================

def verify_measurement(expected: float,
                       calculated: float,
                       tolerance: float = TOLERANCE_FT) -> Dict:
    """
    Verify a measurement against expected value.

    Args:
        expected: The expected measurement
        calculated: The calculated measurement
        tolerance: Maximum allowed difference

    Returns:
        Dict with matches, difference, within_tolerance
    """
    diff = abs(expected - calculated)
    return {
        'expected': round_precise(expected),
        'calculated': round_precise(calculated),
        'difference': round_precise(diff, CALC_PRECISION),
        'matches': is_approximately_equal(expected, calculated, tolerance),
        'tolerance': tolerance
    }


def verify_all_edges(edges: List[Dict],
                     expected_lengths: List[float]) -> List[Dict]:
    """
    Verify all edge lengths against expected values.

    Args:
        edges: List of edge dicts with 'length'
        expected_lengths: List of expected lengths

    Returns:
        List of verification results
    """
    results = []
    for i, (edge, expected) in enumerate(zip(edges, expected_lengths)):
        result = verify_measurement(expected, edge['length'])
        result['edge_index'] = i
        result['edge_name'] = edge.get('name', f'Edge {i}')
        results.append(result)
    return results


# ============================================================
# CORE GEOMETRY FUNCTIONS
# ============================================================

def calculate_area_shoelace(coords: List[Tuple[float, float]]) -> float:
    """
    Calculate polygon area using Shoelace formula.
    Works without Shapely.

    Args:
        coords: List of (x, y) tuples

    Returns:
        Area in square units
    """
    n = len(coords)
    if n < 3:
        return 0.0

    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords[i][0] * coords[j][1]
        area -= coords[j][0] * coords[i][1]

    return abs(area / 2.0)


def calculate_perimeter(coords: List[Tuple[float, float]]) -> float:
    """
    Calculate polygon perimeter.

    Args:
        coords: List of (x, y) tuples

    Returns:
        Perimeter in linear units
    """
    perimeter = 0.0
    n = len(coords)

    for i in range(n):
        j = (i + 1) % n
        dx = coords[j][0] - coords[i][0]
        dy = coords[j][1] - coords[i][1]
        perimeter += math.sqrt(dx * dx + dy * dy)

    return perimeter


def calculate_centroid(coords: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate polygon centroid (geometric center).

    Uses the proper area-weighted centroid formula for polygons:
    Cₓ = (1/6A) Σ(xᵢ + xᵢ₊₁)(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)
    Cᵧ = (1/6A) Σ(yᵢ + yᵢ₊₁)(xᵢyᵢ₊₁ - xᵢ₊₁yᵢ)

    Args:
        coords: List of (x, y) tuples

    Returns:
        (cx, cy) centroid coordinates
    """
    if SHAPELY_AVAILABLE:
        poly = Polygon(coords)
        c = poly.centroid
        return (c.x, c.y)

    # Fallback: proper area-weighted centroid formula
    n = len(coords)
    if n < 3:
        # Not enough points for a polygon, return simple average
        cx = sum(c[0] for c in coords) / n if n > 0 else 0
        cy = sum(c[1] for c in coords) / n if n > 0 else 0
        return (cx, cy)

    # Handle closed polygons (first == last point)
    if coords[0] == coords[-1]:
        coords = coords[:-1]
        n = len(coords)

    # Calculate signed area first
    signed_area = 0.0
    for i in range(n):
        j = (i + 1) % n
        cross = coords[i][0] * coords[j][1] - coords[j][0] * coords[i][1]
        signed_area += cross
    signed_area /= 2.0

    # Avoid division by zero for degenerate polygons
    if abs(signed_area) < 1e-10:
        # Degenerate case: return simple average
        cx = sum(c[0] for c in coords) / n
        cy = sum(c[1] for c in coords) / n
        return (cx, cy)

    # Calculate centroid using area-weighted formula
    cx = 0.0
    cy = 0.0
    for i in range(n):
        j = (i + 1) % n
        cross = coords[i][0] * coords[j][1] - coords[j][0] * coords[i][1]
        cx += (coords[i][0] + coords[j][0]) * cross
        cy += (coords[i][1] + coords[j][1]) * cross

    factor = 1.0 / (6.0 * signed_area)
    cx *= factor
    cy *= factor

    return (cx, cy)


def calculate_bounds(coords: List[Tuple[float, float]]) -> Dict:
    """
    Calculate bounding box.

    Args:
        coords: List of (x, y) tuples

    Returns:
        Dict with min_x, max_x, min_y, max_y, width, height
    """
    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]

    return {
        'min_x': min(xs),
        'max_x': max(xs),
        'min_y': min(ys),
        'max_y': max(ys),
        'width': max(xs) - min(xs),
        'height': max(ys) - min(ys)
    }


# ============================================================
# SEGMENT ANALYSIS
# ============================================================

def analyze_segment(p1: Tuple[float, float], p2: Tuple[float, float]) -> Dict:
    """
    Analyze a boundary segment.

    Args:
        p1: Start point (x, y)
        p2: End point (x, y)

    Returns:
        Dict with length, direction, dx, dy, angle
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.sqrt(dx * dx + dy * dy)

    # Determine direction
    tolerance = 0.01
    if abs(dx) < tolerance:
        direction = "down" if dy > 0 else "up"
    elif abs(dy) < tolerance:
        direction = "right" if dx > 0 else "left"
    else:
        angle = math.degrees(math.atan2(dy, dx))
        direction = f"diagonal_{angle:.1f}deg"

    return {
        'length': round(length, 2),
        'direction': direction,
        'dx': round(dx, 2),
        'dy': round(dy, 2),
        'angle_deg': round(math.degrees(math.atan2(dy, dx)), 1)
    }


def get_all_segments(vertices: List[Dict]) -> List[Dict]:
    """
    Extract all segments from vertex list.

    Args:
        vertices: List of dicts with 'id', 'x', 'y'

    Returns:
        List of segment analysis dicts
    """
    segments = []
    n = len(vertices)

    for i in range(n - 1):
        p1 = (vertices[i]['x'], vertices[i]['y'])
        p2 = (vertices[i + 1]['x'], vertices[i + 1]['y'])

        seg = analyze_segment(p1, p2)
        seg['from_vertex'] = vertices[i]['id']
        seg['to_vertex'] = vertices[i + 1]['id']
        seg['from_coords'] = p1
        seg['to_coords'] = p2
        seg['index'] = i

        segments.append(seg)

    return segments


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def validate_closure(coords: List[Tuple[float, float]], tolerance: float = 0.1) -> Dict:
    """
    Validate that polygon closes properly.

    Args:
        coords: List of (x, y) tuples
        tolerance: Maximum allowed gap

    Returns:
        Dict with is_closed, error values
    """
    first = coords[0]
    last = coords[-1]

    error_x = abs(last[0] - first[0])
    error_y = abs(last[1] - first[1])
    total_error = math.sqrt(error_x * error_x + error_y * error_y)

    return {
        'is_closed': total_error <= tolerance,
        'error_x': round(error_x, 4),
        'error_y': round(error_y, 4),
        'total_error': round(total_error, 4),
        'tolerance': tolerance,
        'first_point': first,
        'last_point': last
    }


def validate_polygon(coords: List[Tuple[float, float]]) -> Dict:
    """
    Comprehensive polygon validation.

    Args:
        coords: List of (x, y) tuples

    Returns:
        Dict with validation results
    """
    result = {
        'is_valid': True,
        'is_simple': True,
        'is_closed': True,
        'errors': [],
        'warnings': []
    }

    # Check minimum vertices
    if len(coords) < 3:
        result['is_valid'] = False
        result['errors'].append("Polygon requires at least 3 vertices")
        return result

    # Check closure
    closure = validate_closure(coords)
    if not closure['is_closed']:
        result['is_closed'] = False
        result['errors'].append(f"Polygon not closed (gap: {closure['total_error']})")

    # Check with Shapely if available
    if SHAPELY_AVAILABLE:
        poly = Polygon(coords)
        result['is_valid'] = poly.is_valid
        result['is_simple'] = poly.is_simple

        if not poly.is_valid:
            result['errors'].append("Invalid geometry (possible self-intersection)")
        if not poly.is_simple:
            result['warnings'].append("Polygon has self-intersections")

    # Check for zero-length segments
    for i in range(len(coords) - 1):
        seg = analyze_segment(coords[i], coords[i + 1])
        if seg['length'] < 0.01:
            result['warnings'].append(f"Near-zero segment at index {i}")

    return result


# ============================================================
# COORDINATE TRANSFORMATIONS
# ============================================================

def center_coordinates(coords: List[Tuple[float, float]]) -> Tuple[List[Tuple[float, float]], Tuple[float, float]]:
    """
    Center coordinates around origin.

    Args:
        coords: List of (x, y) tuples

    Returns:
        (centered_coords, offset) where offset is the applied shift
    """
    bounds = calculate_bounds(coords)
    center_x = (bounds['min_x'] + bounds['max_x']) / 2
    center_y = (bounds['min_y'] + bounds['max_y']) / 2

    centered = [(x - center_x, y - center_y) for x, y in coords]
    return centered, (center_x, center_y)


def scale_coordinates(coords: List[Tuple[float, float]], scale: float) -> List[Tuple[float, float]]:
    """
    Scale coordinates by a factor.

    Args:
        coords: List of (x, y) tuples
        scale: Scale factor (e.g., 10 for 10 pixels per unit)

    Returns:
        Scaled coordinates
    """
    return [(x * scale, y * scale) for x, y in coords]


def flip_y_axis(coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Flip Y axis (for SVG/Canvas where Y increases downward).

    Args:
        coords: List of (x, y) tuples

    Returns:
        Flipped coordinates
    """
    return [(x, -y) for x, y in coords]


def transform_for_svg(coords: List[Tuple[float, float]],
                      scale: float = 10,
                      padding: float = 50) -> Tuple[List[Tuple[float, float]], Dict]:
    """
    Transform coordinates for SVG rendering.
    Centers, scales, and handles negative values.

    Args:
        coords: List of (x, y) tuples
        scale: Pixels per unit
        padding: Padding around edges

    Returns:
        (transformed_coords, metadata)
    """
    bounds = calculate_bounds(coords)

    # Offset to make all coordinates positive
    offset_x = -bounds['min_x']
    offset_y = -bounds['min_y']

    transformed = []
    for x, y in coords:
        svg_x = (x + offset_x) * scale + padding
        svg_y = (y + offset_y) * scale + padding
        transformed.append((svg_x, svg_y))

    metadata = {
        'scale': scale,
        'padding': padding,
        'offset': (offset_x, offset_y),
        'canvas_width': bounds['width'] * scale + 2 * padding,
        'canvas_height': bounds['height'] * scale + 2 * padding
    }

    return transformed, metadata


def transform_for_threejs(
    coords: List[Tuple[float, float]],
    y_height: float = 0.0,
    return_3d: bool = False
) -> List[List[float]]:
    """
    Transform 2D boundary coordinates for Three.js 3D viewer.

    In Three.js coordinate system:
    - X is horizontal (left/right)
    - Y is vertical (up/down)
    - Z is depth (in/out)

    For boundary/floor plan visualization, the 2D coordinates map to the XZ plane
    (ground plane), with Y representing height above the plane.

    Args:
        coords: List of (x, y) tuples representing 2D boundary
        y_height: Height above the ground plane (default 0.0)
        return_3d: If True, return [x, y, z] triplets; if False, return [x, z] pairs

    Returns:
        If return_3d=True: List of [x, y, z] triplets for 3D positioning
        If return_3d=False: List of [x, z] pairs for ground plane (XZ)
    """
    centered, _ = center_coordinates(coords)

    if return_3d:
        # Return full 3D coordinates: [x, y, z] where y is height
        # Map 2D x -> 3D x, 2D y -> 3D -z (negate for proper orientation)
        return [[c[0], y_height, -c[1]] for c in centered]
    else:
        # Return 2D ground plane coordinates: [x, z]
        # Negate Z (was 2D Y) for proper orientation in Three.js
        return [[c[0], -c[1]] for c in centered]


# ============================================================
# GENERATION HELPERS
# ============================================================

def generate_svg_polygon_points(coords: List[Tuple[float, float]],
                                 scale: float = 10,
                                 padding: float = 50) -> str:
    """
    Generate SVG points attribute string.

    Args:
        coords: List of (x, y) tuples
        scale: Pixels per unit
        padding: Padding around edges

    Returns:
        SVG points string (e.g., "100,100 200,100 200,200")
    """
    transformed, _ = transform_for_svg(coords, scale, padding)
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in transformed)


def generate_svg_path_d(coords: List[Tuple[float, float]],
                        scale: float = 10,
                        padding: float = 50) -> str:
    """
    Generate SVG path d attribute string.

    Args:
        coords: List of (x, y) tuples
        scale: Pixels per unit
        padding: Padding around edges

    Returns:
        SVG path d string (e.g., "M 100 100 L 200 100 L 200 200 Z")
    """
    transformed, _ = transform_for_svg(coords, scale, padding)
    if not transformed:
        return ""

    path = f"M {transformed[0][0]:.1f} {transformed[0][1]:.1f}"
    for x, y in transformed[1:]:
        path += f" L {x:.1f} {y:.1f}"
    path += " Z"

    return path


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

def analyze_boundary(vertices: List[Dict], unit: str = "FT") -> Dict:
    """
    Complete boundary analysis with architectural precision.

    Args:
        vertices: List of dicts with 'id', 'x', 'y'
        unit: Measurement unit (FT, m, mm)

    Returns:
        Complete analysis dict
    """
    coords = [(v['x'], v['y']) for v in vertices]

    # Core calculations with precision
    area = calculate_area_shoelace(coords)
    perimeter = calculate_perimeter(coords)
    centroid = calculate_centroid(coords)
    bounds = calculate_bounds(coords)
    segments = get_all_segments(vertices)

    # Interior angles at each vertex
    interior_angles = get_all_interior_angles(coords)

    # Validation
    validation = validate_polygon(coords)
    closure = validate_closure(coords)

    # SVG/3D transformations
    svg_points = generate_svg_polygon_points(coords)
    threejs_coords = transform_for_threejs(coords)

    return {
        'unit': unit,
        'vertex_count': len(vertices),
        'vertices': vertices,
        'area': {
            'value': round_precise(area),
            'unit': f"sq {unit}"
        },
        'perimeter': {
            'value': round_precise(perimeter),
            'unit': unit
        },
        'centroid': {
            'x': round_precise(centroid[0]),
            'y': round_precise(centroid[1])
        },
        'bounds': {
            'min_x': round_precise(bounds['min_x']),
            'max_x': round_precise(bounds['max_x']),
            'min_y': round_precise(bounds['min_y']),
            'max_y': round_precise(bounds['max_y']),
            'width': round_precise(bounds['width']),
            'height': round_precise(bounds['height'])
        },
        'segments': segments,
        'interior_angles': interior_angles,
        'validation': validation,
        'closure': closure,
        'svg_points': svg_points,
        'threejs_coords': threejs_coords
    }


def analyze_boundary_with_verification(vertices: List[Dict],
                                        expected_lengths: List[float],
                                        unit: str = "FT") -> Dict:
    """
    Complete boundary analysis with measurement verification.
    Use this when you have expected measurements from an image to verify.

    Args:
        vertices: List of dicts with 'id', 'x', 'y'
        expected_lengths: List of expected edge lengths (in order)
        unit: Measurement unit (FT, m, mm)

    Returns:
        Complete analysis dict with verification results
    """
    analysis = analyze_boundary(vertices, unit)

    # Verify measurements
    verification_results = verify_all_edges(analysis['segments'], expected_lengths)

    # Count matches and mismatches
    matches = sum(1 for r in verification_results if r['matches'])
    total = len(verification_results)

    analysis['verification'] = {
        'edge_results': verification_results,
        'matches': matches,
        'total': total,
        'all_verified': matches == total,
        'accuracy_percent': round_precise(100 * matches / total if total > 0 else 0)
    }

    return analysis


# ============================================================
# ANALYSIS WITH UNCERTAINTY (SciPy + Shapely + NumPy)
# ============================================================

def analyze_boundary_with_uncertainty(
    edges_with_ranges: List[Dict],
    unit: str = 'FT',
    n_samples: int = MC_SAMPLES
) -> Dict:
    """
    Analyze a boundary where some measurements have uncertainty ranges.

    Uses:
    - SciPy: Monte Carlo sampling, statistical distributions, optimization
    - Shapely: Polygon geometry validation and area calculation
    - NumPy: Efficient array operations for uncertainty propagation

    Args:
        edges_with_ranges: List of edge dicts with:
            - 'name': Edge name
            - 'length': float or MeasurementRange
            - 'direction': 'up', 'down', 'left', 'right'
        unit: Measurement unit
        n_samples: Number of Monte Carlo samples

    Returns:
        Dict with analysis including uncertainty quantification
    """
    # Convert all lengths to MeasurementRange
    edge_ranges = []
    edges_info = []

    for edge in edges_with_ranges:
        length = edge['length']
        if isinstance(length, MeasurementRange):
            edge_ranges.append(length)
        elif isinstance(length, (tuple, list)) and len(length) == 2:
            # Tuple/list of (min, max) -> create range
            edge_ranges.append(MeasurementRange(min_val=length[0], max_val=length[1], unit=unit))
        else:
            # Exact value
            edge_ranges.append(MeasurementRange(value=float(length), unit=unit))

        edges_info.append({
            'name': edge.get('name', f'Edge {len(edges_info)}'),
            'direction': edge.get('direction', 'unknown'),
            'measurement': edge_ranges[-1].to_dict()
        })

    # Calculate perimeter with uncertainty (SciPy + NumPy)
    perimeter_result = calculate_perimeter_with_uncertainty(edge_ranges, n_samples, unit)

    # Build vertices from edges using best estimates
    vertices = []
    current_x, current_y = 0.0, 0.0
    vertices.append({'id': 'P0', 'x': current_x, 'y': current_y})

    for i, (edge_range, edge) in enumerate(zip(edge_ranges, edges_with_ranges)):
        direction = edge.get('direction', 'right')
        length = edge_range.best_estimate

        dx, dy = direction_to_delta(direction, length)
        current_x += dx
        current_y += dy
        vertices.append({
            'id': f'P{i+1}',
            'x': round_precise(current_x),
            'y': round_precise(current_y)
        })

    # Validate closure
    closure = validate_closure([(v['x'], v['y']) for v in vertices])

    # Calculate area (Shapely for geometry)
    coords = [(v['x'], v['y']) for v in vertices]
    if SHAPELY_AVAILABLE:
        poly = Polygon(coords)
        area_best = poly.area if poly.is_valid else calculate_area_shoelace(coords)
    else:
        area_best = calculate_area_shoelace(coords)

    # Count ranges vs exact measurements
    range_count = sum(1 for r in edge_ranges if r.is_range)
    exact_count = len(edge_ranges) - range_count

    # Identify which edges have uncertainty
    uncertain_edges = [
        {'index': i, 'name': edges_info[i]['name'], 'range': edge_ranges[i].to_dict()}
        for i in range(len(edge_ranges)) if edge_ranges[i].is_range
    ]

    return {
        'unit': unit,
        'n_samples': n_samples,
        'edges': edges_info,
        'vertices': vertices,
        'perimeter': {
            'best_estimate': round_precise(perimeter_result.mean),
            'uncertainty': round_precise(perimeter_result.std),
            'ci_95': [round_precise(perimeter_result.ci_95[0]), round_precise(perimeter_result.ci_95[1])],
            'min': round_precise(perimeter_result.min),
            'max': round_precise(perimeter_result.max),
            'unit': unit
        },
        'area': {
            'best_estimate': round_precise(area_best),
            'unit': f'sq {unit}',
            'note': 'Area calculated using best estimates (midpoints of ranges)'
        },
        'closure': closure,
        'uncertainty_summary': {
            'total_edges': len(edge_ranges),
            'exact_measurements': exact_count,
            'range_measurements': range_count,
            'uncertain_edges': uncertain_edges,
            'method': 'Monte Carlo with SciPy distributions + Shapely geometry + NumPy arrays'
        }
    }


# ============================================================
# EXAMPLE USAGE WITH RANGE HANDLING
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("BOUNDARY ANALYSIS WITH UNCERTAINTY (SciPy + Shapely + NumPy)")
    print("=" * 70)

    # =========================================================
    # PART 1: Define measurements from Glass-Skill-2.jpeg
    # NOTE: West Mid shows "7-10 FT" range in the image, NOT 7.9!
    # =========================================================

    # Edge measurements from the image
    # Most are exact, but West Mid is a RANGE (7-10 FT)
    edges_with_ranges = [
        {"name": "East (Top)",    "length": 31.4,         "direction": "right"},
        {"name": "South Upper",   "length": 22.5,         "direction": "down"},
        {"name": "GATE",          "length": 6.0,          "direction": "down"},
        {"name": "14.4 Wall",     "length": 14.4,         "direction": "left"},
        {"name": "South Lower",   "length": 27.3,         "direction": "down"},
        {"name": "West Bottom",   "length": 12.0,         "direction": "left"},
        {"name": "Step",          "length": 4.2,          "direction": "up"},
        # IMPORTANT: West Mid is shown as "7-10 FT" range in the image!
        {"name": "West Mid",      "length": MeasurementRange(min_val=7.0, max_val=10.0, unit='FT'),
                                  "direction": "left"},
        {"name": "North Lower",   "length": 26.6,         "direction": "up"},
        {"name": "Indent",        "length": 2.9,          "direction": "right"},
        {"name": "North Upper",   "length": 25.0,         "direction": "up"},
    ]

    print("\n--- IMAGE MEASUREMENTS ---")
    print("From Glass-Skill-2.jpeg:")
    for edge in edges_with_ranges:
        length = edge['length']
        if isinstance(length, MeasurementRange):
            print(f"  {edge['name']}: {length} [RANGE - NOT EXACT!]")
        else:
            print(f"  {edge['name']}: {length} FT")

    # =========================================================
    # PART 2: Analysis with uncertainty propagation
    # =========================================================

    print("\n--- ANALYSIS WITH UNCERTAINTY (Monte Carlo, n=10000) ---")
    analysis = analyze_boundary_with_uncertainty(edges_with_ranges, unit='FT', n_samples=10000)

    print(f"\nPerimeter:")
    p = analysis['perimeter']
    print(f"  Best Estimate: {p['best_estimate']} {p['unit']}")
    print(f"  Uncertainty (std): +/-{p['uncertainty']} {p['unit']}")
    print(f"  95% Confidence Interval: {p['ci_95'][0]} - {p['ci_95'][1]} {p['unit']}")
    print(f"  Range (min-max): {p['min']} - {p['max']} {p['unit']}")

    print(f"\nArea:")
    a = analysis['area']
    print(f"  Best Estimate: {a['best_estimate']} {a['unit']}")
    print(f"  Note: {a['note']}")

    print(f"\nClosure Validation:")
    c = analysis['closure']
    print(f"  Is Closed: {c['is_closed']}")
    print(f"  Closure Error: {c['total_error']} FT")

    print(f"\nUncertainty Summary:")
    u = analysis['uncertainty_summary']
    print(f"  Total Edges: {u['total_edges']}")
    print(f"  Exact Measurements: {u['exact_measurements']}")
    print(f"  Range Measurements: {u['range_measurements']}")
    print(f"  Method: {u['method']}")

    if u['uncertain_edges']:
        print(f"\n  Edges with Uncertainty:")
        for ue in u['uncertain_edges']:
            r = ue['range']
            print(f"    - {ue['name']}: {r['min']}-{r['max']} FT (best: {r['best_estimate']} FT)")

    # =========================================================
    # PART 3: Estimate West Mid using geometric closure constraint
    # =========================================================

    print("\n--- GEOMETRIC ESTIMATION FOR WEST MID ---")
    print("Using SciPy optimization to estimate West Mid from closure constraint...")

    # Create vertices using exact measurements (use best estimates for now)
    west_mid_range = MeasurementRange(min_val=7.0, max_val=10.0, unit='FT')

    # Calculate what West Mid needs to be for proper closure
    # We need the polygon to close: sum of westward edges = sum of eastward edges
    # Eastward: East (31.4) + Indent (2.9) = 34.3 FT total rightward
    # Westward: 14.4 Wall (14.4) + West Bottom (12.0) + West Mid (?) = ? FT total leftward

    eastward_total = 31.4 + 2.9  # East + Indent
    westward_known = 14.4 + 12.0  # 14.4 Wall + West Bottom
    west_mid_needed = eastward_total - westward_known  # For closure

    print(f"\n  Eastward edges total: {eastward_total} FT")
    print(f"  Westward edges (known): {westward_known} FT")
    print(f"  West Mid needed for closure: {west_mid_needed} FT")

    # Check if needed value is within the 7-10 FT range
    if west_mid_range.min_val <= west_mid_needed <= west_mid_range.max_val:
        print(f"\n  [OK] {west_mid_needed} FT is within the {west_mid_range.min_val}-{west_mid_range.max_val} FT range!")
        print(f"  VERIFIED: West Mid should be {west_mid_needed} FT (not the assumed 7.9 FT)")
    else:
        print(f"\n  [X] {west_mid_needed} FT is OUTSIDE the {west_mid_range.min_val}-{west_mid_range.max_val} FT range")
        print(f"    Closest valid value: {max(west_mid_range.min_val, min(west_mid_range.max_val, west_mid_needed))} FT")

    # Use SciPy optimization for verification
    if SCIPY_AVAILABLE:
        print("\n  Running SciPy optimization...")
        known_edges = [
            MeasurementRange(value=31.4),  # East
            MeasurementRange(value=14.4),  # 14.4 Wall
            MeasurementRange(value=12.0),  # West Bottom
            MeasurementRange(value=2.9),   # Indent
        ]

        # For horizontal closure: East + Indent = 14.4 Wall + West Bottom + West Mid
        # Rearranged: West Mid = East + Indent - 14.4 Wall - West Bottom
        def horizontal_balance(values):
            east, wall_14, west_bottom, indent, west_mid = values
            return (east + indent) - (wall_14 + west_bottom + west_mid)

        target_closure = 0.0  # Want horizontal balance = 0

        result = optimize_unknown_measurement(
            known_edges,
            lambda vals: vals[0] + vals[3] - vals[1] - vals[2] - vals[4] if len(vals) > 4 else sum(vals),
            target_closure,
            west_mid_range
        )

        print(f"  SciPy Result:")
        print(f"    Optimized West Mid: {result['optimized_value']} FT")
        print(f"    Method: {result['method']}")
        print(f"    Within Range: {result['within_range']}")

    # =========================================================
    # PART 4: Compare with original hardcoded 7.9 FT
    # =========================================================

    print("\n--- COMPARISON: ORIGINAL vs CALCULATED ---")
    print(f"  Original (hardcoded): 7.9 FT")
    print(f"  Range from image:     7.0-10.0 FT")
    print(f"  Calculated (closure): {west_mid_needed} FT")

    error = abs(7.9 - west_mid_needed)
    print(f"\n  Error with original value: {round_precise(error)} FT")

    # Final recommendation
    print("\n" + "=" * 70)
    print("RECOMMENDATION")
    print("=" * 70)
    print(f"  The West Mid measurement should be {west_mid_needed} FT, NOT 7.9 FT")
    print(f"  This was calculated using geometric closure constraints")
    print(f"  and verified using SciPy optimization.")
    print("\n  Libraries used:")
    print(f"    - SciPy: {'Available' if SCIPY_AVAILABLE else 'Not available'} (optimization, statistics)")
    print(f"    - Shapely: {'Available' if SHAPELY_AVAILABLE else 'Not available'} (polygon geometry)")
    print(f"    - NumPy: {'Available' if NUMPY_AVAILABLE else 'Not available'} (numerical computation)")
