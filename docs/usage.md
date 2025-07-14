# Usage Guide

## Prerequisites

1. Python 3.10 or higher
2. API keys for:
   - GitHub Personal Access Token
   - OpenRouter API Key
   - ScrapeGraphAI API Key

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/github-star-to-company-agent.git
cd github-star-to-company-agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root with your API keys:

```env
GITHUB_TOKEN=your_github_personal_access_token
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
SGAI_API_KEY=your_scrapegraphai_api_key
```

#### Getting API Keys:

- **GitHub Token**: Go to GitHub Settings → Developer settings → Personal access tokens → Generate new token
- **OpenRouter API Key**: Sign up at [OpenRouter](https://openrouter.ai) and get your API key
- **ScrapeGraphAI API Key**: Sign up at [ScrapeGraphAI Dashboard](https://dashboard.scrapegraphai.com) and get your API key

## Running the Application

### Start the Streamlit App

```bash
streamlit run src/app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Using the Interface

1. **Enter Repository**: Input a GitHub repository in the format `owner/repo` (e.g., `ScrapeGraphAI/Scrapegraph-ai`)
2. **Click Analyze**: Press the "Analyze Repository" button to start the analysis
3. **View Results**: The agent will:
   - Fetch stargazers from the repository
   - Trace them to their companies
   - Evaluate companies as potential sales targets
   - Display ranked results

### Advanced Settings

In the sidebar, you can adjust:
- **Max companies to display**: Limit the number of results shown
- **Minimum score threshold**: Filter out low-scoring companies

## Understanding Results

### Company Scores (0-100)

- **70-100**: High Priority - Excellent fit for AI scraping infrastructure
- **50-69**: Medium Priority - Good potential, worth exploring
- **30-49**: Low Priority - Some relevance, but not ideal
- **0-29**: Not Recommended - Poor fit

### Evaluation Criteria

Companies are scored based on:
- **Technology Stack**: Use of AI, ML, data analytics, scraping
- **Industry**: E-commerce, fintech, SaaS, analytics
- **Company Size**: Larger companies score higher
- **Growth Indicators**: Funding, hiring, expansion
- **Data Needs**: Explicit mentions of data collection needs

## Programmatic Usage

You can also use the agent programmatically:

```python
from src.agent import run_agent

result = run_agent("facebook/react")

if result["success"]:
    for company in result["evaluations"][:10]:
        print(f"{company['company']}: Score {company['score']} - {company['recommendation']}")
else:
    print(f"Error: {result['error']}")
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run specific tests:

```bash
python tests/test_agent.py
```

## Troubleshooting

### Common Issues

1. **"API key missing" errors**
   - Ensure all API keys are correctly set in the `.env` file
   - Check that the `.env` file is in the project root directory

2. **Rate limiting errors**
   - The agent automatically limits requests to avoid rate limiting
   - If you still hit limits, wait a few minutes before retrying

3. **No companies found**
   - Some repositories may have stargazers without company information
   - Try repositories with more enterprise/professional users

4. **Scraping errors**
   - Some company websites may block scraping
   - The agent will still provide evaluation based on available information

## Ethical Considerations

- Respect GitHub's rate limits and terms of service
- Use scraped data responsibly and ethically
- Don't use the tool for spam or unsolicited outreach
- Respect privacy and data protection regulations

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the error messages in the Streamlit interface
3. Open an issue on the GitHub repository