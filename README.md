# Solana Due Diligence Bot v2

A comprehensive due diligence analysis system for Solana meme coins and tokens. This bot automatically analyzes new tokens for security, tokenomics, market data, community engagement, and developer activity to identify potential investment opportunities.

## Features

### 🔍 **Comprehensive Analysis**

- **Tokenomics**: Supply analysis, holder distribution, token metadata
- **Market Data**: Liquidity analysis, trading pairs, price information
- **Security**: Authority checks, honeypot detection, LP analysis
- **Community**: Social media engagement analysis (X/Twitter)
- **Developer**: Creator wallet analysis, GitHub repository discovery
- **Metrics**: Holder concentration analysis, risk assessment

### 🚀 **Real-time Monitoring**

- Live token streaming via Bitquery
- Automatic analysis of new tokens
- Buy signal evaluation with configurable thresholds
- Telegram notifications for promising tokens

### 📊 **Detailed Reporting**

- JSON and Markdown report generation
- Comprehensive risk assessment
- Historical analysis capabilities
- Customizable output formats

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd due_diligence_project_v2

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file with your API keys:

```bash
# Required API Keys
SOLSCAN_API_KEY=your_solscan_api_key
GITHUB_TOKEN=your_github_token
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Optional API Keys
BITQUERY_API_KEY=your_bitquery_api_key
MORALIS_API_KEY=your_moralis_api_key
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
```

### 3. Basic Usage

#### Analyze a Single Token

```bash
python main.py run <MINT_ADDRESS>
```

#### Start Live Streaming

```bash
python stream_control.py start
```

#### Check Stream Status

```bash
python stream_control.py status
```

#### Stop Streaming

```bash
python stream_control.py stop
```

## Configuration

The system uses `config.yaml` for configuration. Key settings include:

- **Solana RPC**: Configure your Solana RPC endpoint
- **API Keys**: Set up external service integrations
- **Thresholds**: Customize buy signal criteria
- **Output**: Configure report generation settings

## Buy Signal Criteria

The bot evaluates tokens based on:

- ✅ **Mint Authority Revoked**: Token cannot mint new supply
- ✅ **Freeze Authority Revoked**: Token cannot freeze accounts
- ✅ **Minimum Liquidity**: Configurable USD liquidity threshold
- ✅ **Holder Distribution**: Top-10 holder concentration limits
- ✅ **Security Checks**: Additional risk assessments

## Project Structure

```text
due_diligence_project_v2/
├── main.py                          # Main entry point
├── stream_control.py                # Stream management wrapper
├── config.yaml                      # Configuration file
├── requirements.txt                 # Python dependencies
├── solana_due_diligence/           # Core analysis modules
│   ├── config.py                   # Configuration management
│   ├── providers/                  # External API clients
│   │   ├── solana_rpc.py          # Solana RPC client
│   │   ├── solscan.py             # Solscan API client
│   │   ├── github_api.py          # GitHub API client
│   │   └── moralis.py             # Moralis API client
│   ├── analyzers/                  # Analysis modules
│   │   ├── tokenomics/            # Token supply & distribution
│   │   ├── market/                # Market data & liquidity
│   │   ├── security/              # Security & risk analysis
│   │   ├── community/             # Social media analysis
│   │   ├── developer/             # Developer activity
│   │   ├── github/                # GitHub repository analysis
│   │   └── metrics/               # Holder concentration metrics
│   ├── signals/                   # Buy signal evaluation
│   ├── notify/                    # Notification system
│   ├── reporting/                 # Report generation
│   ├── streaming/                 # Live token monitoring
│   └── ingestion/                 # Data ingestion
├── tests/                         # Test suite
└── reports/                       # Generated reports (created automatically)
```

## API Integrations

### Required Services

- **Solscan**: Token metadata and holder information
- **GitHub**: Repository discovery and analysis
- **Telegram**: Buy signal notifications

### Optional Services

- **Bitquery**: Live token streaming
- **Moralis**: Advanced holder analysis
- **Custom RPC**: Enhanced Solana data access

## Development

### Running Tests

```bash
pytest tests/
```

### Adding New Analyzers

1. Create analyzer class in appropriate module
2. Implement `analyze()` method
3. Add to main analysis pipeline in `main.py`
4. Update report generation in `reporting/report.py`

### Customizing Buy Signals

Modify `signals/engine.py` to adjust evaluation criteria and thresholds.

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Ensure you have valid API keys and sufficient rate limits
2. **RPC Errors**: Check your Solana RPC endpoint configuration
3. **Missing Dependencies**: Run `pip install -r requirements.txt`
4. **Permission Errors**: Ensure write permissions for the reports directory

### Logs and Debugging

The system uses Rich for colored console output. Check console messages for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is for educational and research purposes. Please ensure compliance with all applicable terms of service for integrated APIs.

## Disclaimer

This tool is for educational purposes only. Cryptocurrency investments carry significant risk. Always conduct your own research and consider consulting with financial advisors before making investment decisions.
