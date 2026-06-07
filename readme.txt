# 🧪 RDKit Studio

RDKit Studio is an interactive, high-performance web application designed for cheminformatics, computational chemistry, and drug discovery workflows. Built entirely on **Streamlit** and powered by the core **RDKit** library, this platform provides researchers, computational biologists, and students with an intuitive visual interface to handle structural drawing analysis, descriptor calculations, and molecular properties mapping.

---

## 🚀 Key Modules & Capabilities

* **Structure IO Processing:** Parse and structure chemical notations across SMILES string values or direct structural files.
* **Drug-Likeness Profiling:** Calculate and filter physical-chemical dimensions matching Lipinski's Rule of 5 (Molecular Weight, LogP, TPSA, HBD, HBA).
* **Substructure Mapping Engine:** Query specific chemical sub-fragments and automatically display highlighted target structural segments.
* **Fingerprints & Similarity:** Evaluate structural distance alignments, compute chemical similarity indexes, and extract molecular fingerprints.
* **Chemical Transformation:** Predict structural changes and map complex reactions dynamically.

---

## 📁 Repository Blueprint

As structured in this repository:
```text
├── 📁 modules/             # UI architectures and independent computational engines
├── app.py                  # Streamlit central app execution engine 
├── packages.txt            # System-level Linux graphics core configuration dependencies
└── requirements.txt        # Managed Python library execution requirements