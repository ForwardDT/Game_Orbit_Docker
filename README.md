# Orbital Docking Simulator (Game\_Orbit\_Docker)

A Python-based orbital mechanics game where you pilot a spacecraft to dock with the ISS, inspired by SpaceX rescue missions.

## Table of Contents

* [Features](#features)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [Controls](#controls)
* [File Structure](#file-structure)
* [Customization](#customization)
* [Contributing](#contributing)
* [License](#license)

## Features

* Realistic orbital physics for both your spacecraft and the ISS using inverse-square gravity.
* Thrust-based maneuvering with limited fuel and dynamic controls.
* Trail visualization to track orbital paths.
* Docking protocol with proximity and relative velocity checks.
* On-screen HUD showing speed, fuel, altitude, relative velocity, and distance to ISS.
* Tutorial tips and orbit prediction overlay.

## Prerequisites

* Python 3.7 or higher
* [pygame](https://www.pygame.org/news)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ForwardDT/Game_Orbit_Docker.git
   cd Game_Orbit_Docker
   ```
2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

No additional configuration is required. All parameters (gravity constants, thrust sensitivity, docking proximity, etc.) can be adjusted directly in `Orbit_docker_ISS_Spacex.py`.

## Usage

Run the simulator:

```bash
python Orbit_docker_ISS_Spacex.py
```

* A window will open displaying Earth, ISS (blue), and your spacecraft (green).
* Tutorial tips appear at the top. Press **N** to cycle tips.
* Toggle orbit prediction with **P**, restart mission with **R**.

## Controls

* **W**: Thrust forward
* **S**: Thrust backward
* **A**: Thrust left
* **D**: Thrust right
* **P**: Toggle orbit prediction overlay
* **R**: Restart mission
* **N**: Next tutorial tip

## File Structure

```
Game_Orbit_Docker/
├── Orbit_docker_ISS_Spacex.py   # Main game script
├── requirements.txt             # Dependencies
```

## Customization

* **Gravity Constants**: Adjust `G` (player) and `ISS_G` constants at the top of `Orbit_docker_ISS_Spacex.py`.
* **Start Parameters**: Modify `PLAYER_START_RADIUS`, `PLAYER_START_ANGLE`, and `PLAYER_START_SPEED`.
* **Docking Criteria**: Fine-tune `DOCKING_PROXIMITY_RADIUS`, `DOCKING_HOLD_TIME`, and relative velocity threshold in `check_docking()`.

## Contributing

Contributions and bug reports are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/YourFeature`.
3. Commit your changes: `git commit -m "Add feature description"`.
4. Push to your branch and open a Pull Request.

