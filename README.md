# Energy Operations Platform

## Overview

The **Energy Operations Platform** is a growing Python-based backend and data project for processing, validating and analyzing technical energy and station data.

The current version focuses on a small but clean data-processing core: station data is imported from CSV, transformed into Python objects, validated, analyzed and reported. Invalid or missing values are handled robustly and documented through logging.

This project is part of a structured learning path toward backend, data and cloud development with a focus on industrial and energy-related software systems.

---

## Project Goal

The goal of this project is to build a realistic technical backend and data platform step by step.

The long-term vision is a system that can:

* process technical asset and measurement data,
* validate incoming data,
* calculate key figures,
* classify operating states,
* create alerts,
* store data in a database,
* expose data through REST APIs,
* and later be containerized and deployed.

The project is intentionally not a generic tutorial app. It is designed around technical data, energy systems and asset monitoring scenarios.

---

## Current Version

**Current version:** `v0.32`

The current version focuses on:

* object-oriented station modeling,
* CSV-based data import,
* robust handling of invalid and missing values,
* report generation,
* basic logging,
* and a clean separation of responsibilities between modules.

---

## Current Features

The project currently supports the following functionality:

* CSV file with station and load data is read.
* Each CSV row is converted into a `Station` object.
* Valid load values are stored and processed.
* Invalid load values, such as text instead of numbers, do not stop the program.
* Invalid values are detected as data-quality problems and logged.
* Missing values are detected, skipped and logged.
* Stations without enough valid load values are handled safely in the report.
* Additional station data is imported from `server.py`.
* `server.py` currently acts as a placeholder for a future external data source or server interface.
* Reports are generated for valid stations.
* The report includes average load, minimum load, maximum load and classification.
* Program execution and data-quality problems are written to `app.log`.

---

## Project Structure

| File                | Responsibility                                                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `main.py`           | Entry point of the program. Controls the overall workflow and configures logging.                                     |
| `station.py`        | Contains the `Station` class, station-related calculations, classification, report generation and CSV-row conversion. |
| `read_documents.py` | Reads station data from a CSV file.                                                                                   |
| `server.py`         | Simulates additional external station data. Placeholder for future server/API-based data sources.                     |
| `stations.csv`      | Example input data for stations and load values.                                                                      |
| `app.log`           | Log file containing program flow and data-quality warnings.                                                           |

---

## Technologies Used

### Currently used

* Python
* Object-oriented programming
* CSV file processing
* Error handling
* Logging
* Modular project structure

### Planned for later versions

* Git and GitHub
* SQL
* PostgreSQL
* FastAPI
* REST APIs
* Docker
* Azure basics
* Testing
* Monitoring
* Security basics

---

## How to Run

### Requirements

* Python installed
* Project files available locally

### Run the program

Open a terminal in the project folder and run:

```bash
python main.py
```

The program reads station data, creates station objects, processes load values and prints reports for valid stations.

A log file named `app.log` is created or updated during execution.

---

## Example Input

Example structure of `stations.csv`:

```csv
Station,Load1,Load2,Load3
Station A,80,95,xyz
Station B,110,130,150
Station C,200,220,240
Station D,120,,
Station E,,,
```

The program processes valid values and logs invalid or missing values.

---

## Example Behavior

If a station contains valid load values, the program generates a report.

Example:

```text
Station B
Average Load: 130.0
Minimum Load: 110
Maximum Load: 150
Classification: NORMAL
```

If a value is invalid, for example `xyz`, the program does not stop. The invalid value is skipped and logged.

If a station has no valid load values, no calculation is performed for that station.

---

## Error Handling and Logging

The project uses Python logging to make program behavior and data-quality issues traceable.

Examples of logged events:

| Situation                         | Log Level | Meaning                                        |
| --------------------------------- | --------- | ---------------------------------------------- |
| Program started                   | `INFO`    | Normal program flow                            |
| CSV file is being read            | `INFO`    | Normal program flow                            |
| Station imported successfully     | `DEBUG`   | Detailed development information               |
| Missing load value                | `WARNING` | Data-quality issue                             |
| Invalid load value                | `WARNING` | Data-quality issue                             |
| Not enough load values for report | `WARNING` | Data-quality issue                             |
| File not found                    | `ERROR`   | Program cannot process the expected input file |

This distinction is important because not every data problem should stop the program. Invalid or missing measurement values are handled as data-quality warnings, while missing files are treated as actual processing errors.

---

## Version History

| Version | Description                                                                                                           |
| ------- | --------------------------------------------------------------------------------------------------------------------- |
| `v0.1`  | First Python script with station data stored directly in code. Basic calculations and classification.                 |
| `v0.2`  | External data sources introduced. Station data loaded from text/CSV files. Basic error handling added.                |
| `v0.3`  | First object-oriented structure with a `Station` class. CSV rows are converted into station objects.                  |
| `v0.31` | Refactoring of CSV conversion into `Station.from_csv_row()`. More robust handling of invalid and missing load values. |
| `v0.32` | Basic logging introduced. Program flow and data-quality issues are written to `app.log`. Code structure cleaned up.   |

---

## Learning Goals Covered So Far

The current project version demonstrates practical knowledge in:

* Python basics,
* functions and return values,
* modules and imports,
* object-oriented programming,
* class methods,
* special methods such as `__str__` and `__repr__`,
* CSV processing,
* validation of external input data,
* defensive programming,
* basic logging,
* and separation of responsibilities between files.

---

## Roadmap

The project will be extended step by step.

### Next steps

* Initialize Git repository.
* Create first structured Git commits.
* Improve and maintain `README.md`.
* Start SQL basics.
* Design first PostgreSQL data model for:

  * assets,
  * measurements,
  * alerts.

### Later planned steps

* Add PostgreSQL persistence.
* Build REST API with FastAPI.
* Add API endpoints for assets, measurements and alerts.
* Add basic tests.
* Add Docker setup.
* Add basic deployment scenario.
* Add monitoring and security basics.
* Extend the project toward a more complete Energy Operations Platform.

---

## Long-Term Vision

The long-term goal is to evolve this project from a local Python data analyzer into a backend-oriented energy and asset data platform.

Possible future extensions include:

* solar park assets,
* wind park assets,
* battery storage assets,
* substations,
* measurement history,
* alert generation,
* KPI dashboards,
* weather data integration,
* forecasting,
* anomaly detection,
* and optional cloud deployment.

These features are planned as later extensions. The current focus is on building a clean and reliable backend foundation step by step.

---

## Learning and Career Context

This project is part of a structured six-month transition from mechanical engineering, technical development and technical project leadership toward backend, data and cloud development.

The focus is on roles where technical domain knowledge and software skills can be combined, especially in:

* industrial software,
* energy systems,
* asset monitoring,
* data platforms,
* backend services,
* and technical digitalization.

The project is intended to become a practical GitHub portfolio that demonstrates continuous learning, technical implementation and software architecture thinking.
