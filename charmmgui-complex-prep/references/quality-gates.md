# Quality Gates

## Before Minimization

- A receptor chain and a single intended ligand residue are unambiguously identified.
- `LIG` has a chemically valid 3D form, appropriate protonation for the stated pH/assay context, and no implausible valence or broken ring.
- The pose is traceable to docking, experiment, or a declared modelling procedure. A docking score alone does not establish binding.
- `lig.rtf`/`lig.prm` and the PDB use the same atom names and atom order.

## After Local Minimization

- The minimizer reaches its declared force criterion; record the threshold and final maximum force.
- Report protein-LIG heavy-atom contacts below 1.2, 1.5, and 2.0 A. Any remaining contact below 1.2 A is a hard failure. Contacts between 1.2 and 2.0 A require structure inspection rather than automatic acceptance.
- Report the smallest protein-LIG heavy-atom distance and anchor RMSD when an anchor restraint is used.
- Confirm the FAP04-like anchor did not cross a periodic boundary relative to its reference pose.

## Before CHARMM-GUI Upload

- Use a continuous PDB, not wrapped periodic coordinates.
- Inspect the PDB in a molecular viewer. No peptide or ligand bonds may span the simulation box.
- Run `validate_complex_pdb.py`. Review every warning; a large backbone or `CONECT` bond distance can indicate PBC wrapping, a missing residue, or a genuinely broken structure.
- Preserve the original pose, minimization logs, restraint mapping, and parameter warnings alongside the final PDB.

## Interpretation Boundary

This workflow prepares a plausible starting structure. It does not prove a binding mode, binding affinity, self-assembly mechanism, or production-MD stability. Those claims require independent sampling and analysis.
