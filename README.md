# Data Visualization App

Interactive tool for creating hierarchical visualizations from CSV data. Built with Streamlit and Plotly.

[LINK TO CHART CREATOR](https://chartcreator.streamlit.app/)

## Features

- Multiple chart types (Sunburst, Treemap, Icicle)
- CSV data upload and preprocessing
- Customizable color schemes
- Interactive configuration
- Data validation
- Download options (HTML, JSON)

## Installation

```bash
git clone 
cd visualization-app
pip install -r requirements.txt
```

## Usage

1. Run the app:
```bash
streamlit run src/visualization.py
```

2. Upload CSV file
3. Select hierarchy columns
4. Configure chart settings
5. Generate visualization

## Requirements

- Python 3.8+
- streamlit
- pandas
- plotly
- numpy

## Example Data

Tested with NBA statistics dataset, visualizing:
- Free throw performance
- Seasonal patterns
- Game statistics

## License

MIT

## Contributing

1. Fork repository
2. Create feature branch
3. Submit pull request
