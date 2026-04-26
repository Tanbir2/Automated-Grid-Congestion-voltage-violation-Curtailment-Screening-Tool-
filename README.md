# Automated Grid Congestion & Curtailment Screening Tool

## Overview
This project provides a Python-based automation framework for conducting high-resolution transmission planning studies. The tool automates **PSS®E** simulations to screen for thermal congestion and voltage violations within renewable-heavy transmission corridors, with a primary focus on Southeast Alberta.

By integrating historical **AESO** market data with PSS®E power flow models, the tool identifies grid bottlenecks and calculates required generator curtailment across 8,760 hourly scenarios.

## Key Features
* **Automated PSS®E Integration**: Leverages the `psspy` API to automate load/generation dispatch and contingency analysis ($N-0$ and $N-1$).
* **Hourly Time-Series Simulation**: Maps historical hourly shapes to static base cases for realistic dynamic planning.
* **Violation Screening**: Detects thermal overloads ($>100\%$ MVA) and bus voltage violations ($<0.95$ or $>1.05$ pu).
* **Interactive Analytics**: Includes a **Streamlit** dashboard for visualizing line loading, voltage profiles, and curtailment statistics.


## System Architecture
The tool follows a three-stage pipeline: **Data Processing → Simulation Engine → Visualization**.



## Technical Methodology

### 1. Load & Generation Dispatch
The tool maps hourly time-series data to PSS®E machines and loads. For assets sharing a Point of Interconnection (POI), a capability-weighted allocation logic is utilized:

$$P_{i}(t) = \min(P_{g}(t) \cdot w_{i}, P_{MAX,i})$$

Where:
* $w_{i}$ is the capability weight of machine $i$ relative to total plant capacity.
* $P_{g}(t)$ is the hourly metered volume for the asset group.

### 2. Violation Screening Logic
* **Thermal**: Monitors branch flows against Rate A (Normal) and Rate B (Emergency) limits.
* **Voltage**: Monitors all 100kV+ buses for deviations outside the standard $0.90–1.10$ pu range during contingencies.


## Data Sources & Inputs

This tool requires two primary inputs sourced from the **Alberta Electric System Operator (AESO)**:

1.  **System Topology**: AESO PSS®E Base Cases (`.sav` or `.raw` formats). 
    > **Note**: Base cases contain sensitive Critical Energy Infrastructure Information (CEII) and are not included in this repository.
2.  **Historical Market Data**:
    * **Alberta Internal Load (AIL)**: Hourly load data by planning area and region.
    * **Generation Metered Volumes**: Hourly MWh data for wind, solar, and thermal assets.



## Visualization & Dashboards
Results are processed into an interactive dashboard using **Streamlit**, allowing planners to:
* Identify the most frequently congested transmission corridors.
* Analyze **Active Power (MW)** flow vs. Voltage stability limits.
* Review total MWh lost to curtailment per generator.




## Installation & Usage

### Prerequisites
* Python 3.7
* PSS®E 34 or 35 (with valid license and environment variables set)
* Required Libraries: `pandas`, `streamlit`

### Quick Start
1. **Clone the repository**:
   ```bash
   git clone [https://github.com/Tanbir2/Automated-Grid-Congestion-voltage-violation-Curtailment-Screening-Tool-.git](https://github.com/Tanbir2/Automated-Grid-Congestion-voltage-violation-Curtailment-Screening-Tool-.git)
