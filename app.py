import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from io import StringIO
import base64

# Set page configuration
st.set_page_config(
    page_title="Product Content Analysis Matrix",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .score-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 500;
        color: white;
        margin: 0 auto;
    }
    .score-5 { background-color: #4c7a00; }
    .score-4 { background-color: #76a12e; }
    .score-3 { background-color: #9bc357; }
    .score-2 { background-color: #c2dc8d; }
    .score-1 { background-color: #f3f4f6; color: #6b7280; }
    .score-null { background-color: #e5e7eb; }
    
    .st-emotion-cache-16idsys p {
        font-size: 14px;
        margin-bottom: 0.5rem;
    }
    
    .category-header {
        background-color: #f3f4f6;
        padding: 10px;
        font-weight: bold;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .metric-row {
        display: flex;
        align-items: center;
        padding: 10px;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .competitor-header {
        text-align: center;
        padding: 10px;
        font-weight: bold;
        border-bottom: 2px solid #76a12e;
    }
    
    .competitor-score {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0;
    }
    
    .legend-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        padding: 10px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 5px;
        white-space: nowrap;
    }
    
    .legend-circle {
        width: 25px;
        height: 25px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 500;
        color: white;
    }
    
    .score-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        border: 1px solid #e5e7eb;
    }
    
    .score-table th, .score-table td {
        text-align: center;
        padding: 10px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .element-column {
        text-align: left;
        width: 300px;
        padding-left: 10px !important;
    }
    
    .matrix-container {
        overflow-x: auto;
    }
    
    /* Fix for competitor headers alignment */
    .competitor-column {
        min-width: 140px;
        width: 140px;
        max-width: 140px;
    }
    
    .compact-description {
        font-size: 0.8rem;
        color: #6b7280;
        display: inline;
        margin-left: 5px;
    }
    
    .competitor-name {
        font-weight: bold;
        text-align: center;
    }
    
    .metric-name {
        font-weight: bold;
        display: inline;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing data
if 'competitors' not in st.session_state:
    st.session_state.competitors = [
        {"name": "SiteOne.com", "score": 44},
        {"name": "Grainger", "score": 50},
        {"name": "Home Depot", "score": 77},
        {"name": "PlantingTree.com", "score": 62},
        {"name": "Fastenal", "score": 34},
        {"name": "Heritage", "score": 33}
    ]

if 'categories' not in st.session_state:
    st.session_state.categories = [
        {
            "name": "Site Navigation",
            "metrics": [
                {
                    "name": "Taxonomy Menu: Mega Menu",
                    "description": "Expandable navigation showing full product hierarchy and category breadth",
                    "scores": [5, 5, 5, 3, 3, 3]
                },
                {
                    "name": "Faceted Navigation",
                    "description": "Filter system using product attributes for refinement",
                    "scores": [3, 5, 5, 5, 3, 5]
                }
            ]
        },
        {
            "name": "Product List Page",
            "metrics": [
                {
                    "name": "Product Descriptions",
                    "description": "Structured naming with brand, model, and key specifications",
                    "scores": [3, 3, 5, 3, 2, 3]
                },
                {
                    "name": "Thumbnail Images",
                    "description": "Quality and consistency of list view images",
                    "scores": [3, 3, 5, 5, 2, 3]
                }
            ]
        },
        {
            "name": "Product Detail Images",
            "metrics": [
                {
                    "name": "Primary Image",
                    "description": "Presence and quality of main product image",
                    "scores": [5, 5, 5, 5, 3, 3]
                },
                {
                    "name": "Multiple Images",
                    "description": "Additional product views/angles available",
                    "scores": [2, 3, 5, 5, 2, 2]
                },
                {
                    "name": "Rich Content",
                    "description": "Interactive rotating product view",
                    "scores": [1, 1, 1, 1, 1, 1]
                },
                {
                    "name": "Lifestyle Images",
                    "description": "Photos showing product being used/installed",
                    "scores": [1, 2, 5, 5, 1, 1]
                }
            ]
        },
        {
            "name": "Product Media",
            "metrics": [
                {
                    "name": "Product Videos",
                    "description": "Video content showing product features/use",
                    "scores": [1, 1, 1, 1, 1, 1]
                },
                {
                    "name": "Product PDF Assets",
                    "description": "Spec sheets, manuals, installation guides",
                    "scores": [3, 2, 5, 3, 2, 1]
                }
            ]
        },
        {
            "name": "Product Content",
            "metrics": [
                {
                    "name": "Long Description/Feature Bullets",
                    "description": "Marketing descriptions and key product features",
                    "scores": [3, 2, 5, 5, 3, 2]
                },
                {
                    "name": "Specifications",
                    "description": "Technical product attributes and details",
                    "scores": [3, 5, 5, 5, 3, 2]
                },
                {
                    "name": "How to?",
                    "description": "Where/how to use the product",
                    "scores": [3, 2, 5, 5, 2, 1]
                },
                {
                    "name": "Product Recommendations/Substitutions",
                    "description": "Compatible products, replacement parts",
                    "scores": [3, 3, 5, 3, 2, 2]
                },
                {
                    "name": "Customer Reviews & Q&A",
                    "description": "Customer feedback and questions with answers",
                    "scores": [2, 3, 5, 3, 1, 1]
                },
                {
                    "name": "Projects/Inspirational/Collections",
                    "description": "Project ideas and inspirational content",
                    "scores": [1, 2, 5, 3, 1, 1]
                },
                {
                    "name": "Base/Variant – SUPER SKU",
                    "description": "Product variants and super SKU structure",
                    "scores": [2, 3, 5, 2, 2, 1]
                }
            ]
        }
    ]

# Function to calculate total score for a competitor
def calculate_total_score(competitor_index):
    total = 0
    count = 0
    
    for category in st.session_state.categories:
        for metric in category["metrics"]:
            if competitor_index < len(metric["scores"]) and metric["scores"][competitor_index] is not None:
                total += metric["scores"][competitor_index]
                count += 1
    
    return total if count > 0 else 0

# Function to update all competitor scores
def update_competitor_scores():
    for i, competitor in enumerate(st.session_state.competitors):
        competitor["score"] = calculate_total_score(i)

# Download functions
def get_download_link(data, filename, text):
    json_str = json.dumps(data, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Main app layout
def main():
    st.title("Product Content Analysis Matrix")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Dashboard", "Data Editor"])
    
    with tab1:
        # Condensed Legend in a single row
        st.markdown("""
        <div class="legend-container">
            <div class="legend-item">
                <div class="legend-circle score-5">5</div>
                <span>World Class (5)</span>
            </div>
            <div class="legend-item">
                <div class="legend-circle score-4">4</div>
                <span>Very Good (4)</span>
            </div>
            <div class="legend-item">
                <div class="legend-circle score-3">3</div>
                <span>Good (3)</span>
            </div>
            <div class="legend-item">
                <div class="legend-circle score-2">2</div>
                <span>Basic (2)</span>
            </div>
            <div class="legend-item">
                <div class="legend-circle score-1">1</div>
                <span>None (1)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Convert old scores (0,2,3,4) to new scale (1,2,3,4,5)
        if "score_updated" not in st.session_state:
            for cat in st.session_state.categories:
                for met in cat["metrics"]:
                    for i, score in enumerate(met["scores"]):
                        if score == 0:
                            met["scores"][i] = 1
                        elif score == 4:
                            met["scores"][i] = 5
            st.session_state.score_updated = True
        
        # Update scores
        update_competitor_scores()
        
        # Display competitors and their total scores without subheader - directly in the same table
        # Create a table for competitor scores with scores above names
        st.markdown("""
        <h3>Competitor Scores</h3>
        <div class="matrix-container">
        <table class='score-table'>
            <tr>
        """, unsafe_allow_html=True)
        
        # Create competitor score table directly in HTML
        score_html = ""
        for comp in st.session_state.competitors:
            score_html += f"<td class='competitor-column'><div class='competitor-score'>{comp['score']}</div></td>"
        
        st.markdown(score_html, unsafe_allow_html=True)
        st.markdown("</tr><tr>", unsafe_allow_html=True)
        
        name_html = ""
        for comp in st.session_state.competitors:
            name_html += f"<td class='competitor-column'><div class='competitor-name'>{comp['name']}</div></td>"
        
        st.markdown(name_html, unsafe_allow_html=True)
        st.markdown("</tr></table></div>", unsafe_allow_html=True)
        
        # Detailed table view
        st.markdown("<h3>Detailed Matrix View</h3>", unsafe_allow_html=True)
        
        for category in st.session_state.categories:
            st.markdown(f"<div class='category-header'>{category['name']}</div>", unsafe_allow_html=True)
            
            # Create a table for metrics and scores
            table_html = "<div class='matrix-container'><table class='score-table'><tr>"
            table_html += "<th class='element-column'>Element / Metric</th>"
            
            # Add competitor names as headers
            for comp in st.session_state.competitors:
                table_html += f"<th class='competitor-column'>{comp['name']}</th>"
            
            table_html += "</tr>"
            
            # Add metric rows
            for metric in category["metrics"]:
                table_html += "<tr>"
                # Create a very compact Element/Metric section
                table_html += f"<td class='element-column'><div class='metric-name'>{metric['name']}</div><div class='compact-description'>{metric['description']}</div></td>"
                
                # Add scores
                for i, score in enumerate(metric["scores"]):
                    if i < len(st.session_state.competitors):
                        table_html += f"<td class='competitor-column'><div class='score-circle score-{score}'>{score}</div></td>"
                table_html += "</tr>"
                
            table_html += "</table></div>"
            st.markdown(table_html, unsafe_allow_html=True)
    
    with tab2:
        st.header("Manage Competitors")
        
        # Edit existing competitors
        for i, competitor in enumerate(st.session_state.competitors):
            cols = st.columns([3, 1])
            with cols[0]:
                new_name = st.text_input(f"Competitor {i+1}", competitor["name"], key=f"comp_{i}")
                st.session_state.competitors[i]["name"] = new_name
            with cols[1]:
                if st.button("Remove", key=f"remove_{i}") and len(st.session_state.competitors) > 1:
                    st.session_state.competitors.pop(i)
                    # Remove scores for this competitor
                    for category in st.session_state.categories:
                        for metric in category["metrics"]:
                            if i < len(metric["scores"]):
                                metric["scores"].pop(i)
                    st.rerun()
# Add new competitor
        st.subheader("Add New Competitor")
        new_comp_cols = st.columns([3, 1])
        with new_comp_cols[0]:
            new_competitor = st.text_input("New competitor name")
        with new_comp_cols[1]:
            if st.button("Add Competitor") and new_competitor.strip():
                if len(st.session_state.competitors) < 10:
                    st.session_state.competitors.append({"name": new_competitor, "score": 0})
                    # Add empty score slot for each metric
                    for category in st.session_state.categories:
                        for metric in category["metrics"]:
                            metric["scores"].append(1)  # Default to 1 (None) instead of 0
                    st.rerun()
                else:
                    st.error("Maximum of 10 competitors reached")
        
        # Edit scores
        st.header("Edit Scores")
        
        for category_idx, category in enumerate(st.session_state.categories):
            st.subheader(category["name"])
            
            for metric_idx, metric in enumerate(category["metrics"]):
                st.markdown(f"**{metric['name']}**")
                st.markdown(f"<small>{metric['description']}</small>", unsafe_allow_html=True)
                
                score_cols = st.columns(len(st.session_state.competitors))
                for comp_idx, competitor in enumerate(st.session_state.competitors):
                    with score_cols[comp_idx]:
                        st.markdown(f"**{competitor['name']}**")
                        new_score = st.selectbox(
                            "",
                            options=[1, 2, 3, 4, 5],
                            format_func=lambda x: f"{x} - {'World Class' if x==5 else 'Very Good' if x==4 else 'Good' if x==3 else 'Basic' if x==2 else 'None'}",
                            index=[1, 2, 3, 4, 5].index(metric["scores"][comp_idx]) if comp_idx < len(metric["scores"]) and metric["scores"][comp_idx] in [1, 2, 3, 4, 5] else 0,
                            key=f"score_{category_idx}_{metric_idx}_{comp_idx}"
                        )
                                                
                        # Update scores
                        if comp_idx < len(metric["scores"]) and new_score != metric["scores"][comp_idx]:
                            metric["scores"][comp_idx] = new_score
        
        # Import/Export functionality
        st.header("Import/Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Reset to Default"):
                if st.session_state.get('confirm_reset', False):
                    # Reset to default data
                    st.session_state.competitors = [
                        {"name": "SiteOne.com", "score": 44},
                        {"name": "Grainger", "score": 50},
                        {"name": "Home Depot", "score": 77},
                        {"name": "PlantingTree.com", "score": 62},
                        {"name": "Fastenal", "score": 34},
                        {"name": "Heritage", "score": 33}
                    ]
                    
                    # Reset categories with new scoring (1-5 instead of 0-4)
                    st.session_state.categories = [
                        {
                            "name": "Site Navigation",
                            "metrics": [
                                {
                                    "name": "Taxonomy Menu: Mega Menu",
                                    "description": "Expandable navigation showing full product hierarchy and category breadth",
                                    "scores": [5, 5, 5, 3, 3, 3]
                                },
                                {
                                    "name": "Faceted Navigation",
                                    "description": "Filter system using product attributes for refinement",
                                    "scores": [3, 5, 5, 5, 3, 5]
                                }
                            ]
                        },
                        {
                            "name": "Product List Page",
                            "metrics": [
                                {
                                    "name": "Product Descriptions",
                                    "description": "Structured naming with brand, model, and key specifications",
                                    "scores": [3, 3, 5, 3, 2, 3]
                                },
                                {
                                    "name": "Thumbnail Images",
                                    "description": "Quality and consistency of list view images",
                                    "scores": [3, 3, 5, 5, 2, 3]
                                }
                            ]
                        },
                        {
                            "name": "Product Detail Images",
                            "metrics": [
                                {
                                    "name": "Primary Image",
                                    "description": "Presence and quality of main product image",
                                    "scores": [5, 5, 5, 5, 3, 3]
                                },
                                {
                                    "name": "Multiple Images",
                                    "description": "Additional product views/angles available",
                                    "scores": [2, 3, 5, 5, 2, 2]
                                },
                                {
                                    "name": "Rich Content",
                                    "description": "Interactive rotating product view",
                                    "scores": [1, 1, 1, 1, 1, 1]
                                },
                                {
                                    "name": "Lifestyle Images",
                                    "description": "Photos showing product being used/installed",
                                    "scores": [1, 2, 5, 5, 1, 1]
                                }
                            ]
                        },
                        {
                            "name": "Product Media",
                            "metrics": [
                                {
                                    "name": "Product Videos",
                                    "description": "Video content showing product features/use",
                                    "scores": [1, 1, 1, 1, 1, 1]
                                },
                                {
                                    "name": "Product PDF Assets",
                                    "description": "Spec sheets, manuals, installation guides",
                                    "scores": [3, 2, 5, 3, 2, 1]
                                }
                            ]
                        },
                        {
                            "name": "Product Content",
                            "metrics": [
                                {
                                    "name": "Long Description/Feature Bullets",
                                    "description": "Marketing descriptions and key product features",
                                    "scores": [3, 2, 5, 5, 3, 2]
                                },
                                {
                                    "name": "Specifications",
                                    "description": "Technical product attributes and details",
                                    "scores": [3, 5, 5, 5, 3, 2]
                                },
                                {
                                    "name": "How to?",
                                    "description": "Where/how to use the product",
                                    "scores": [3, 2, 5, 5, 2, 1]
                                },
                                {
                                    "name": "Product Recommendations/Substitutions",
                                    "description": "Compatible products, replacement parts",
                                    "scores": [3, 3, 5, 3, 2, 2]
                                },
                                {
                                    "name": "Customer Reviews & Q&A",
                                    "description": "Customer feedback and questions with answers",
                                    "scores": [2, 3, 5, 3, 1, 1]
                                },
                                {
                                    "name": "Projects/Inspirational/Collections",
                                    "description": "Project ideas and inspirational content",
                                    "scores": [1, 2, 5, 3, 1, 1]
                                },
                                {
                                    "name": "Base/Variant – SUPER SKU",
                                    "description": "Product variants and super SKU structure",
                                    "scores": [2, 3, 5, 2, 2, 1]
                                }
                            ]
                        }
                    ]
                    
                    st.session_state['confirm_reset'] = False
                    st.rerun()
                else:
                    st.session_state['confirm_reset'] = True
                    st.warning("Click again to confirm reset. This will erase all customizations.")
        
        with col2:
            export_data = {
                "competitors": st.session_state.competitors,
                "categories": st.session_state.categories
            }
            st.markdown(get_download_link(export_data, "matrix-data.json", "Export Data"), unsafe_allow_html=True)
        
        with col3:
            uploaded_file = st.file_uploader("Import Data", type=["json"])
            if uploaded_file:
                try:
                    content = uploaded_file.getvalue().decode("utf-8")
                    data = json.loads(content)
                    
                    if "competitors" in data and "categories" in data:
                        st.session_state.competitors = data["competitors"]
                        st.session_state.categories = data["categories"]
                        st.success("Data imported successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid data format")
                except Exception as e:
                    st.error(f"Error parsing file: {str(e)}")
                    
        # Visualization options
        st.header("Visualization Options")
        if st.button("Generate Radar Chart"):
            # Create radar chart of competitor scores by category
            categories_df = []
            
            for category in st.session_state.categories:
                category_name = category["name"]
                for comp_idx, competitor in enumerate(st.session_state.competitors):
                    comp_name = competitor["name"]
                    
                    # Calculate average score for this category
                    cat_scores = [m["scores"][comp_idx] for m in category["metrics"]]
                    avg_score = sum(cat_scores) / len(cat_scores) if cat_scores else 0
                    
                    categories_df.append({
                        "Category": category_name,
                        "Competitor": comp_name,
                        "Score": round(avg_score, 1)
                    })
            
            cat_df = pd.DataFrame(categories_df)
            
            # Create radar chart using Plotly
            fig = go.Figure()
            
            categories = cat_df["Category"].unique()
            
            for competitor in cat_df["Competitor"].unique():
                comp_data = cat_df[cat_df["Competitor"] == competitor]
                
                fig.add_trace(go.Scatterpolar(
                    r=comp_data["Score"].values,
                    theta=comp_data["Category"].values,
                    fill='toself',
                    name=competitor
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                title="Category Performance by Competitor",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
if __name__ == "__main__":
    main()
