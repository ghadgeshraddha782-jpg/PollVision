# PollVision — Dynamic Dataset Analyzer

PollVision is a Python-based data analysis application built with Streamlit. It allows users to upload datasets, clean data, explore statistical summaries, and generate interactive visualizations without writing code for each new dataset.

## Features

- **Dataset Upload:** Upload CSV files and preview the dataset.
- **Data Cleaning:** Handle missing values, remove duplicate rows, and standardize data where supported.
- **Dynamic Dashboard:** Explore different datasets using selectable columns and chart types.
- **Interactive Visualizations:** Generate bar charts, histograms, box plots, and line charts.
- **Statistical Insights:** Explore numerical summaries and categorical distributions.
- **Data Filtering:** Filter records and inspect the resulting data.
- **CSV Export:** Download the cleaned dataset for further analysis.
- **User-Friendly Interface:** A responsive interface with a dark teal and mint visual theme.

## Tech Stack

- **Language:** Python
- **Web Framework:** Streamlit
- **Data Processing:** Pandas
- **Visualization:** Plotly and other libraries listed in `requirements.txt`

## Project Structure

```text
Poll-Results-Visualizer/
├── app.py
├── requirements.txt
├── .gitignore
└── data/
    └── raw/
        ├── sample_poll.csv
        ├── test_poll_data.csv
        └── cleaned_poll_data.csv
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ghadgeshraddha782-jpg/PollVision.git
cd PollVision
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m streamlit run app.py
```

Streamlit will provide a local URL in the terminal. Open that URL in your browser to use PollVision.

## How to Use

1. Launch the application.
2. Open the dataset upload section and upload a CSV file.
3. Preview the data and inspect its columns.
4. Use the data cleaning options to prepare the dataset.
5. Explore the dashboard by selecting columns and visualization types.
6. Review statistical insights and apply filters.
7. Download the cleaned dataset if needed.

## Testing

The application has been tested with the Iris dataset to check CSV upload, data cleaning, categorical counts, numerical visualizations, filtering, and statistical summaries.

Further testing with additional datasets is recommended to verify compatibility with different data types, column formats, and dataset sizes.

## Future Improvements

- Deploy the application online.
- Support larger datasets efficiently.
- Improve automatic data-type detection.
- Add more visualization options and downloadable reports.
- Add automated tests for data cleaning and dashboard calculations.

## Author

**Shraddha Ghadge**

GitHub: [ghadgeshraddha782-jpg](https://github.com/ghadgeshraddha782-jpg)

LinkedIn: [Shraddha Ghadge](https://www.linkedin.com/in/shraddha-ghadge)

---

*PollVision — Turn raw datasets into meaningful insights.*
