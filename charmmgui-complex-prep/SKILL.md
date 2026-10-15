---
name: charmmgui-complex-prep
description: Prepare a receptor-ligand complex for CHARMM-GUI and later MD from a receptor plus ligand or an existing complex. Use when spatial pose selection, clash-relief minimization, CGenFF rtf/prm generation, or periodic-boundary-safe PDB export is required; do not use to invent an unvalidated binding pose.
---

# CHARMM-GUI Complex Preparation

Produce an auditable, continuous-coordinate complex that can be uploaded to
CHARMM-GUI Solution Builder. Accept either:

- receptor and ligand files, with a user-supplied or reproducible docked pose; or
- a complete receptor-ligand complex needing validation and local repair.

Do not claim that a structure is MD-ready merely because it is a PDB. A
scientifically usable result requires a credible pose, chemical consistency,
matching CHARMM ligand parameters, no catastrophic contacts, and an
unwrapped/continuous exported coordinate set.

## Choose The Starting Route

1. Inventory all supplied structures, formats, atom/residue names, hydrogens,
   chains, and any existing topology/parameter files. Preserve the user's
   original structures; write derived outputs to a dedicated results directory.
2. For an existing complex, use it only if the ligand is complete and placed in
   a plausible binding site. For separate receptor and ligand files, require a
   documented docking/experimental pose. If no pose exists, perform or request
   a reproducible docking/placement workflow before rebuilding a full complex.
   Never fabricate a pose from an arbitrary superposition.
3. Assign the ligand residue name `LIG`. Confirm that PDB/SDF/MOL2 atom order
   and atom names are identical to the topology ultimately used for `LIG`.

## Chemical And Parameter Gate

1. Validate ligand valence, formal charge, protonation state, aromaticity, and
   3D conformer. Explicit hydrogens must be chemically sensible.
2. Use CHARMM-GUI Ligand Reader & Modeler / CGenFF (or an approved equivalent)
   to obtain `lig.rtf` and `lig.prm`. Keep the exact job output with the result.
3. Read CGenFF penalties. High penalties mean the topology can support a
   geometry-repair run but are not evidence for production-quality MD. Flag
   parameters needing ParamChem/QM refinement; do not hide this limitation.
4. The final PDB's `LIG` atom names must match `lig.rtf`. If using a GROMACS
   `LIG.itp`, verify its atom sequence against the PDB before any minimization.

## Pose Selection And Local Clash Relief

Use the user-selected/best scored pose only after checking binding-site
contacts and obvious protein-ligand penetration. For a flexible multisegment
ligand whose FAP04-like anchor has a reliable pose:

- restrain the mapped anchor atoms to the selected pose;
- restrain protein heavy atoms initially;
- leave all other ligand atoms mobile;
- perform pre-relaxation only when sub-angstrom overlaps cause non-finite
  forces, then rerun CHARMM36 local energy minimization.

Do not use a pre-relaxation coordinate tweak as scientific MD. It exists only
to put a catastrophically overlapping starting model into the numerical basin
of a force-field minimizer. Follow it with force-field minimization and record
both stages.

Use the output quality gates in [references/quality-gates.md](references/quality-gates.md).
The optional validator at [scripts/validate_complex_pdb.py](scripts/validate_complex_pdb.py)
checks PDB-level continuity and obvious long bonds after export; it does not
replace chemistry review or trajectory analysis.

## Periodic-Boundary Invariant

When minimization is run with periodic boundaries, never export wrapped GRO
coordinates directly as a CHARMM-GUI PDB. Restore every atom to the periodic
image nearest to the continuous reference complex before PDB export. Then
check the protein backbone and ligand `CONECT` bonds for implausibly long
distances. A preview showing long parallel lines across the screen is a PBC
display artifact that must be fixed by unwrapping, not ignored.

## Deliverables

Create a result directory containing:

- `*_continuous.pdb`: continuous-coordinate receptor-LIG complex for upload;
- minimized `.gro`/`.pdb`, final topology and restraint inputs when local
  minimization was performed;
- `lig.rtf` and `lig.prm`, with the original CGenFF/CHARMM-GUI job artifacts;
- a text/Markdown report with input provenance, pose choice, restraint atom
  mapping, minimization convergence, potential energy, maximum force, closest
  protein-LIG heavy-atom distance, and remaining caveats;
- executable scripts or exact commands sufficient to reproduce the result.

## CHARMM-GUI Handoff

Upload only `*_continuous.pdb` to a new Solution Builder job. In PDB Reader,
confirm the protein chain(s) and `LIG` hetero chain, upload the matching
`lig.rtf` and `lig.prm`, and normally let CHARMM-GUI rebuild hydrogens rather
than preserving GROMACS-generated H coordinates. Build solvent/ions and run
staged equilibration before production MD.
