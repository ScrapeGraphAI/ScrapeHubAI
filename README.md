# ScrapeHubAI

An open-source LangGraph-based agent that analyzes GitHub stargazers, traces them to their companies, and evaluates these companies as potential sales targets for AI scraping infrastructure.

## 🌟 Features

- **GitHub Stargazer Analysis**: Fetches and analyzes users who starred a repository
- **Company Identification**: Traces GitHub users to their affiliated companies
- **Intelligent Evaluation**: Scores companies based on size, industry, and technology fit
- **Web Scraping**: Uses ScrapeGraphAI API to gather additional company information
- **Beautiful UI**: Streamlit-based interface for easy interaction
- **Export Results**: Download analysis results as CSV for further processing

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- API keys for GitHub, OpenRouter, and ScrapeGraphAI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ScrapeHubAI.git
cd ScrapeHubAI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys:

#### Getting a GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token" → "Generate new token (classic)"
3. Give your token a descriptive name (e.g., "ScrapeHub")
4. Select the following scopes:
   - `public_repo` (required for reading public repositories)
   - `read:user` (optional, for better user information)
   - `read:org` (optional, for organization information)
5. Click "Generate token" at the bottom
6. **Important**: Copy your token immediately - you won't be able to see it again!

#### Setting up your `.env` file

Create a `.env` file in the project root:
```env
GITHUB_TOKEN=your_github_personal_access_token
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
SGAI_API_KEY=your_scrapegraphai_api_key
```

Or copy from the example:
```bash
cp .env.example .env
# Then edit .env with your actual API keys
```

#### Getting Other API Keys

- **OpenRouter**: Sign up at [OpenRouter.ai](https://openrouter.ai) and get your API key from the dashboard
- **ScrapeGraphAI**: Register at [dashboard.scrapegraphai.com](https://dashboard.scrapegraphai.com) and obtain your API key

4. Run the application:
```bash
streamlit run src/app.py
```

## 📊 How It Works

1. **Fetch Stargazers**: The agent retrieves users who starred the specified GitHub repository
2. **Trace to Companies**: Identifies companies through user profiles and organization memberships
3. **Gather Intelligence**: Uses ScrapeGraphAI to scrape additional company information
4. **Evaluate & Rank**: Scores companies based on multiple criteria:
   - Technology relevance (AI, ML, data analytics, scraping)
   - Industry fit (e-commerce, SaaS, fintech)
   - Company size and growth indicators
   - Explicit data processing needs

## 🎯 Use Cases

- **Sales Intelligence**: Identify potential customers for AI/data infrastructure products
- **Market Research**: Understand which companies are interested in specific technologies
- **Partnership Discovery**: Find companies with complementary technology needs
- **Competitive Analysis**: See which companies are following competitor repositories

## 🛠️ Architecture

- **LangGraph**: Orchestrates the multi-step analysis workflow
- **OpenRouter**: Provides LLM capabilities for intelligent evaluation
- **ScrapeGraphAI**: Powers web scraping for company information
- **Streamlit**: Creates an intuitive user interface

## 📁 Project Structure

```
github-star-to-company-agent/
├── src/
│   ├── agent.py          # LangGraph workflow definition
│   ├── tools.py          # GitHub and scraping tools
│   ├── evaluator.py      # Company scoring logic
│   └── app.py            # Streamlit UI
├── tests/
│   └── test_agent.py     # Unit tests
├── docs/
│   └── usage.md          # Detailed usage guide
├── .env                  # API keys (create this)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 🔧 Configuration

### Environment Variables

- `GITHUB_TOKEN`: Personal access token for GitHub API
- `OPENROUTER_API_KEY`: API key for OpenRouter LLM service
- `OPENROUTER_API_BASE`: OpenRouter API endpoint (default: https://openrouter.ai/api/v1)
- `SGAI_API_KEY`: API key for ScrapeGraphAI service

### Advanced Settings

Customize analysis parameters through the Streamlit UI:
- Maximum number of companies to display
- Minimum score threshold for filtering
- Analysis depth and timeout settings

## ⚖️ Ethical Considerations

- **Respect Rate Limits**: The agent implements automatic rate limiting
- **Privacy**: Only analyzes publicly available information
- **Terms of Service**: Ensure compliance with all platform ToS
- **Responsible Use**: Designed for legitimate business intelligence only

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for agent orchestration
- Powered by [ScrapeGraphAI](https://scrapegraphai.com) for web scraping
- UI created with [Streamlit](https://streamlit.io)
- LLM capabilities via [OpenRouter](https://openrouter.ai)

## 📞 Support

For issues, questions, or suggestions:
1. Check the [usage guide](docs/usage.md)
2. Open an issue on GitHub
3. Review existing issues for solutions

---

Made with ❤️ for the data intelligence community