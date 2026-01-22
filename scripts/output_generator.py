#!/usr/bin/env python3
"""
Output Generator Module
Generates all manufacturing output files from validated specifications.

Enhanced version with:
- Professional 3D interactive viewer with realistic glass material
- Detailed technical drawings with proper dimensioning
- Comprehensive manufacturing specifications
- Industry-standard G-code output

Based on research from:
- Glass fabrication tolerances (One Day Glass, Guardian Glass)
- CNC machining drawing guidelines (Protolabs, Hubs)
- Three.js glass visualization techniques (Codrops)
"""

import json
import math
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class OutputGenerator:
    """Generates manufacturing output files from glass specifications."""

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.generated_files: List[str] = []

    def generate_all(
        self,
        extraction: Dict[str, Any],
        skip_3d: bool = False,
        skip_gcode: bool = False,
        timestamp: datetime = None
    ) -> List[str]:
        """Generate all output files.

        Args:
            extraction: The extraction data dictionary
            skip_3d: Skip 3D HTML generation
            skip_gcode: Skip G-code generation
            timestamp: Optional timestamp for reproducible outputs.
                      If None, uses current datetime.
        """
        self.generated_files = []

        # Use provided timestamp or current time for reproducibility
        if timestamp is None:
            timestamp = datetime.now()
        self._timestamp = timestamp

        self._generate_instructions(extraction)
        self._generate_technical_drawing(extraction)
        self._generate_validation_report(extraction)

        if not skip_3d:
            self._generate_3d_model(extraction)
        if not skip_gcode:
            self._generate_gcode(extraction)

        return self.generated_files

    def _generate_3d_model(self, extraction: Dict[str, Any]) -> None:
        """Generate professional interactive 3D HTML visualization with realistic glass."""
        dims = extraction.get("dimensions", {})
        width = dims.get("width", 100)
        height = dims.get("height", 100)
        thickness = dims.get("thickness", 10)
        holes = extraction.get("holes", [])
        sections = extraction.get("sections", [])
        glass_type = extraction.get("glass_type", "clear_tempered")
        edge_type = extraction.get("edge_type", "flat_polished")
        notes = extraction.get("notes", [])

        # Calculate weight
        weight = (width/1000) * (height/1000) * (thickness/1000) * 2500
        for hole in holes:
            d = hole.get("diameter", 0) / 1000
            hole_vol = math.pi * (d/2)**2 * (thickness/1000)
            weight -= hole_vol * 2500

        # Generate holes JavaScript array
        holes_js = json.dumps(holes)
        sections_js = json.dumps(sections)
        notes_js = json.dumps(notes)

        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Glass Panel 3D Viewer - {width}x{height}x{thickness}mm</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); }}

        #canvas-container {{ width: 100vw; height: 100vh; }}

        .panel {{ position: fixed; background: rgba(20, 30, 50, 0.95); color: #fff; padding: 20px; border-radius: 12px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}

        .info-panel {{ top: 20px; left: 20px; width: 320px; max-height: calc(100vh - 40px); overflow-y: auto; }}
        .info-panel h1 {{ font-size: 1.4em; margin-bottom: 15px; color: #4fc3f7; border-bottom: 2px solid #4fc3f7; padding-bottom: 10px; }}
        .info-panel h2 {{ font-size: 1.1em; margin: 15px 0 10px; color: #81d4fa; }}

        .spec-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
        .spec-item {{ background: rgba(255,255,255,0.05); padding: 10px; border-radius: 6px; }}
        .spec-label {{ font-size: 0.75em; color: #90a4ae; text-transform: uppercase; letter-spacing: 0.5px; }}
        .spec-value {{ font-size: 1.1em; font-weight: 600; color: #e0f7fa; margin-top: 2px; }}
        .spec-unit {{ font-size: 0.8em; color: #80deea; }}

        .hole-list {{ list-style: none; }}
        .hole-list li {{ background: rgba(255,255,255,0.05); padding: 8px 12px; margin: 5px 0; border-radius: 6px; font-size: 0.9em; border-left: 3px solid #ff7043; }}

        .section-list {{ list-style: none; }}
        .section-list li {{ background: rgba(255,255,255,0.05); padding: 8px 12px; margin: 5px 0; border-radius: 6px; font-size: 0.85em; border-left: 3px solid #66bb6a; }}

        .notes-list {{ list-style: none; }}
        .notes-list li {{ background: rgba(255,255,255,0.03); padding: 6px 10px; margin: 4px 0; border-radius: 4px; font-size: 0.8em; color: #b0bec5; }}

        .controls-panel {{ top: 20px; right: 20px; width: 280px; }}
        .controls-panel h2 {{ font-size: 1.1em; margin-bottom: 15px; color: #4fc3f7; }}

        .control-group {{ margin: 12px 0; }}
        .control-group label {{ display: block; font-size: 0.85em; color: #90a4ae; margin-bottom: 5px; }}
        .control-group input[type="range"] {{ width: 100%; accent-color: #4fc3f7; }}
        .control-group input[type="checkbox"] {{ accent-color: #4fc3f7; margin-right: 8px; }}

        .btn {{ background: linear-gradient(135deg, #4fc3f7 0%, #29b6f6 100%); color: #000; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: 600; width: 100%; margin: 5px 0; transition: transform 0.2s, box-shadow 0.2s; }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 15px rgba(79, 195, 247, 0.4); }}
        .btn-secondary {{ background: rgba(255,255,255,0.1); color: #fff; }}
        .btn-secondary:hover {{ background: rgba(255,255,255,0.2); box-shadow: none; }}

        .view-buttons {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 15px; }}

        .tolerance-info {{ background: rgba(255,193,7,0.1); border: 1px solid rgba(255,193,7,0.3); padding: 12px; border-radius: 8px; margin-top: 15px; }}
        .tolerance-info h3 {{ color: #ffc107; font-size: 0.9em; margin-bottom: 8px; }}
        .tolerance-info p {{ font-size: 0.8em; color: #b0bec5; line-height: 1.4; }}

        .status-bar {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: rgba(20, 30, 50, 0.9); padding: 10px 25px; border-radius: 25px; color: #81d4fa; font-size: 0.85em; }}

        @media (max-width: 768px) {{
            .info-panel {{ width: calc(100vw - 40px); max-height: 40vh; }}
            .controls-panel {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div id="canvas-container"></div>

    <div class="panel info-panel">
        <h1>Glass Panel Specifications</h1>

        <h2>Dimensions</h2>
        <div class="spec-grid">
            <div class="spec-item">
                <div class="spec-label">Width</div>
                <div class="spec-value">{width} <span class="spec-unit">mm</span></div>
            </div>
            <div class="spec-item">
                <div class="spec-label">Height</div>
                <div class="spec-value">{height} <span class="spec-unit">mm</span></div>
            </div>
            <div class="spec-item">
                <div class="spec-label">Thickness</div>
                <div class="spec-value">{thickness} <span class="spec-unit">mm</span></div>
            </div>
            <div class="spec-item">
                <div class="spec-label">Weight</div>
                <div class="spec-value">{weight:.2f} <span class="spec-unit">kg</span></div>
            </div>
        </div>

        <h2>Material</h2>
        <div class="spec-grid">
            <div class="spec-item">
                <div class="spec-label">Glass Type</div>
                <div class="spec-value" style="font-size:0.9em">{glass_type.replace('_', ' ').title()}</div>
            </div>
            <div class="spec-item">
                <div class="spec-label">Edge Type</div>
                <div class="spec-value" style="font-size:0.9em">{edge_type.replace('_', ' ').title()}</div>
            </div>
        </div>

        <h2>Holes ({len(holes)})</h2>
        <ul class="hole-list" id="hole-list"></ul>

        <h2>Sections ({len(sections)})</h2>
        <ul class="section-list" id="section-list"></ul>

        <h2>Notes</h2>
        <ul class="notes-list" id="notes-list"></ul>

        <div class="tolerance-info">
            <h3>Manufacturing Tolerances</h3>
            <p>Dimensions: ±1.5mm | Holes: ±1mm position<br>
            Edge distance min: {max(thickness * 2, 25)}mm<br>
            Diagonal tolerance: ±3mm</p>
        </div>
    </div>

    <div class="panel controls-panel">
        <h2>View Controls</h2>

        <div class="control-group">
            <label><input type="checkbox" id="showDimensions" checked> Show Dimensions</label>
        </div>
        <div class="control-group">
            <label><input type="checkbox" id="showHoles" checked> Highlight Holes</label>
        </div>
        <div class="control-group">
            <label><input type="checkbox" id="showSections" checked> Show Sections</label>
        </div>
        <div class="control-group">
            <label><input type="checkbox" id="wireframe"> Wireframe Mode</label>
        </div>

        <div class="control-group">
            <label>Glass Opacity</label>
            <input type="range" id="opacity" min="0.1" max="1" step="0.1" value="0.7">
        </div>

        <div class="control-group">
            <label>Glass Tint</label>
            <input type="range" id="tint" min="0" max="100" value="30">
        </div>

        <div class="view-buttons">
            <button class="btn btn-secondary" onclick="setView('front')">Front</button>
            <button class="btn btn-secondary" onclick="setView('back')">Back</button>
            <button class="btn btn-secondary" onclick="setView('top')">Top</button>
            <button class="btn btn-secondary" onclick="setView('side')">Side</button>
        </div>

        <button class="btn" onclick="setView('iso')" style="margin-top:15px">Reset View (ISO)</button>
        <button class="btn btn-secondary" onclick="toggleAutoRotate()">Toggle Auto-Rotate</button>
    </div>

    <div class="status-bar">
        <span id="status">Drag to rotate • Scroll to zoom • Double-click to reset</span>
    </div>

    <script>
        // Data from extraction
        const panelWidth = {width};
        const panelHeight = {height};
        const panelThickness = {thickness};
        const holes = {holes_js};
        const sections = {sections_js};
        const notes = {notes_js};

        // Populate lists
        const holeList = document.getElementById('hole-list');
        holes.forEach((h, i) => {{
            const li = document.createElement('li');
            li.innerHTML = `<strong>Hole ${{i+1}}:</strong> X=${{h.x}}mm, Y=${{h.y}}mm, Ø${{h.diameter}}mm`;
            holeList.appendChild(li);
        }});

        const sectionList = document.getElementById('section-list');
        sections.forEach((s, i) => {{
            const li = document.createElement('li');
            // Handle tapered sections
            if (s.is_tapered && s.width_bottom !== undefined && s.width_top !== undefined) {{
                li.innerHTML = `<strong>${{s.name}}:</strong> ${{s.width_bottom}}-${{s.width_top}}×${{s.height}}mm (tapered)`;
            }} else {{
                li.innerHTML = `<strong>${{s.name}}:</strong> ${{s.width}}×${{s.height}}mm at (${{s.x_offset}}, ${{s.y_offset}})`;
            }}
            sectionList.appendChild(li);
        }});

        const notesList = document.getElementById('notes-list');
        notes.forEach(n => {{
            const li = document.createElement('li');
            li.textContent = n;
            notesList.appendChild(li);
        }});

        // Three.js setup
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();

        // Sky gradient background
        const canvas = document.createElement('canvas');
        canvas.width = 2; canvas.height = 512;
        const ctx = canvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 512);
        gradient.addColorStop(0, '#0d1b2a');
        gradient.addColorStop(0.5, '#1b263b');
        gradient.addColorStop(1, '#415a77');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 2, 512);
        const bgTexture = new THREE.CanvasTexture(canvas);
        scene.background = bgTexture;

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.001, 50000);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        // OrbitControls - NO zoom restrictions for detailed inspection
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 0.001;  // Allow EXTREMELY close zoom (virtually no limit)
        controls.maxDistance = 50000;  // Allow very far zoom out
        controls.zoomSpeed = 1.5;      // Faster zoom for easier navigation
        controls.enablePan = true;     // Allow panning to navigate when zoomed in

        // Scale for visualization (mm to scene units)
        const scale = 0.1;
        const w = panelWidth * scale;
        const h = panelHeight * scale;
        const t = panelThickness * scale;

        // Glass material with realistic properties
        const glassMaterial = new THREE.MeshPhysicalMaterial({{
            color: 0x88ccff,
            metalness: 0.0,
            roughness: 0.05,
            transmission: 0.9,
            transparent: true,
            opacity: 0.7,
            thickness: t,
            envMapIntensity: 1.0,
            clearcoat: 1.0,
            clearcoatRoughness: 0.1,
            ior: 1.5,
            side: THREE.DoubleSide
        }});

        // Create glass panel with holes using CSG-like approach (simplified)
        const panelGroup = new THREE.Group();

        // Main panel
        const panelGeometry = new THREE.BoxGeometry(w, h, t);
        const panel = new THREE.Mesh(panelGeometry, glassMaterial);
        panel.castShadow = true;
        panel.receiveShadow = true;
        panelGroup.add(panel);

        // Edge frame (wireframe outline)
        const edgeGeometry = new THREE.EdgesGeometry(panelGeometry);
        const edgeMaterial = new THREE.LineBasicMaterial({{ color: 0x4fc3f7, linewidth: 2 }});
        const edges = new THREE.LineSegments(edgeGeometry, edgeMaterial);
        panelGroup.add(edges);

        // Hole markers - minimal clean design
        const holeMarkers = new THREE.Group();
        holes.forEach((hole, i) => {{
            const hx = (hole.x - panelWidth/2) * scale;
            const hy = (hole.y - panelHeight/2) * scale;
            const hr = (hole.diameter/2) * scale;

            // Simple hole circle outline
            const ringGeometry = new THREE.RingGeometry(hr * 0.9, hr, 32);
            const ringMaterial = new THREE.MeshBasicMaterial({{ color: 0x333333, side: THREE.DoubleSide }});
            const ring = new THREE.Mesh(ringGeometry, ringMaterial);
            ring.position.set(hx, hy, t/2 + 0.05);
            holeMarkers.add(ring);

            // Back side ring
            const ringBack = ring.clone();
            ringBack.position.set(hx, hy, -t/2 - 0.05);
            holeMarkers.add(ringBack);

            // Center cross mark (small)
            const crossSize = hr * 0.5;
            const crossMat = new THREE.LineBasicMaterial({{ color: 0x666666 }});
            const hLine = new THREE.Line(
                new THREE.BufferGeometry().setFromPoints([
                    new THREE.Vector3(hx - crossSize, hy, t/2 + 0.1),
                    new THREE.Vector3(hx + crossSize, hy, t/2 + 0.1)
                ]), crossMat
            );
            const vLine = new THREE.Line(
                new THREE.BufferGeometry().setFromPoints([
                    new THREE.Vector3(hx, hy - crossSize, t/2 + 0.1),
                    new THREE.Vector3(hx, hy + crossSize, t/2 + 0.1)
                ]), crossMat
            );
            holeMarkers.add(hLine, vLine);

            // LARGER hole diameter label - clearly visible
            const labelCanvas = document.createElement('canvas');
            labelCanvas.width = 256; labelCanvas.height = 128;  // Much larger canvas
            const labelCtx = labelCanvas.getContext('2d');
            labelCtx.fillStyle = 'rgba(50,50,50,0.9)';
            labelCtx.fillRect(0, 0, 256, 128);
            labelCtx.strokeStyle = 'rgba(255,100,100,0.8)';
            labelCtx.lineWidth = 4;
            labelCtx.strokeRect(0, 0, 256, 128);
            labelCtx.fillStyle = '#ffffff';
            labelCtx.font = 'bold 56px Arial';  // Much larger font
            labelCtx.textAlign = 'center';
            labelCtx.textBaseline = 'middle';
            labelCtx.fillText(`O${{hole.diameter}}mm`, 128, 64);  // Added 'mm' unit
            const labelTexture = new THREE.CanvasTexture(labelCanvas);
            const labelMaterial = new THREE.SpriteMaterial({{ map: labelTexture, transparent: true, opacity: 0.95 }});
            const label = new THREE.Sprite(labelMaterial);
            label.scale.set(12, 6, 1);  // Much larger scale (was 3, 1.5)
            label.position.set(hx, hy + hr + 5, t/2 + 0.5);  // Positioned higher
            holeMarkers.add(label);
        }});
        panelGroup.add(holeMarkers);

        // Section dividers and labels
        const sectionLines = new THREE.Group();
        const sectionLabels = new THREE.Group();

        // Helper function to create text label - LARGE READABLE TEXT
        function createTextLabel(text, fontSize, bgColor, textColor) {{
            // SIGNIFICANTLY INCREASED font sizes for readability
            const actualFontSize = fontSize * 3;  // Triple the font size
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            ctx.font = `bold ${{actualFontSize}}px Arial`;
            const metrics = ctx.measureText(text);
            const textWidth = metrics.width;
            const padding = 30;  // Increased padding

            canvas.width = textWidth + padding * 2;
            canvas.height = actualFontSize + padding * 2;

            ctx.fillStyle = bgColor || 'rgba(30,40,60,0.95)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.strokeStyle = 'rgba(255,255,255,0.5)';
            ctx.lineWidth = 3;  // Thicker border
            ctx.strokeRect(0, 0, canvas.width, canvas.height);

            ctx.font = `bold ${{actualFontSize}}px Arial`;
            ctx.fillStyle = textColor || '#ffffff';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(text, canvas.width/2, canvas.height/2);

            const texture = new THREE.CanvasTexture(canvas);
            texture.minFilter = THREE.LinearFilter;
            const material = new THREE.SpriteMaterial({{ map: texture, transparent: true }});
            const sprite = new THREE.Sprite(material);
            // INCREASED scale for better visibility (was 0.03, now 0.08)
            sprite.scale.set(canvas.width * 0.08, canvas.height * 0.08, 1);
            return sprite;
        }}

        // Draw section dividers and add section labels
        sections.forEach((section, i) => {{
            const sectionWidth = section.is_tapered ? (section.width_top || section.width) : section.width;
            const sectionHeight = section.height;
            const xOffset = section.x_offset || 0;
            const sectionCenterX = (xOffset + sectionWidth/2 - panelWidth/2) * scale;

            // Section divider line (except for first section)
            if (i > 0) {{
                const sx = (xOffset - panelWidth/2) * scale;
                const points = [
                    new THREE.Vector3(sx, -h/2, t/2 + 0.3),
                    new THREE.Vector3(sx, h/2, t/2 + 0.3)
                ];
                const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
                const lineMaterial = new THREE.LineDashedMaterial({{ color: 0x66bb6a, dashSize: 2, gapSize: 1, linewidth: 2 }});
                const line = new THREE.Line(lineGeometry, lineMaterial);
                line.computeLineDistances();
                sectionLines.add(line);
            }}

            // Section name label at top
            const nameLabel = createTextLabel(section.name, 18, 'rgba(40,80,120,0.95)', '#ffffff');
            nameLabel.position.set(sectionCenterX, h/2 + 4, t/2 + 0.5);
            sectionLabels.add(nameLabel);

            // Section width label at bottom
            const widthText = section.is_tapered ?
                `${{section.width_bottom || section.width}}-${{section.width_top || section.width}}mm` :
                `${{sectionWidth}}mm`;
            const sectionWidthLabel = createTextLabel(widthText, 16, 'rgba(60,60,80,0.9)', '#4fc3f7');
            sectionWidthLabel.position.set(sectionCenterX, -h/2 - 3, t/2 + 0.5);
            sectionLabels.add(sectionWidthLabel);

            // Section height labels - LEFT and RIGHT sides
            const leftEdgeX = (xOffset - panelWidth/2) * scale;
            const rightEdgeX = (xOffset + sectionWidth - panelWidth/2) * scale;

            // Get left and right heights (use section height as fallback)
            const heightLeft = section.height_left || sectionHeight;
            const heightRight = section.height_right || sectionHeight;

            // LEFT side height label - positioned inside section near left edge
            const heightLabelLeft = createTextLabel(`${{heightLeft}}mm`, 14, 'rgba(60,80,60,0.9)', '#81c784');
            heightLabelLeft.position.set(leftEdgeX + 2, h/2 - 3, t/2 + 0.5);  // Top-left inside
            sectionLabels.add(heightLabelLeft);

            // RIGHT side height label - positioned inside section near right edge
            const heightLabelRight = createTextLabel(`${{heightRight}}mm`, 14, 'rgba(60,80,60,0.9)', '#81c784');
            heightLabelRight.position.set(rightEdgeX - 2, h/2 - 3, t/2 + 0.5);  // Top-right inside
            sectionLabels.add(heightLabelRight);

            // Also show "L:" and "R:" indicators below the height values
            const leftIndicator = createTextLabel(`L`, 10, 'rgba(80,100,80,0.7)', '#c8e6c9');
            leftIndicator.position.set(leftEdgeX + 2, h/2 - 5, t/2 + 0.5);
            sectionLabels.add(leftIndicator);

            const rightIndicator = createTextLabel(`R`, 10, 'rgba(80,100,80,0.7)', '#c8e6c9');
            rightIndicator.position.set(rightEdgeX - 2, h/2 - 5, t/2 + 0.5);
            sectionLabels.add(rightIndicator);

            // Taper info for door section (84< = where taper begins, NOT a notch)
            if (section.is_tapered && section.taper_start_height) {{
                const taperStartHeight = section.taper_start_height;
                const taperY = (taperStartHeight - panelHeight/2) * scale;

                // Calculate tapered section height (top part above taper start)
                const taperedSectionHeight = (sectionHeight - taperStartHeight).toFixed(1);

                // Taper reference label (84<) on left side
                const taperRefLabel = createTextLabel(`${{taperStartHeight}}<`, 14, 'rgba(100,80,50,0.9)', '#ffcc80');
                taperRefLabel.position.set(leftEdgeX + 3, taperY, t/2 + 0.6);
                sectionLabels.add(taperRefLabel);

                // Horizontal line at taper start
                const taperLinePoints = [
                    new THREE.Vector3(leftEdgeX, taperY, t/2 + 0.3),
                    new THREE.Vector3(rightEdgeX, taperY, t/2 + 0.3)
                ];
                const taperLineMat = new THREE.LineDashedMaterial({{ color: 0xffcc80, dashSize: 1, gapSize: 0.5 }});
                const taperLine = new THREE.Line(
                    new THREE.BufferGeometry().setFromPoints(taperLinePoints),
                    taperLineMat
                );
                taperLine.computeLineDistances();
                sectionLabels.add(taperLine);

                // Tapered section height label (7.3mm) at top
                const taperedLabel = createTextLabel(`${{taperedSectionHeight}}mm`, 14, 'rgba(150,100,50,0.95)', '#ffe0b2');
                const midTaperY = (taperY + h/2) / 2;  // Middle of tapered section
                taperedLabel.position.set(sectionCenterX, midTaperY, t/2 + 0.6);
                sectionLabels.add(taperedLabel);

                // Label for tapered section
                const taperDescLabel = createTextLabel(`TAPERED`, 10, 'rgba(120,80,40,0.8)', '#ffcc80');
                taperDescLabel.position.set(sectionCenterX, midTaperY - 1.5, t/2 + 0.5);
                sectionLabels.add(taperDescLabel);

                // Straight section height label (84mm) below taper line
                const straightLabel = createTextLabel(`${{taperStartHeight}}mm`, 12, 'rgba(80,80,100,0.8)', '#b0bec5');
                const midStraightY = (-h/2 + taperY) / 2;  // Middle of straight section
                straightLabel.position.set(leftEdgeX + 3, midStraightY, t/2 + 0.5);
                sectionLabels.add(straightLabel);

                // Label for straight section
                const straightDescLabel = createTextLabel(`STRAIGHT`, 10, 'rgba(80,80,100,0.7)', '#90a4ae');
                straightDescLabel.position.set(leftEdgeX + 3, midStraightY - 1.5, t/2 + 0.4);
                sectionLabels.add(straightDescLabel);
            }}

            // Type label (door/panel)
            const typeLabel = createTextLabel(section.type.toUpperCase(), 10, 'rgba(80,80,100,0.8)', '#b0bec5');
            typeLabel.position.set(sectionCenterX, h/2 + 2, t/2 + 0.5);
            sectionLabels.add(typeLabel);

            // Hole count label for panels
            if (section.hole_count > 0) {{
                const holeLabel = createTextLabel(`${{section.hole_count}} holes`, 10, 'rgba(100,60,60,0.8)', '#ff8a80');
                holeLabel.position.set(sectionCenterX, -h/2 + 2, t/2 + 0.5);
                sectionLabels.add(holeLabel);
            }}
        }});

        panelGroup.add(sectionLines);
        panelGroup.add(sectionLabels);

        // Comprehensive Dimension labels
        const dimensionGroup = new THREE.Group();
        const dimLineMat = new THREE.LineBasicMaterial({{ color: 0xff9800, linewidth: 2 }});

        // ===== BOTTOM: Total Width =====
        const widthDimY = -h/2 - 6;
        const widthPoints = [
            new THREE.Vector3(-w/2, widthDimY, 0),
            new THREE.Vector3(w/2, widthDimY, 0)
        ];
        const widthLine = new THREE.Line(
            new THREE.BufferGeometry().setFromPoints(widthPoints), dimLineMat
        );
        dimensionGroup.add(widthLine);

        // Width end ticks
        const tickSize = 1;
        [[-w/2, widthDimY], [w/2, widthDimY]].forEach(([x, y]) => {{
            const tickPoints = [
                new THREE.Vector3(x, y - tickSize, 0),
                new THREE.Vector3(x, y + tickSize, 0)
            ];
            dimensionGroup.add(new THREE.Line(
                new THREE.BufferGeometry().setFromPoints(tickPoints), dimLineMat
            ));
        }});

        // Total width label
        const totalWidthLabel = createTextLabel(`${{panelWidth}}mm (Total Width)`, 16, 'rgba(255,152,0,0.95)', '#ffffff');
        totalWidthLabel.position.set(0, widthDimY - 2.5, 0);
        dimensionGroup.add(totalWidthLabel);

        // ===== LEFT SIDE: Main Height =====
        const heightDimX = -w/2 - 6;
        const heightPoints = [
            new THREE.Vector3(heightDimX, -h/2, 0),
            new THREE.Vector3(heightDimX, h/2, 0)
        ];
        const heightLine = new THREE.Line(
            new THREE.BufferGeometry().setFromPoints(heightPoints), dimLineMat
        );
        dimensionGroup.add(heightLine);

        // Height end ticks
        [[heightDimX, -h/2], [heightDimX, h/2]].forEach(([x, y]) => {{
            const tickPoints = [
                new THREE.Vector3(x - tickSize, y, 0),
                new THREE.Vector3(x + tickSize, y, 0)
            ];
            dimensionGroup.add(new THREE.Line(
                new THREE.BufferGeometry().setFromPoints(tickPoints), dimLineMat
            ));
        }});

        // Main height label
        const heightLabel = createTextLabel(`${{panelHeight}}mm`, 16, 'rgba(255,152,0,0.95)', '#ffffff');
        heightLabel.position.set(heightDimX - 3, 0, 0);
        dimensionGroup.add(heightLabel);

        // ===== LEFT EDGE: Thickness =====
        const thicknessLabel = createTextLabel(`T: ${{panelThickness}}mm`, 14, 'rgba(100,100,150,0.9)', '#ce93d8');
        thicknessLabel.position.set(-w/2 - 4, h/2 - 3, t);
        dimensionGroup.add(thicknessLabel);

        // ===== EDGE TYPE label =====
        const edgeTypeLabel = createTextLabel(`{edge_type.replace('_', ' ').title()}`, 12, 'rgba(80,80,120,0.9)', '#90caf9');
        edgeTypeLabel.position.set(-w/2 - 3, -h/2 + 3, t/2 + 0.5);
        dimensionGroup.add(edgeTypeLabel);

        panelGroup.add(dimensionGroup);

        scene.add(panelGroup);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(ambientLight);

        const mainLight = new THREE.DirectionalLight(0xffffff, 0.8);
        mainLight.position.set(100, 100, 100);
        mainLight.castShadow = true;
        scene.add(mainLight);

        const fillLight = new THREE.DirectionalLight(0x4fc3f7, 0.3);
        fillLight.position.set(-100, -50, -100);
        scene.add(fillLight);

        const backLight = new THREE.DirectionalLight(0xffffff, 0.2);
        backLight.position.set(0, 0, -100);
        scene.add(backLight);

        // Ground plane (reflection surface)
        const groundGeometry = new THREE.PlaneGeometry(1000, 1000);
        const groundMaterial = new THREE.MeshStandardMaterial({{
            color: 0x1a1a2e,
            roughness: 0.8,
            metalness: 0.2
        }});
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -h/2 - 30;
        ground.receiveShadow = true;
        scene.add(ground);

        // Grid helper
        const gridHelper = new THREE.GridHelper(500, 50, 0x404040, 0x303030);
        gridHelper.position.y = -h/2 - 29;
        scene.add(gridHelper);

        // Initial camera position
        const maxDim = Math.max(w, h);
        camera.position.set(maxDim * 1.5, maxDim * 0.8, maxDim * 1.5);
        controls.target.set(0, 0, 0);

        // View functions
        function setView(view) {{
            const dist = maxDim * 2;
            switch(view) {{
                case 'front': camera.position.set(0, 0, dist); break;
                case 'back': camera.position.set(0, 0, -dist); break;
                case 'top': camera.position.set(0, dist, 0.1); break;
                case 'side': camera.position.set(dist, 0, 0); break;
                case 'iso': camera.position.set(dist*0.7, dist*0.5, dist*0.7); break;
            }}
            controls.target.set(0, 0, 0);
            controls.update();
        }}

        let autoRotate = false;
        function toggleAutoRotate() {{
            autoRotate = !autoRotate;
            controls.autoRotate = autoRotate;
            document.getElementById('status').textContent = autoRotate ? 'Auto-rotating...' : 'Drag to rotate • Scroll to zoom';
        }}

        // Control event handlers
        document.getElementById('showDimensions').addEventListener('change', (e) => {{
            dimensionGroup.visible = e.target.checked;
        }});

        document.getElementById('showHoles').addEventListener('change', (e) => {{
            holeMarkers.visible = e.target.checked;
        }});

        document.getElementById('showSections').addEventListener('change', (e) => {{
            sectionLines.visible = e.target.checked;
            sectionLabels.visible = e.target.checked;
        }});

        document.getElementById('wireframe').addEventListener('change', (e) => {{
            glassMaterial.wireframe = e.target.checked;
        }});

        document.getElementById('opacity').addEventListener('input', (e) => {{
            glassMaterial.opacity = parseFloat(e.target.value);
        }});

        document.getElementById('tint').addEventListener('input', (e) => {{
            const tint = parseInt(e.target.value);
            const r = 0.53 + (tint/100) * 0.2;
            const g = 0.8 - (tint/100) * 0.3;
            const b = 1.0 - (tint/100) * 0.5;
            glassMaterial.color.setRGB(r, g, b);
        }});

        // Double-click to reset
        renderer.domElement.addEventListener('dblclick', () => setView('iso'));

        // Resize handler
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        // Animation loop
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();
    </script>
</body>
</html>'''

        (self.output_dir / "glass_3d_model.html").write_text(html, encoding='utf-8')
        self.generated_files.append("glass_3d_model.html")
    
    def _generate_instructions(self, extraction: Dict[str, Any]) -> None:
        """Generate comprehensive manufacturing instructions."""
        dims = extraction.get("dimensions", {})
        holes = extraction.get("holes", [])
        sections = extraction.get("sections", [])
        glass_type = extraction.get("glass_type", "clear_tempered")
        edge_type = extraction.get("edge_type", "flat_polished")
        notes = extraction.get("notes", [])

        width = dims.get("width", 0)
        height = dims.get("height", 0)
        thickness = dims.get("thickness", 0)

        # Calculate weight
        weight = (width/1000) * (height/1000) * (thickness/1000) * 2500
        for hole in holes:
            d = hole.get("diameter", 0) / 1000
            hole_vol = math.pi * (d/2)**2 * (thickness/1000)
            weight -= hole_vol * 2500

        # Calculate area
        area_m2 = (width/1000) * (height/1000)

        # Determine tolerances based on thickness
        if thickness <= 6:
            dim_tolerance = "±1.5"
        elif thickness <= 10:
            dim_tolerance = "±2.0"
        else:
            dim_tolerance = "±3.0"

        content = f"""# Glass Panel Manufacturing Instructions

## Document Information
| Field | Value |
|-------|-------|
| Generated | {self._timestamp.strftime('%Y-%m-%d %H:%M:%S')} |
| Document Version | 1.0 |
| Standard | EN 12150 / ASTM C1048 |

---

## 1. Panel Specifications

### 1.1 Dimensions
| Parameter | Value | Tolerance |
|-----------|-------|-----------|
| Width (W) | {width} mm | {dim_tolerance} mm |
| Height (H) | {height} mm | {dim_tolerance} mm |
| Thickness (T) | {thickness} mm | ±0.5 mm |
| Diagonal | {math.sqrt(width**2 + height**2):.1f} mm | ±3.0 mm |

### 1.2 Physical Properties
| Property | Value |
|----------|-------|
| Surface Area | {area_m2:.3f} m² |
| Calculated Weight | {weight:.2f} kg |
| Glass Density | 2,500 kg/m³ |

### 1.3 Material Specification
| Property | Specification |
|----------|---------------|
| Glass Type | {glass_type.replace('_', ' ').title()} |
| Edge Treatment | {edge_type.replace('_', ' ').title()} |
| Color/Tint | Clear |
| Heat Treatment | {"Heat Strengthened / Tempered" if "tempered" in glass_type.lower() else "Annealed"} |

---

## 2. Cutting Instructions

### 2.1 Initial Cut
1. **Stock Selection**: Select glass sheet minimum {width + 50}mm x {height + 50}mm
2. **Scoring**: Score glass using carbide wheel at 2-3 bar pressure
3. **Breaking**: Apply controlled pressure along score line
4. **Rough Cut Tolerance**: ±2.0 mm (to be refined in edging)

### 2.2 Edge Processing
| Edge | Treatment | Specification |
|------|-----------|---------------|
| All edges | {edge_type.replace('_', ' ').title()} | Minimum {thickness}mm seam |
| Corners | Arrised | 2mm x 45° chamfer |

---

## 3. Hole Drilling Sequence

### 3.1 Pre-Drilling Checks
- [ ] Verify glass is at room temperature (18-25°C)
- [ ] Check drill bit condition (diamond core)
- [ ] Ensure coolant system is operational
- [ ] Confirm hole positions from datum edge

### 3.2 Drilling Parameters
| Parameter | Value |
|-----------|-------|
| Tool Type | Diamond Core Drill |
| Spindle Speed | 2,500-3,500 RPM |
| Feed Rate | 10-15 mm/min |
| Coolant | Water (continuous flow) |
| Back Support | Required |

### 3.3 Hole Schedule
"""
        if holes:
            content += "| Hole # | X Position | Y Position | Diameter | Edge Distance | Notes |\n"
            content += "|--------|------------|------------|----------|---------------|-------|\n"
            for i, h in enumerate(holes, 1):
                x = h.get('x', 0)
                y = h.get('y', 0)
                d = h.get('diameter', 0)
                # Calculate minimum edge distance
                edge_dist_left = x - d/2
                edge_dist_right = width - x - d/2
                edge_dist_bottom = y - d/2
                edge_dist_top = height - y - d/2
                min_edge = min(edge_dist_left, edge_dist_right, edge_dist_bottom, edge_dist_top)
                content += f"| {i} | {x:.1f} mm | {y:.1f} mm | Ø{d:.1f} mm | {min_edge:.1f} mm | Through hole |\n"

            content += f"""
### 3.4 Drilling Procedure (Per Hole)
1. Position workpiece on drilling table with back support
2. Align drill bit to marked position (±1mm tolerance)
3. Start spindle and coolant flow
4. Begin drilling at slow feed until pilot hole established
5. Continue at standard feed rate until breakthrough
6. Retract slowly to prevent chipping
7. Inspect hole for chips or cracks
8. Deburr edges if necessary

"""
        else:
            content += "*No holes required for this panel*\n\n"

        if sections:
            content += """---

## 4. Section Details

### 4.1 Section Schedule
"""
            content += "| Section | Type | Width | H-Left | H-Right | X Offset | Holes |\n"
            content += "|---------|------|-------|--------|---------|----------|-------|\n"
            for s in sections:
                # Handle tapered sections
                if s.get('is_tapered') and 'width_bottom' in s and 'width_top' in s:
                    width_str = f"{s.get('width_bottom', 0):.1f}-{s.get('width_top', 0):.1f} mm"
                else:
                    width_str = f"{s.get('width', 0):.1f} mm"
                height_left = s.get('height_left', s.get('height', 0))
                height_right = s.get('height_right', s.get('height', 0))
                hole_count = s.get('hole_count', 0)
                content += f"| {s.get('name', 'N/A')} | {s.get('type', 'panel')} | {width_str} | {height_left:.1f} mm | {height_right:.1f} mm | {s.get('x_offset', 0):.1f} mm | {hole_count} |\n"

            # Add detailed section information
            content += """
### 4.2 Detailed Section Specifications
"""
            for s in sections:
                content += f"""
#### {s.get('name', 'Section')} ({s.get('type', 'panel').upper()})
"""
                if s.get('is_tapered'):
                    content += f"""- **Width (Bottom)**: {s.get('width_bottom', 0)} mm
- **Width (Top)**: {s.get('width_top', 0)} mm
- **Taper Start Height**: {s.get('taper_start_height', 0)} mm
- **Straight Section**: {s.get('straight_section_height', s.get('taper_start_height', 0))} mm
- **Tapered Section**: {s.get('tapered_section_height', 0)} mm
"""
                else:
                    content += f"""- **Width**: {s.get('width', 0)} mm
"""
                content += f"""- **Height (Left Edge)**: {s.get('height_left', s.get('height', 0))} mm
- **Height (Right Edge)**: {s.get('height_right', s.get('height', 0))} mm
- **X Offset**: {s.get('x_offset', 0)} mm
- **Holes**: {s.get('hole_count', 0)}
"""
                if s.get('notes'):
                    content += f"- **Notes**: {s.get('notes')}\n"

        content += f"""
---

## 5. Quality Control

### 5.1 Dimensional Inspection
- [ ] Width: {width} mm {dim_tolerance} mm
- [ ] Height: {height} mm {dim_tolerance} mm
- [ ] Thickness: {thickness} mm ±0.5 mm
- [ ] Diagonal difference: ≤3.0 mm
- [ ] All hole positions: ±1.0 mm

### 5.2 Visual Inspection
- [ ] No chips or cracks at edges
- [ ] No scratches visible at 1m distance under 500 lux
- [ ] Edge finish consistent and smooth
- [ ] Holes free of chips and burrs
- [ ] No inclusions or bubbles in viewing area

### 5.3 Heat Treatment Verification (if applicable)
- [ ] Fragmentation test sample available
- [ ] Surface compression ≥69 MPa (10,000 psi)
- [ ] Edge compression ≥69 MPa (10,000 psi)

---

## 6. Packaging & Handling

### 6.1 Handling Precautions
- Always handle with clean gloves
- Lift from edges, never from flat surface
- Store vertically at 3-6° angle
- Use edge protectors during transport

### 6.2 Packaging Requirements
- Interleaving paper between panels
- Edge protection on all sides
- Crate rating minimum {weight * 3:.0f} kg capacity
- "FRAGILE - GLASS" labels required

---

## 7. Notes & Special Instructions

"""
        for note in notes:
            content += f"- {note}\n"

        content += f"""
---

## 8. Approval Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Prepared By | | | |
| Reviewed By | | | |
| Approved By | | | |

---

*This document was auto-generated by the Glass Manufacturing Skill v1.0*
*Reference standards: EN 12150-1, ASTM C1048, ISO 12543*
"""
        (self.output_dir / "manufacturing_instructions.md").write_text(content, encoding='utf-8')
        self.generated_files.append("manufacturing_instructions.md")
    
    def _generate_gcode(self, extraction: Dict[str, Any]) -> None:
        """Generate professional CNC G-code for glass drilling."""
        dims = extraction.get("dimensions", {})
        holes = extraction.get("holes", [])
        width = dims.get("width", 0)
        height = dims.get("height", 0)
        thickness = dims.get("thickness", 10)

        # CNC parameters for glass drilling
        safe_z = 10.0           # Safe Z height
        rapid_z = 3.0           # Rapid approach Z
        peck_depth = 1.5        # Peck drilling depth
        plunge_feed = 10        # Feed rate for plunging (mm/min)
        rapid_feed = 1000       # Rapid feed rate
        spindle_speed = 3000    # RPM for diamond drill
        coolant_on = "M8"       # Coolant on
        coolant_off = "M9"      # Coolant off

        timestamp = self._timestamp.strftime('%Y-%m-%d %H:%M:%S')

        gcode = f"""; ================================================================
; GLASS PANEL CNC DRILLING PROGRAM
; ================================================================
; Generated: {timestamp}
; Generator: Glass Manufacturing Skill v1.0
; ================================================================
;
; PANEL SPECIFICATIONS:
; Width:     {width} mm
; Height:    {height} mm
; Thickness: {thickness} mm
; Holes:     {len(holes)}
;
; MACHINE REQUIREMENTS:
; - Diamond core drill bits
; - Continuous water coolant system
; - Back support plate installed
; - Vacuum or clamp fixturing
;
; SAFETY NOTES:
; - Verify workpiece is securely fixtured
; - Check coolant flow before starting
; - Wear appropriate PPE
; - Do not leave machine unattended
;
; ================================================================

; --- PROGRAM START ---
%
O0001 (GLASS PANEL DRILLING)

; --- SAFETY BLOCK ---
G90 G94 G17 G40 G49 G80  ; Absolute, feed/min, XY plane, cancel comp/cycles
G21                       ; Metric units (mm)
G28 G91 Z0               ; Home Z axis first
G90                       ; Return to absolute

; --- SET WORK COORDINATES ---
G54                       ; Use work coordinate system 1
; Assumes origin at bottom-left corner of glass panel

; --- SPINDLE AND COOLANT ---
S{spindle_speed} M3       ; Start spindle CW at {spindle_speed} RPM
G4 P2000                  ; Dwell 2 seconds for spindle to reach speed
{coolant_on}              ; Coolant ON (water for glass drilling)

; --- RAPID TO SAFE HEIGHT ---
G0 Z{safe_z}              ; Move to safe Z height

"""
        if holes:
            for i, h in enumerate(holes, 1):
                x = h.get('x', 0)
                y = h.get('y', 0)
                d = h.get('diameter', 0)
                total_depth = thickness + 2  # Drill through with 2mm clearance

                gcode += f"""
; ================================================================
; HOLE {i} of {len(holes)}
; Position: X={x}, Y={y}
; Diameter: {d} mm
; ================================================================

; Rapid to position above hole
G0 X{x:.3f} Y{y:.3f}      ; Move to hole center
G0 Z{rapid_z}             ; Rapid to approach height

; --- PECK DRILLING CYCLE ---
; Using G83 peck drilling for clean hole quality
G83 X{x:.3f} Y{y:.3f} Z-{total_depth:.3f} R{rapid_z} Q{peck_depth} F{plunge_feed}
; G83: Peck drilling cycle
;   X,Y: Hole position
;   Z: Final depth ({total_depth}mm through {thickness}mm glass)
;   R: Retract plane ({rapid_z}mm)
;   Q: Peck increment ({peck_depth}mm)
;   F: Feed rate ({plunge_feed} mm/min)

G80                       ; Cancel canned cycle
G0 Z{safe_z}              ; Retract to safe height

; Inspection pause (optional - remove for production)
; M0                      ; Optional stop for hole inspection
"""

        gcode += f"""
; ================================================================
; PROGRAM END
; ================================================================

; --- RETURN TO HOME ---
{coolant_off}             ; Coolant OFF
G0 Z{safe_z}              ; Ensure safe Z height
M5                        ; Spindle STOP
G28 G91 Z0               ; Home Z axis
G28 X0 Y0                ; Home X and Y axes
G90                       ; Absolute mode

; --- PROGRAM COMPLETE ---
M30                       ; End program and rewind

%

; ================================================================
; POST-PROCESSING NOTES:
; ================================================================
; 1. Inspect all holes for chips or cracks
; 2. Deburr hole edges if necessary
; 3. Clean glass surface of coolant residue
; 4. Verify hole positions with gauge
; 5. Document any deviations
; ================================================================
"""
        (self.output_dir / "cnc_program.gcode").write_text(gcode, encoding='utf-8')
        self.generated_files.append("cnc_program.gcode")
    
    def _generate_technical_drawing(self, extraction: Dict[str, Any]) -> None:
        """Generate professional SVG technical drawing with multiple views."""
        dims = extraction.get("dimensions", {})
        holes = extraction.get("holes", [])
        sections = extraction.get("sections", [])
        glass_type = extraction.get("glass_type", "clear_tempered")
        edge_type = extraction.get("edge_type", "flat_polished")

        width = dims.get("width", 100)
        height = dims.get("height", 100)
        thickness = dims.get("thickness", 10)

        # SVG canvas dimensions - INCREASED for larger text
        svg_width = 1800
        svg_height = 1400

        # Drawing area margins
        margin = 100
        title_block_height = 180

        # Calculate scale to fit panel in drawing area
        draw_width = svg_width - 2 * margin - 300  # Leave space for side view
        draw_height = svg_height - 2 * margin - title_block_height - 100

        scale_x = draw_width / width
        scale_y = draw_height / height
        scale = min(scale_x, scale_y) * 0.7  # 70% of available space

        # Panel drawing position (front view)
        panel_x = margin + 50
        panel_y = margin + 50
        panel_w = width * scale
        panel_h = height * scale

        # Side view position
        side_x = panel_x + panel_w + 80
        side_y = panel_y
        side_w = thickness * scale * 5  # Exaggerate thickness for visibility
        side_h = panel_h

        # Calculate weight
        weight = (width/1000) * (height/1000) * (thickness/1000) * 2500

        # Calculate tolerances based on thickness (matching validation_report logic)
        tolerance_linear = 1.5 if thickness <= 6 else (2.0 if thickness <= 10 else 3.0)
        tolerance_diagonal = 3.0
        tolerance_hole = 1.0
        tolerance_thickness = 0.5

        timestamp = self._timestamp.strftime('%Y-%m-%d')

        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">
    <defs>
        <!-- Arrow marker for dimension lines -->
        <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
        </marker>
        <marker id="arrow-start" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto" markerUnits="strokeWidth">
            <path d="M9,0 L9,6 L0,3 z" fill="#333"/>
        </marker>
        <!-- Grid pattern -->
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#e0e0e0" stroke-width="0.5"/>
        </pattern>
        <!-- Hatch pattern for section -->
        <pattern id="hatch" patternUnits="userSpaceOnUse" width="4" height="4">
            <path d="M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2" stroke="#666" stroke-width="0.5"/>
        </pattern>
    </defs>

    <!-- Background -->
    <rect width="{svg_width}" height="{svg_height}" fill="#fafafa"/>

    <!-- Drawing border -->
    <rect x="10" y="10" width="{svg_width-20}" height="{svg_height-20}" fill="none" stroke="#333" stroke-width="2"/>

    <!-- Grid (optional background) -->
    <rect x="10" y="10" width="{svg_width-20}" height="{svg_height - title_block_height - 20}" fill="url(#grid)" opacity="0.5"/>

    <!-- ============================================== -->
    <!-- FRONT VIEW -->
    <!-- ============================================== -->
    <g id="front-view">
        <text x="{panel_x + panel_w/2}" y="{panel_y - 25}" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="#333">FRONT VIEW</text>

        <!-- Panel outline -->
        <rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}"
              fill="none" stroke="#000" stroke-width="3"/>

        <!-- Panel fill (glass appearance) -->
        <rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}"
              fill="#e3f2fd" fill-opacity="0.3"/>
'''

        # Draw section dividers and section labels with measurements
        for i, section in enumerate(sections):
            sec_x_offset = section.get('x_offset', 0)
            sec_width = section.get('width_top', section.get('width', 0)) if section.get('is_tapered') else section.get('width', 0)
            sec_height = section.get('height', height)
            sec_height_left = section.get('height_left', sec_height)
            sec_height_right = section.get('height_right', sec_height)
            sec_center_x = panel_x + (sec_x_offset + sec_width / 2) * scale

            # Section divider line (except for first section)
            if i > 0:
                sx = panel_x + sec_x_offset * scale
                svg += f'''
        <!-- Section divider {i} -->
        <line x1="{sx}" y1="{panel_y}" x2="{sx}" y2="{panel_y + panel_h}"
              stroke="#666" stroke-width="1" stroke-dasharray="5,3"/>
'''

            # Section name label at top
            svg += f'''
        <!-- Section {i+1} labels -->
        <text x="{sec_center_x}" y="{panel_y - 55}" text-anchor="middle"
              font-family="Arial" font-size="20" font-weight="bold" fill="#1565c0">{section.get('name', f'Section {i+1}')}</text>
        <text x="{sec_center_x}" y="{panel_y - 35}" text-anchor="middle"
              font-family="Arial" font-size="16" fill="#666">({section.get('type', 'panel').upper()})</text>
'''

            # Section width label at bottom
            if section.get('is_tapered'):
                width_text = f"{section.get('width_bottom', sec_width)}-{section.get('width_top', sec_width)}mm"
            else:
                width_text = f"{sec_width}mm"
            svg += f'''
        <text x="{sec_center_x}" y="{panel_y + panel_h + 75}" text-anchor="middle"
              font-family="Arial" font-size="18" font-weight="bold" fill="#1976d2">{width_text}</text>
'''

            # Height labels on left and right of section
            left_x = panel_x + sec_x_offset * scale + 10
            right_x = panel_x + (sec_x_offset + sec_width) * scale - 10
            svg += f'''
        <text x="{left_x}" y="{panel_y + 25}" font-family="Arial" font-size="16" font-weight="bold" fill="#2e7d32">{sec_height_left}mm</text>
        <text x="{right_x}" y="{panel_y + 25}" text-anchor="end" font-family="Arial" font-size="16" font-weight="bold" fill="#2e7d32">{sec_height_right}mm</text>
'''

            # Taper info for door section
            if section.get('is_tapered') and section.get('taper_start_height'):
                taper_start = section.get('taper_start_height', 0)
                tapered_height = section.get('tapered_section_height', sec_height - taper_start)
                taper_y = panel_y + panel_h - (taper_start * scale)

                # Horizontal line at taper start
                svg += f'''
        <!-- Taper line for {section.get('name')} -->
        <line x1="{panel_x + sec_x_offset * scale}" y1="{taper_y}"
              x2="{panel_x + (sec_x_offset + sec_width) * scale}" y2="{taper_y}"
              stroke="#ff9800" stroke-width="2" stroke-dasharray="5,3"/>
        <text x="{sec_center_x - 30}" y="{taper_y + 6}" font-family="Arial" font-size="16" font-weight="bold" fill="#e65100">{taper_start}<</text>
        <text x="{sec_center_x}" y="{taper_y - 15}" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="#ff9800">TAPERED: {tapered_height}mm</text>
        <text x="{sec_center_x}" y="{taper_y + 30}" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">STRAIGHT: {taper_start}mm</text>
'''

        # Draw holes
        for i, hole in enumerate(holes):
            hx = panel_x + hole.get('x', 0) * scale
            hy = panel_y + panel_h - hole.get('y', 0) * scale  # Flip Y axis
            hr = (hole.get('diameter', 0) / 2) * scale

            svg += f'''
        <!-- Hole {i+1} -->
        <circle cx="{hx}" cy="{hy}" r="{hr}" fill="none" stroke="#d32f2f" stroke-width="1.5"/>
        <line x1="{hx - hr}" y1="{hy}" x2="{hx + hr}" y2="{hy}" stroke="#d32f2f" stroke-width="0.5"/>
        <line x1="{hx}" y1="{hy - hr}" x2="{hx}" y2="{hy + hr}" stroke="#d32f2f" stroke-width="0.5"/>
'''

        # Dimension lines
        dim_offset = 40
        svg += f'''
        <!-- Width dimension -->
        <line x1="{panel_x}" y1="{panel_y + panel_h + dim_offset}" x2="{panel_x + panel_w}" y2="{panel_y + panel_h + dim_offset}"
              stroke="#333" stroke-width="2" marker-start="url(#arrow-start)" marker-end="url(#arrow)"/>
        <line x1="{panel_x}" y1="{panel_y + panel_h + 10}" x2="{panel_x}" y2="{panel_y + panel_h + dim_offset + 15}"
              stroke="#333" stroke-width="1"/>
        <line x1="{panel_x + panel_w}" y1="{panel_y + panel_h + 10}" x2="{panel_x + panel_w}" y2="{panel_y + panel_h + dim_offset + 15}"
              stroke="#333" stroke-width="1"/>
        <text x="{panel_x + panel_w/2}" y="{panel_y + panel_h + dim_offset + 30}" text-anchor="middle"
              font-family="Arial" font-size="22" font-weight="bold" fill="#333">{width} mm (TOTAL WIDTH)</text>

        <!-- Height dimension -->
        <line x1="{panel_x - dim_offset}" y1="{panel_y}" x2="{panel_x - dim_offset}" y2="{panel_y + panel_h}"
              stroke="#333" stroke-width="2" marker-start="url(#arrow-start)" marker-end="url(#arrow)"/>
        <line x1="{panel_x - dim_offset - 15}" y1="{panel_y}" x2="{panel_x - 10}" y2="{panel_y}"
              stroke="#333" stroke-width="1"/>
        <line x1="{panel_x - dim_offset - 15}" y1="{panel_y + panel_h}" x2="{panel_x - 10}" y2="{panel_y + panel_h}"
              stroke="#333" stroke-width="1"/>
        <text x="{panel_x - dim_offset - 10}" y="{panel_y + panel_h/2}" text-anchor="middle"
              font-family="Arial" font-size="22" font-weight="bold" fill="#333" transform="rotate(-90 {panel_x - dim_offset - 10} {panel_y + panel_h/2})">{height} mm</text>
    </g>

    <!-- ============================================== -->
    <!-- SIDE VIEW (SECTION) -->
    <!-- ============================================== -->
    <g id="side-view">
        <text x="{side_x + side_w/2}" y="{side_y - 25}" text-anchor="middle" font-family="Arial" font-size="24" font-weight="bold" fill="#333">SIDE VIEW</text>

        <!-- Panel cross-section -->
        <rect x="{side_x}" y="{side_y}" width="{side_w}" height="{side_h}"
              fill="url(#hatch)" stroke="#000" stroke-width="3"/>

        <!-- Thickness dimension -->
        <line x1="{side_x}" y1="{side_y + side_h + dim_offset}" x2="{side_x + side_w}" y2="{side_y + side_h + dim_offset}"
              stroke="#333" stroke-width="2" marker-start="url(#arrow-start)" marker-end="url(#arrow)"/>
        <text x="{side_x + side_w/2}" y="{side_y + side_h + dim_offset + 30}" text-anchor="middle"
              font-family="Arial" font-size="20" font-weight="bold" fill="#333">{thickness} mm (THICKNESS)</text>
    </g>

    <!-- ============================================== -->
    <!-- HOLE DETAIL TABLE -->
    <!-- ============================================== -->
    <g id="hole-table" transform="translate({side_x + side_w + 60}, {panel_y})">
        <text x="0" y="0" font-family="Arial" font-size="20" font-weight="bold" fill="#333">HOLE SCHEDULE</text>
        <line x1="0" y1="8" x2="280" y2="8" stroke="#333" stroke-width="2"/>

        <!-- Table header -->
        <text x="10" y="40" font-family="Arial" font-size="16" font-weight="bold" fill="#333">#</text>
        <text x="40" y="40" font-family="Arial" font-size="16" font-weight="bold" fill="#333">X (mm)</text>
        <text x="120" y="40" font-family="Arial" font-size="16" font-weight="bold" fill="#333">Y (mm)</text>
        <text x="200" y="40" font-family="Arial" font-size="16" font-weight="bold" fill="#333">Ø (mm)</text>
        <line x1="0" y1="50" x2="280" y2="50" stroke="#333" stroke-width="1"/>
'''

        # Add hole entries to table
        for i, hole in enumerate(holes):
            y_pos = 75 + i * 28
            svg += f'''
        <text x="10" y="{y_pos}" font-family="Arial" font-size="16" fill="#333">{i+1}</text>
        <text x="40" y="{y_pos}" font-family="Arial" font-size="16" fill="#333">{hole.get('x', 0):.1f}</text>
        <text x="120" y="{y_pos}" font-family="Arial" font-size="16" fill="#333">{hole.get('y', 0):.1f}</text>
        <text x="200" y="{y_pos}" font-family="Arial" font-size="16" font-weight="bold" fill="#d32f2f">{hole.get('diameter', 0):.1f}</text>
'''

        svg += '''
    </g>
'''

        # Add SECTION TABLE
        section_table_y = panel_y + 200 + len(holes) * 28
        svg += f'''
    <!-- ============================================== -->
    <!-- SECTION SCHEDULE TABLE -->
    <!-- ============================================== -->
    <g id="section-table" transform="translate({side_x + side_w + 60}, {section_table_y})">
        <text x="0" y="0" font-family="Arial" font-size="20" font-weight="bold" fill="#1565c0">SECTION SCHEDULE</text>
        <line x1="0" y1="8" x2="420" y2="8" stroke="#1565c0" stroke-width="2"/>

        <!-- Table header -->
        <text x="10" y="40" font-family="Arial" font-size="14" font-weight="bold" fill="#333">Name</text>
        <text x="80" y="40" font-family="Arial" font-size="14" font-weight="bold" fill="#333">Type</text>
        <text x="140" y="40" font-family="Arial" font-size="14" font-weight="bold" fill="#333">Width</text>
        <text x="220" y="40" font-family="Arial" font-size="14" font-weight="bold" fill="#333">H-Left</text>
        <text x="290" y="40" font-family="Arial" font-size="14" font-weight="bold" fill="#333">H-Right</text>
        <text x="360" y="40" font-family="Arial" font-size="14" font-weight="bold" fill="#333">Taper</text>
        <line x1="0" y1="50" x2="420" y2="50" stroke="#333" stroke-width="1"/>
'''

        # Add section entries to table
        for i, section in enumerate(sections):
            y_pos = 75 + i * 28
            sec_width = section.get('width_top', section.get('width', 0)) if section.get('is_tapered') else section.get('width', 0)
            taper_info = f"{section.get('tapered_section_height', '-')}mm" if section.get('is_tapered') else "-"
            svg += f'''
        <text x="10" y="{y_pos}" font-family="Arial" font-size="14" fill="#333">{section.get('name', f'P{i+1}')}</text>
        <text x="80" y="{y_pos}" font-family="Arial" font-size="14" fill="#666">{section.get('type', 'panel')}</text>
        <text x="140" y="{y_pos}" font-family="Arial" font-size="14" font-weight="bold" fill="#1976d2">{sec_width}</text>
        <text x="220" y="{y_pos}" font-family="Arial" font-size="14" font-weight="bold" fill="#2e7d32">{section.get('height_left', section.get('height', 0))}</text>
        <text x="290" y="{y_pos}" font-family="Arial" font-size="14" font-weight="bold" fill="#2e7d32">{section.get('height_right', section.get('height', 0))}</text>
        <text x="360" y="{y_pos}" font-family="Arial" font-size="14" fill="#ff9800">{taper_info}</text>
'''

        svg += '''
    </g>

    <!-- ============================================== -->
    <!-- TITLE BLOCK -->
    <!-- ============================================== -->
'''
        title_y = svg_height - title_block_height - 10
        svg += f'''
    <g id="title-block">
        <rect x="10" y="{title_y}" width="{svg_width - 20}" height="{title_block_height}" fill="#fff" stroke="#333" stroke-width="3"/>

        <!-- Dividers -->
        <line x1="450" y1="{title_y}" x2="450" y2="{svg_height - 10}" stroke="#333" stroke-width="1"/>
        <line x1="900" y1="{title_y}" x2="900" y2="{svg_height - 10}" stroke="#333" stroke-width="1"/>
        <line x1="1350" y1="{title_y}" x2="1350" y2="{svg_height - 10}" stroke="#333" stroke-width="1"/>
        <line x1="10" y1="{title_y + 80}" x2="450" y2="{title_y + 80}" stroke="#333" stroke-width="0.5"/>

        <!-- Title -->
        <text x="230" y="{title_y + 45}" text-anchor="middle" font-family="Arial" font-size="32" font-weight="bold" fill="#333">GLASS PANEL</text>
        <text x="230" y="{title_y + 72}" text-anchor="middle" font-family="Arial" font-size="18" fill="#666">Technical Drawing</text>

        <!-- Project info -->
        <text x="30" y="{title_y + 110}" font-family="Arial" font-size="16" fill="#666">Drawing No:</text>
        <text x="150" y="{title_y + 110}" font-family="Arial" font-size="16" font-weight="bold" fill="#333">GP-001</text>
        <text x="30" y="{title_y + 140}" font-family="Arial" font-size="16" fill="#666">Date:</text>
        <text x="150" y="{title_y + 140}" font-family="Arial" font-size="16" fill="#333">{timestamp}</text>

        <!-- Specifications -->
        <text x="470" y="{title_y + 35}" font-family="Arial" font-size="18" font-weight="bold" fill="#333">SPECIFICATIONS</text>
        <text x="470" y="{title_y + 65}" font-family="Arial" font-size="16" fill="#666">Dimensions:</text>
        <text x="600" y="{title_y + 65}" font-family="Arial" font-size="16" font-weight="bold" fill="#333">{width} x {height} x {thickness} mm</text>
        <text x="470" y="{title_y + 90}" font-family="Arial" font-size="16" fill="#666">Glass Type:</text>
        <text x="600" y="{title_y + 90}" font-family="Arial" font-size="16" fill="#333">{glass_type.replace('_', ' ').title()}</text>
        <text x="470" y="{title_y + 115}" font-family="Arial" font-size="16" fill="#666">Edge:</text>
        <text x="600" y="{title_y + 115}" font-family="Arial" font-size="16" fill="#333">{edge_type.replace('_', ' ').title()}</text>
        <text x="470" y="{title_y + 140}" font-family="Arial" font-size="16" fill="#666">Weight:</text>
        <text x="600" y="{title_y + 140}" font-family="Arial" font-size="16" font-weight="bold" fill="#333">{weight:.2f} kg</text>

        <!-- Tolerances (calculated based on glass thickness) -->
        <text x="920" y="{title_y + 35}" font-family="Arial" font-size="18" font-weight="bold" fill="#333">TOLERANCES</text>
        <text x="920" y="{title_y + 65}" font-family="Arial" font-size="16" fill="#666">Linear:</text>
        <text x="1050" y="{title_y + 65}" font-family="Arial" font-size="16" font-weight="bold" fill="#333">+/-{tolerance_linear} mm</text>
        <text x="920" y="{title_y + 90}" font-family="Arial" font-size="16" fill="#666">Diagonal:</text>
        <text x="1050" y="{title_y + 90}" font-family="Arial" font-size="16" font-weight="bold" fill="#333">+/-{tolerance_diagonal} mm</text>
        <text x="920" y="{title_y + 115}" font-family="Arial" font-size="16" fill="#666">Holes:</text>
        <text x="1050" y="{title_y + 115}" font-family="Arial" font-size="16" font-weight="bold" fill="#333">+/-{tolerance_hole} mm</text>
        <text x="920" y="{title_y + 140}" font-family="Arial" font-size="16" fill="#666">Thickness:</text>
        <text x="1050" y="{title_y + 140}" font-family="Arial" font-size="16" font-weight="bold" fill="#333">+/-{tolerance_thickness} mm</text>

        <!-- Approval -->
        <text x="1370" y="{title_y + 35}" font-family="Arial" font-size="18" font-weight="bold" fill="#333">APPROVAL</text>
        <text x="1370" y="{title_y + 70}" font-family="Arial" font-size="14" fill="#666">Drawn:</text>
        <line x1="1440" y1="{title_y + 70}" x2="1680" y2="{title_y + 70}" stroke="#ccc" stroke-width="1"/>
        <text x="1370" y="{title_y + 100}" font-family="Arial" font-size="14" fill="#666">Checked:</text>
        <line x1="1450" y1="{title_y + 100}" x2="1680" y2="{title_y + 100}" stroke="#ccc" stroke-width="1"/>
        <text x="1370" y="{title_y + 130}" font-family="Arial" font-size="14" fill="#666">Approved:</text>
        <line x1="1460" y1="{title_y + 130}" x2="1680" y2="{title_y + 130}" stroke="#ccc" stroke-width="1"/>

        <!-- Scale indicator -->
        <text x="1680" y="{title_y + 160}" text-anchor="end" font-family="Arial" font-size="14" fill="#666">Scale: NTS</text>
    </g>

    <!-- Legend -->
    <g id="legend" transform="translate({svg_width - 280}, {margin})">
        <text x="0" y="0" font-family="Arial" font-size="18" font-weight="bold" fill="#333">LEGEND</text>
        <line x1="0" y1="8" x2="180" y2="8" stroke="#333" stroke-width="1"/>

        <circle cx="15" cy="40" r="10" fill="none" stroke="#d32f2f" stroke-width="2"/>
        <text x="35" y="45" font-family="Arial" font-size="16" fill="#333">Hole</text>

        <line x1="5" y1="75" x2="25" y2="75" stroke="#666" stroke-width="2" stroke-dasharray="5,3"/>
        <text x="35" y="80" font-family="Arial" font-size="16" fill="#333">Section Line</text>

        <rect x="5" y="95" width="20" height="20" fill="url(#hatch)" stroke="#000" stroke-width="1"/>
        <text x="35" y="110" font-family="Arial" font-size="16" fill="#333">Glass Section</text>
    </g>

</svg>'''

        (self.output_dir / "technical_drawing.svg").write_text(svg, encoding='utf-8')
        self.generated_files.append("technical_drawing.svg")
    
    def _generate_validation_report(self, extraction: Dict[str, Any]) -> None:
        """Generate comprehensive JSON validation report."""
        dims = extraction.get("dimensions", {})
        holes = extraction.get("holes", [])
        sections = extraction.get("sections", [])

        width = dims.get("width", 0)
        height = dims.get("height", 0)
        thickness = dims.get("thickness", 0)

        # Calculate derived values
        diagonal = math.sqrt(width**2 + height**2)
        area_mm2 = width * height
        area_m2 = area_mm2 / 1_000_000
        weight = (width/1000) * (height/1000) * (thickness/1000) * 2500

        # Subtract hole volumes
        for hole in holes:
            d = hole.get("diameter", 0) / 1000
            hole_vol = math.pi * (d/2)**2 * (thickness/1000)
            weight -= hole_vol * 2500

        # Determine tolerances
        tolerance_linear = 1.5 if thickness <= 6 else (2.0 if thickness <= 10 else 3.0)
        tolerance_diagonal = 3.0
        tolerance_hole = 1.0
        tolerance_thickness = 0.5

        # Calculate min edge distances for holes
        min_edge_distance = max(thickness * 2, 25.0)

        # Validate holes
        hole_validations = []
        for i, hole in enumerate(holes):
            x = hole.get('x', 0)
            y = hole.get('y', 0)
            d = hole.get('diameter', 0)
            r = d / 2

            edge_left = x - r
            edge_right = width - x - r
            edge_bottom = y - r
            edge_top = height - y - r
            min_edge = min(edge_left, edge_right, edge_bottom, edge_top)

            hole_validations.append({
                "hole_number": i + 1,
                "position": {"x": x, "y": y},
                "diameter": d,
                "edge_distances": {
                    "left": round(edge_left, 2),
                    "right": round(edge_right, 2),
                    "bottom": round(edge_bottom, 2),
                    "top": round(edge_top, 2),
                    "minimum": round(min_edge, 2)
                },
                "min_required_edge": min_edge_distance,
                "valid": min_edge >= min_edge_distance
            })

        # Build report
        report = {
            "document_info": {
                "timestamp": self._timestamp.isoformat(),
                "generator": "Glass Manufacturing Skill v1.0",
                "format_version": "2.0",
                "standards": ["EN 12150-1", "ASTM C1048", "ISO 12543"]
            },
            "panel_specifications": {
                "dimensions": {
                    "width_mm": width,
                    "height_mm": height,
                    "thickness_mm": thickness,
                    "diagonal_mm": round(diagonal, 2)
                },
                "area": {
                    "mm2": round(area_mm2, 2),
                    "m2": round(area_m2, 4)
                },
                "weight_kg": round(weight, 3),
                "material": {
                    "glass_type": extraction.get("glass_type", "unknown"),
                    "edge_type": extraction.get("edge_type", "unknown")
                }
            },
            "tolerances": {
                "linear_mm": f"±{tolerance_linear}",
                "diagonal_mm": f"±{tolerance_diagonal}",
                "hole_position_mm": f"±{tolerance_hole}",
                "thickness_mm": f"±{tolerance_thickness}"
            },
            "holes": {
                "count": len(holes),
                "min_edge_distance_required": min_edge_distance,
                "details": hole_validations
            },
            "sections": {
                "count": len(sections),
                "details": sections
            },
            "validation": {
                "status": "validated",
                "checks": {
                    "dimensions_valid": width > 0 and height > 0 and thickness > 0,
                    "aspect_ratio_valid": max(width, height) / min(width, height) <= 10 if min(width, height) > 0 else False,
                    "holes_valid": all(h["valid"] for h in hole_validations) if hole_validations else True,
                    "thickness_adequate": thickness >= 4
                },
                "notes": extraction.get("notes", [])
            },
            "manufacturing_summary": {
                "cutting": {
                    "method": "CNC or manual score and break",
                    "stock_size_required": f"{width + 50}mm x {height + 50}mm minimum"
                },
                "drilling": {
                    "required": len(holes) > 0,
                    "tool": "Diamond core drill",
                    "coolant": "Water (continuous)",
                    "back_support": "Required"
                },
                "edge_processing": {
                    "type": extraction.get("edge_type", "flat_polished"),
                    "all_edges": True
                },
                "heat_treatment": {
                    "required": "tempered" in extraction.get("glass_type", "").lower(),
                    "type": "Full temper" if "tempered" in extraction.get("glass_type", "").lower() else "None"
                }
            }
        }

        (self.output_dir / "validation_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        self.generated_files.append("validation_report.json")
