# 3DPrint — Project Memory

## Purpose
A tool that lets Ricky describe an artistic/decorative 3D shape in plain conversational
English and receive a clean, printable STL file — without AI code bloat.

## Hardware / Software Context
- **Printer:** Bambu A1 series
- **Slicer:** Bambu Studio or Orca Slicer
- **Output format:** STL (standard, accepted by both slicers)

## Use Case
- **Artistic and decorative assemblies only** — not functional mechanical parts
- No tolerance or fit precision required (removes the hardest part of the problem)
- Back-and-forth conversation interface — Ricky describes, system asks clarifying
  questions, builds up a complete design spec before generating anything

## Key Architecture Decision
**Skip code generation entirely. Build geometry directly.**

The code bloat problem: when AI generates OpenSCAD or CadQuery code, it produces
overly verbose, deeply nested operations that result in messy meshes, huge polygon
counts, and non-manifold geometry.

The fix: use a Python mesh library (trimesh or numpy-stl) to construct geometry
directly in memory. No intermediate code. No compiler. Complexity stays linear.
Output is a clean manifold STL with only the triangles actually needed.

## Pipeline Design (proposed)
1. **Conversation layer** — asks clarifying questions, builds a structured JSON
   design spec from Ricky's description
2. **Geometry engine** — small library of clean shape primitives and operations
   (extrude, twist, pattern, shell, cut) that operate directly on mesh data
3. **STL exporter** — writes a valid, clean STL ready for Bambu Studio / Orca Slicer

## Open Questions (not yet answered)
1. Standalone decorative objects (vases, sculptures) OR multi-part loose assemblies
   (decorative boxes with lids, modular pieces)?
2. Preview image before STL is generated, or load straight into slicer to see it?
3. Personal use for Ricky only, or a product other people could use?

## Status
Concept only — not scaffolded, not built. Project name TBD.

## Next Steps (start of next session)
1. Answer the 3 open questions above
2. Confirm project name
3. Run /spike on trimesh vs numpy-stl vs build123d for direct mesh generation
4. Scaffold project, then /think for full pipeline design
