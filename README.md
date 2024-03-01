# Installation:

Follow those steps to set up the model on a new system:

### 1) Install Pycharm (or other IDE)

- **URL**: https://www.jetbrains.com/de-de/pycharm/

### 2) Install Python

- **URL**: https://www.python.org/
- **Version requirement**: 3.11 or newer

### 3) Install Poetry Package Manager:

Poetry can be installed using windows powershell or pipx:

```shell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

```pipx
pipx install poetry
```

- **URL**: https://python-poetry.org/docs/
- **Version requirement**: 1.7 or newer

The path to the poetry-executable file must be specified within the path-environment-variable!

### 4) Install Gurobi

Download Gurobi from the official website:

- **URL**: [Gurobi Downloads](https://www.gurobi.com/downloads/)
- **Version Requirement**: 11.0.0 or newer

### 5) Copy repository from git

- **URL**: https://github.com/KammererSimon/FactoryFlexibilityModel.git

### 6) Create Poetry Python environment

In the python terminal execute:

```
poetry install
```

### 7) Create Desktop Shortcut to Tool GUI

In the python terminal execute:

```
poetry run create_shortcut
```

This will create a batch file to execute the kivy-gui as well as a shortcut to it on your Desktop

# Quickstart Instructions

### 1) Opening the GUI

To start the user interface for simulation architecture setup, use the desktop shortcut or run the following command:

```shell
poetry run gui
```

### 2) Performing a simulation:

To simulate a session save it with the gui and then call:

```shell
poetry run simulate [session_folder_path]
```

To simulate the demo sessions just execute:

```shell
poetry run examples\Demo_01
poetry run examples\Demo_02
```

### 3) Showing result dashboard on a simulated model run:

To show the results of a performed simulation execute:

```shell
poetry run dashboard [simulation_object]
```

with [simulation_object] being a .sim file within session_folder\simulations
