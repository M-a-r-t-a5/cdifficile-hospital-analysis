# C. difficile Hospital Analysis
MAT2007 programming project analysing C. difficile Standardized Infection Ratios across US hospitals.

This project analyses C. difficile Standardized Infection Ratios (SIR) across US hospitals using the CMS Healthcare Associated Infections Hospital dataset.

## Research Question
Where in the US would I want to be hospitalized if I wanted the lowest risk of C. difficile infection?

## Files
- Final project.py – Python code used for the analysis
- MAT2007__project_pt_2 (2).pdf - written report
- MAT2007__project_pt_2.zip - latex version of report
- plot1.png, plot2.png, plot3.png – figures produced by the code

## Dataset
The dataset used is the CMS Healthcare Associated Infections - Hospital dataset:
https://data.cms.gov/provider-data/dataset/77hc-ibv8
The dataset contains hospital-level information on several healthcare-associated infections.

## What the script does
- Cleans the Score column
- Filters Standardized Infection Ratio data
- Focuses on C. difficile
- Calculates state average SIR values
- Calculates standard error
- Compares the lowest and highest states
- Calculates correlations with other infection types
- Produces three plots

## Requirements
The code requires Python and the following libraries:
- pandas
- numpy
- matplotlib

They can be installed using:
```bash
pip install pandas numpy matplotlib
