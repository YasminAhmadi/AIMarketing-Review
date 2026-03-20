# AIMarketing

## Table of Contents

- [AIMarketing](#aimarketing)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Directory Structure](#directory-structure)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Scripts and Directories Explained](#scripts-and-directories-explained)
    - [Directories](#directories)
  - [Contributing](#contributing)
  - [Version History](#version-history)
  - [License](#license)

## Project Overview

AIMarketing is a toolkit designed to analyze customer reviews and generate insightful reports, including charts and word clouds, and export the analysis into PDF format.

## Directory Structure

```plaintext
AIMarketing/
│
├── config/
│   └── product_review_criteria.json  # Configuration file for product review criteria
│   └── wordcloud_images
│       ├── dislike.png  
|       └── like.png      
│
├── outputs/
│   ├── charts/          # Directory containing generated charts
│   ├── logs/            # Directory containing log files
│   ├── wordclouds/      # Directory containing generated word clouds
│   ├── pdfs/            # Directory containing generated PDF reports
│   └── docx/            # Directory containing generated docx reports
│
├── src/
│   ├── review_analysis_toolkit.py  # Main script for review analysis
│   ├── report_generation/
│   │   ├── pdf_generator.py  # Script for generating PDF reports
│   │   └── docx_generator.py  # Script for generating docx reports
│   └── utils/                      # Utility functions and scripts
│       ├── chart_generator.py  # Script for generating charts
│       ├── llm_call_functions.py        # Script for calling and interfacing with large language models
│       └── prompts.py                   # Script for managing and organizing prompts
│       └── wordcloud_images
│           ├── dislike.png  
|           └── like.png
│
├── README.md            # Project readme file
│
└── requirements.txt
```

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/alldbi/AImarketing.git
   cd AIMarketing
   ```

2. **Install the necessary dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Review Analysis:**
   - To analyze reviews, run the `review_analysis_toolkit.py` script located in the `src` directory.
  
   ```bash
   python src/review_analysis_toolkit.py
   ```

2. **Generate PDF or DOCX Report:**
   - To generate a PDF report from the analysis results, run the `pdf_generator.py` script located in the `report_generation` directory.

   ```bash
   python report_generation/pdf_generator.py
   ```

   - To generate a docx report from the analysis results, run the `docx_generator.py` script located in the `report_generation` directory.

   ```bash
   python report_generation/docx_generator.py
   ```

## Scripts and Directories Explained

### Directories

- **config/**
  - `product_review_criteria.json`: Configuration file for specifying the criteria for analyzing product reviews.

- **outputs/**
  - `charts`/: Directory containing generated charts from the analysis.
  - `logs`/: Directory containing log files for tracking the execution of scripts.
  - `wordclouds`/: Directory containing generated word clouds from the analysis.
  - `pdfs`/: Directory containing generated PDF reports.
  - `docs`/: Directory containing generated docx reports.

- **src/**
  - `review_analysis_toolkit.py`: Main script for performing review analysis, including data loading, processing, and generating insights.
  - `report_generation`/: Directory containing generating PDF and DOCX reports script.
    - `pdf_generator.py`: Script responsible for generating PDF reports from the analysis results.
    - `docx_generator.py`: Script responsible for generating docx reports from the analysis results.
  - `utils`/: Directory for utility functions and scripts used by the main analysis tool.
    - `chart_generator.py`: Contains functions for generating charts from the analysis data.
    - `llm_call_functions.py`: Contains functions for interfacing with large language models (LLMs) for additional insights or processing.
    - `prompts.py`: Manages and organizes prompts used for interacting with LLMs or other components.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas for improvements.

## Version History

- **v1.0.0**

  - Initial release with basic review analysis and PDF generation functionality.

- **v1.0.1**

  - Added editable report script.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
