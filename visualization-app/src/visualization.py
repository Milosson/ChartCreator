import streamlit as st
import pandas as pd
import plotly.express as px
import io
from typing import Optional, Dict, Any
import traceback

def validate_data(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validate uploaded data with detailed error messages
    Returns: (is_valid, error_message)
    """
    if df is None:
        return False, "No data provided"
    if df.empty:
        return False, "The uploaded file is empty"
    if len(df.columns) < 2:
        return False, "File must contain at least two columns"
    if df.columns.duplicated().any():
        return False, "File contains duplicate column names"
    return True, ""

def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """Process and clean the data safely"""
    try:
        # Remove rows and columns that are completely empty
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        
        # Handle any infinite values
        df = df.replace([float('inf'), float('-inf')], pd.NA)
        
        # Convert numeric strings to numbers where possible
        for col in df.columns:
            try:
                if df[col].dtype == 'object':
                    df[col] = pd.to_numeric(df[col], errors='ignore')
            except Exception:
                continue
                
        return df
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        return df

class DataVisualizer:
    def __init__(self):
        st.set_page_config(
            page_title="Hierarchical Data Visualizer",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        self.initialize_session_state()

    def initialize_session_state(self):
        """Initialize all session state variables"""
        default_settings = {
            'chart_type': 'Sunburst',
            'color_scheme': 'Default',
            'width': 800,
            'height': 800,
            'data': None,
            'error': None
        }
        
        for key, value in default_settings.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def create_chart(self, df: pd.DataFrame, settings: Dict[str, Any]):
        """Create visualization with error handling"""
        try:
            if not settings.get('path_columns'):
                raise ValueError("No hierarchy columns selected")

            chart_types = {
                'Sunburst': px.sunburst,
                'Treemap': px.treemap,
                'Icicle': px.icicle
            }
            
            chart_fn = chart_types.get(settings['chart_type'])
            if not chart_fn:
                raise ValueError(f"Invalid chart type: {settings['chart_type']}")

            # Validate path columns exist in dataframe
            missing_cols = [col for col in settings['path_columns'] if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Columns not found in data: {', '.join(missing_cols)}")

            # Build chart parameters
            chart_params = {
                'data_frame': df,
                'path': settings['path_columns'],
                'width': settings['width'],
                'height': settings['height']
            }

            # Add optional parameters if they're valid
            if settings.get('values_column') and settings['values_column'] != 'None':
                if settings['values_column'] not in df.columns:
                    raise ValueError(f"Values column '{settings['values_column']}' not found in data")
                chart_params['values'] = settings['values_column']

            if settings.get('color_column') and settings['color_column'] != 'None':
                if settings['color_column'] not in df.columns:
                    raise ValueError(f"Color column '{settings['color_column']}' not found in data")
                chart_params['color'] = settings['color_column']

            if settings.get('color_scheme') and settings['color_scheme'] != 'Default':
                chart_params['color_continuous_scale'] = settings['color_scheme']

            fig = chart_fn(**chart_params)
            
            # Update layout for better visualization
            fig.update_layout(
                margin=dict(t=30, l=10, r=10, b=10),
                title_x=0.5,
                title_y=0.95
            )
            
            return fig

        except Exception as e:
            st.error(f"Error creating visualization: {str(e)}")
            if st.checkbox("Show detailed error", key="show_error"):
                st.code(traceback.format_exc())
            return None

    def run(self):
        """Main application logic with error handling"""
        try:
            st.title("Hierarchical Data Visualizer")
            st.markdown("Upload a CSV file to create interactive hierarchical visualizations")

            # Sidebar configuration
            with st.sidebar:
                st.header("Chart Settings")
                settings = {
                    'chart_type': st.selectbox(
                        "Chart Type",
                        ['Sunburst', 'Treemap', 'Icicle'],
                        key='chart_select',
                        help="Select the type of visualization"
                    ),
                    'color_scheme': st.selectbox(
                        "Color Scheme",
                        ['Default', 'Viridis', 'Plasma', 'Blues', 'Reds'],
                        key='color_select',
                        help="Choose color scheme for the visualization"
                    )
                }
                
                st.subheader("Dimensions")
                settings['width'] = st.slider(
                    "Width", 
                    min_value=400, 
                    max_value=1200, 
                    value=800, 
                    key='width',
                    help="Adjust the width of the visualization"
                )
                settings['height'] = st.slider(
                    "Height", 
                    min_value=400, 
                    max_value=1200, 
                    value=800, 
                    key='height',
                    help="Adjust the height of the visualization"
                )

            # File upload with error handling
            uploaded_file = st.file_uploader(
                "Upload CSV file", 
                type=['csv'], 
                key='uploader',
                help="Upload a CSV file with hierarchical data"
            )

            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    is_valid, error_msg = validate_data(df)
                    
                    if not is_valid:
                        st.error(error_msg)
                        return

                    df = process_data(df)
                    
                    # Data preview with row count
                    st.write(f"### Data Preview ({len(df)} rows)")
                    st.dataframe(df.head(), use_container_width=True)

                    # Column selection with better layout
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        path_cols = st.multiselect(
                            "Hierarchy Columns (required)",
                            options=list(df.columns),
                            key='path',
                            help="Select columns for the hierarchy (order matters)"
                        )

                    with col2:
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        values_col = st.selectbox(
                            "Values Column",
                            options=['None'] + list(numeric_cols),
                            key='values',
                            help="Optional: Select a numeric column for sizing"
                        )

                    with col3:
                        color_col = st.selectbox(
                            "Color Column",
                            options=['None'] + list(df.columns),
                            key='color',
                            help="Optional: Select a column for coloring"
                        )

                    # Generate visualization
                    if st.button("Generate Visualization", key='generate', use_container_width=True):
                        if not path_cols:
                            st.error("Please select at least one hierarchy column")
                            return

                        chart_settings = {
                            **settings,
                            'path_columns': path_cols,
                            'values_column': values_col,
                            'color_column': color_col
                        }

                        with st.spinner("Creating visualization..."):
                            fig = self.create_chart(df, chart_settings)
                        
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Download options
                            col1, col2 = st.columns(2)
                            with col1:
                                buffer = io.StringIO()
                                fig.write_html(buffer)
                                st.download_button(
                                    "Download as HTML",
                                    buffer.getvalue(),
                                    f"visualization.html",
                                    "text/html",
                                    key='download_html',
                                    use_container_width=True
                                )
                            
                            with col2:
                                # Add JSON download option
                                json_str = df.to_json(orient='records')
                                st.download_button(
                                    "Download Data as JSON",
                                    json_str,
                                    f"data.json",
                                    "application/json",
                                    key='download_json',
                                    use_container_width=True
                                )

                except Exception as e:
                    st.error(f"Error processing file: {str(e)}")
                    if st.checkbox("Show detailed error", key="show_file_error"):
                        st.code(traceback.format_exc())

        except Exception as e:
            st.error("An unexpected error occurred. Please try again or contact support.")
            if st.checkbox("Show technical details", key="show_tech_error"):
                st.code(traceback.format_exc())

if __name__ == "__main__":
    DataVisualizer().run()