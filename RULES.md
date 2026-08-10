
# Project Organization Rules

This document defines the rules and guidelines for organizing projects within the NERo ecosystem. It covers naming conventions, folder structure, best practices, and recommended technologies to ensure consistency and maintainability across all projects.

---

## Quick Access
- [Project Naming](#project-naming)
- [Folder Structure](#folder-structure)
- [Best Practices](#best-practices)

---

## 📁 Project Naming
Every project must fit into one of the following categories, using the appropriate prefix:

### 🤖 Ground & Mechanics: `robot-(project-name)`
For all physical systems that operate on the ground.
- **Scope:** Robotic arms, rovers, bipeds, industrial automation, etc.
- **Key Distinction:** If it stays on the ground, it belongs here.

### 🚁 Aerial & Hybrids: `aero-(project-name)`
For aerial vehicles and hybrid systems.
- **Scope:** Multirotors, fixed-wing aircraft, VTOL (Vertical Take-Off and Landing) systems.
- **Hybrid Note:** If the project operates both on the ground and in the air, it should be categorized here.

### 💻 Pure Software: `code-(project-name)`
For software-only projects.
- **Scope:** Neural networks, web dashboards, API integrations, App, and other digital products not tied to specific hardware.

### 🧮 Numerical Computing: `aurora-(project-name)`
For MATLAB and numerical computing projects.
- **Scope:** Simulations, control system tuning, signal processing scripts, etc.
- **Tip:** If a project is both MATLAB-based and related to aerial or ground systems, choose the prefix that best matches the project's primary focus (language vs. application).

---

## 📂 Folder Structure


Organize your project using the following standard folders:

- `CAD/`: Contains all files related to mechanical design, including 3D models (such as .stl, .step), technical drawings, and documentation for the physical structure of the robot or device.
- `eletronics/`: Stores electronic design files, such as schematics, PCB layouts, bills of materials (BOM), and any documentation related to the electronic circuits and hardware.
- `firmware/`: Holds the source code and configuration files for microcontrollers and embedded systems, typically developed using PlatformIO or similar tools.
- `software/`: Includes applications, scripts, user interfaces, and supporting tools that run on computers or external devices to interact with or control the robot.

---


## ⚙️ Tech Stack
- ### [Git](https://git-scm.com/)
    All projects must use Git for version control. Keep your repository clean and organized, and avoid committing generated or build files.
    Commit messages should follow these conventions:
        - **addition:** For new features, files, or significant content added to the project.
        - **update:** For improvements, refactoring, or changes to existing features or documentation.
        - **fix:** For bug fixes, corrections, or resolving issues.
    
    Example: `addition: add motor driver module` / `update: improve sensor calibration` / `fix: correct PCB netlist error`

- ### [PlatformIO](https://platformio.org/)
    For projects using an Arduino or an ESP32 for example, it should use the PlatformIO with VSCode. All `robot-*` type project should use it. This ensures consistency, portability, and easier collaboration.


---

## 🌟 Best Practices


- Use clear and consistent file and folder naming conventions.
- Document all significant changes in the README.md of each folder.
- Write meaningful and descriptive commit messages.
- Ensure all contributions are reviewed before merging into the main branch.
- Comment code and designs where necessary to aid understanding and maintenance.
- Use appropriate version control and dependency management tools for each area.
- Prioritize code and component reuse when possible.
- Maintain open and clear communication with all team members.

---
> These guidelines are designed to help you keep your project organized, maintainable, and collaborative—whether for a personal portfolio or a team environment.