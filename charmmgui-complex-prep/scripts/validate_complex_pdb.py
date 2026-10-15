#!/usr/bin/env python3
"""Report PDB features that commonly reveal wrapped or broken MD exports.

Usage: python validate_complex_pdb.py path/to/complex_continuous.pdb
"""
from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.dist(a, b)


def parse_atom(line: str) -> dict[str, object]:
    return {
        "serial": int(line[6:11]),
        "name": line[12:16].strip(),
        "resname": line[17:20].strip(),
        "chain": line[21].strip() or "_",
        "resid": int(line[22:26]),
        "xyz": (float(line[30:38]), float(line[38:46]), float(line[46:54])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdb", type=Path)
    parser.add_argument("--ligand-resname", default="LIG")
    parser.add_argument("--long-bond", type=float, default=5.0, help="Warning threshold in Angstrom")
    args = parser.parse_args()

    atoms: list[dict[str, object]] = []
    conect: list[tuple[int, int]] = []
    for line in args.pdb.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(("ATOM  ", "HETATM")):
            atoms.append(parse_atom(line))
        elif line.startswith("CONECT"):
            fields = line.split()
            if len(fields) > 2:
                conect.extend((int(fields[1]), int(value)) for value in fields[2:])

    if not atoms:
        raise SystemExit("No ATOM/HETATM records found.")

    xyz = [atom["xyz"] for atom in atoms]
    spans = [max(point[i] for point in xyz) - min(point[i] for point in xyz) for i in range(3)]
    ligand = [atom for atom in atoms if atom["resname"] == args.ligand_resname]
    protein = [atom for atom in atoms if atom["resname"] != args.ligand_resname]
    print(f"atoms: {len(atoms)}; protein/non-LIG: {len(protein)}; {args.ligand_resname}: {len(ligand)}")
    print("coordinate span (A): " + ", ".join(f"{value:.2f}" for value in spans))

    by_residue: dict[tuple[str, int], dict[str, dict[str, object]]] = defaultdict(dict)
    for atom in protein:
        by_residue[(str(atom["chain"]), int(atom["resid"]))][str(atom["name"])] = atom
    backbone_warnings = []
    for (chain, resid), residue in by_residue.items():
        successor = by_residue.get((chain, resid + 1), {})
        if "C" in residue and "N" in successor:
            length = distance(residue["C"]["xyz"], successor["N"]["xyz"])
            if length > args.long_bond:
                backbone_warnings.append((chain, resid, length))
    if backbone_warnings:
        print("WARNING: long consecutive protein C-N distances:")
        for chain, resid, length in backbone_warnings[:20]:
            print(f"  chain {chain}, residues {resid}-{resid + 1}: {length:.2f} A")
    else:
        print("protein backbone continuity: no consecutive C-N distance above threshold")

    serials = {int(atom["serial"]): atom for atom in atoms}
    long_conect = []
    for source, target in conect:
        if source in serials and target in serials:
            length = distance(serials[source]["xyz"], serials[target]["xyz"])
            if length > args.long_bond:
                long_conect.append((source, target, length))
    if long_conect:
        print("WARNING: long CONECT distances:")
        for source, target, length in long_conect[:20]:
            print(f"  {source}-{target}: {length:.2f} A")
    elif conect:
        print("CONECT continuity: no bond above threshold")
    else:
        print("CONECT continuity: no CONECT records present; inspect ligand bonds in a viewer")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
