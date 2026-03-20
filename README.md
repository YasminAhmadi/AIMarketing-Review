# AIMarketing

AIMarketing is a Python toolkit for analyzing customer reviews and generating report assets such as charts, word clouds, and PDF/DOCX outputs.

## Features

- Review scoring and sentiment analysis
- Keyword and attribute extraction using LLM prompts
- Chart generation for trends and score distributions
- Word cloud generation
- PDF and DOCX report generation

## Project Structure

```text
AIMarketing/
├── config/
│   └── product_review_criteria.json
├── outputs/
│   ├── charts/
│   ├── logs/
│   ├── pdfs/
│   └── wordclouds/
├── src/
│   ├── review_analysis_toolkit.py
│   ├── report_generation/
│   │   ├── docx_generator.py
│   │   ├── pdf_generator.py
│   │   ├── styles.py
│   │   └── textProcessors.py
│   └── utils/
│       ├── chart_generator.py
│       ├── llm_call_functions.py
│       ├── prompts.py
│       └── wordcloud_images/
├── run.py
├── telegram_review_analytics.py
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/YasminAhmadi/AIMarketing-Review.git
cd AIMarketing-Review
pip install -r requirements.txt
```

## Usage

Run the main workflow:

```bash
python run.py
```

Optional scripts:

```bash
python src/review_analysis_toolkit.py
python telegram_review_analytics.py
```

## Notes

- Configure your environment variables (for example, API keys) locally in a `.env` file.
- Do not commit private datasets or credentials.

## Contributing

Pull requests and issues are welcome.

## License

This project is licensed under the MIT License.
