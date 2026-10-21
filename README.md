# Focal Technologies — Prototypes Repository

> **Course:** Duke University • MENG 570 Product Management  
> **Team:** Focal Technologies  

This repository houses the interactive digital product prototypes developed by the Focal Technologies team for Duke MENG 570.

---

## Prototypes Directory

| Prototype | Target Persona | Focus / Hypothesis | Directory | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Focal Monitor — Prototype A** | **Riley** (Adults concerned about vision changes between exams) | Adults concerned about changes in their vision will perceive ongoing vision tracking as more useful than receiving a single test result. | [`prototypes/prototype-a-riley-vision-tracking/`](prototypes/prototype-a-riley-vision-tracking/) | Ready for Review |
| **Prototype B** | *Team Persona B* | *Under Development* | *TBD* | Upcoming |
| **Prototype C** | *Team Persona C* | *Under Development* | *TBD* | Upcoming |

---

## Quick Start — Prototype A (Focal Monitor)

To run **Prototype A** locally on your machine:

1. **Navigate to the prototype directory:**
   ```bash
   cd prototypes/prototype-a-riley-vision-tracking
   ```

2. **(Optional) Set up a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\Activate.ps1
   # macOS / Linux:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

5. **Run automated test suites:**
   ```bash
   python -m unittest test_app.py
   python -m unittest test_regression.py
   ```

For detailed specifications, customer journey details, research guardrails, and accessibility notes, refer to the [Prototype A README](prototypes/prototype-a-riley-vision-tracking/README.md).

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
