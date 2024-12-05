import streamlit as st
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
from scrapegraph_py import SyncClient
import json

# Define Pydantic models for GitHub trending developers
class Developer(BaseModel):
    username: str = Field(description="Developer's GitHub username")
    full_name: Optional[str] = Field(description="Developer's full name")
    popular_repo: Optional[str] = Field(description="Name of developer's popular repository")
    repo_description: Optional[str] = Field(description="Description of the popular repository")
    company: Optional[str] = Field(description="Company the developer works for")

class TrendingDevelopers(BaseModel):
    developers: List[Developer] = Field(description="List of trending developers from GitHub")

class Repository(BaseModel):
    name: str = Field(description="Repository name")
    description: Optional[str] = Field(description="Repository description")
    stars: int = Field(description="Number of stars")
    language: Optional[str] = Field(description="Primary programming language")

class TrendingRepositories(BaseModel):
    repositories: List[Repository] = Field(description="List of trending repositories from GitHub")

def fetch_trending_developers(api_key):
    # Initialize the client
    sgai_client = SyncClient(api_key=api_key)
    
    try:
        # SmartScraper request with output schema
        response = sgai_client.smartscraper(
            website_url="https://github.com/trending/developers",
            user_prompt="Extract information about trending developers including their username, full name, popular repository, repository description, and company. Parse the data from the articles with class 'Box-row'.",
            output_schema=TrendingDevelopers,
        )
        
        sgai_client.close()
        print(response)
        return TrendingDevelopers(**response['result'])
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        if 'sgai_client' in locals():
            sgai_client.close()
        return None

def fetch_github_topics(api_key):
    sgai_client = SyncClient(api_key=api_key)
    try:
        response = sgai_client.smartscraper(
            website_url="https://github.com/topics",
            user_prompt="Extract featured topics including name and description",
        )
        sgai_client.close()
        return response['result']
    except Exception as e:
        st.error(f"Error fetching topics: {str(e)}")
        if 'sgai_client' in locals():
            sgai_client.close()
        return None

def fetch_github_explore(api_key):
    sgai_client = SyncClient(api_key=api_key)
    try:
        response = sgai_client.smartscraper(
            website_url="https://github.com/explore",
            user_prompt="Extract trending repositories including name, description, stars, and programming language",
            output_schema=TrendingRepositories,
        )
        print(response)
        sgai_client.close()
        return TrendingRepositories(**response['result'])
    except Exception as e:
        st.error(f"Error fetching explore data: {str(e)}")
        if 'sgai_client' in locals():
            sgai_client.close()
        return None

def fetch_github_collections(api_key):
    sgai_client = SyncClient(api_key=api_key)
    try:
        response = sgai_client.smartscraper(
            website_url="https://github.com/collections",
            user_prompt="Extract collections including title and description",
        )
        sgai_client.close()
        return response['result']
    except Exception as e:
        st.error(f"Error fetching collections: {str(e)}")
        if 'sgai_client' in locals():
            sgai_client.close()
        return None

def main():
    st.set_page_config(
        page_title="GitHub Insights",
        page_icon="👨‍💻",
        layout="wide"
    )
    
    st.title("🌟 GitHub Insights")
    st.markdown("---")
      # API Key input
    api_key = st.sidebar.text_input("Enter Scrapegraph API Key", type="password")
     
    # Add ScrapeGraphAI logo and reference in sidebar
    st.sidebar.image("assets/scrapegraphai_logo.png", width=100, use_column_width=True)
    st.sidebar.markdown("<div style='text-align: center'><a href='https://scrapegraphai.com/'>Powered by ScrapeGraphAI</a></div>", unsafe_allow_html=True)
 
    if not api_key:
        st.warning("Please enter your Scrapegraph API key in the sidebar to continue.")
        return

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Trending Developers", 
        "Trending Repos", 
        "Topics", 
        "Collections"
    ])

    # Tab 1: Trending Developers (existing functionality)
    with tab1:
        if st.button("Refresh Developers Data"):
            st.session_state.trending_data = fetch_trending_developers(api_key)
        
        if 'trending_data' not in st.session_state:
            st.session_state.trending_data = fetch_trending_developers(api_key)
        
        if st.session_state.trending_data:
            # Convert to DataFrame for better display
            developers_data = []
            for dev in st.session_state.trending_data.developers:
                developers_data.append({
                    "Username": dev.username,
                    "Full Name": dev.full_name or "N/A",
                    "Popular Repository": dev.popular_repo or "N/A",
                    "Repository Description": dev.repo_description or "N/A",
                    "Company": dev.company or "N/A"
                })
            
            df = pd.DataFrame(developers_data)
            
            # Display data
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
            
            col1, col2 = st.columns(2)
            
            # CSV download button
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name="github_trending_developers.csv",
                    mime="text/csv"
                )
            
            # JSON download button
            with col2:
                # Convert the data to JSON format
                json_data = json.dumps(
                    {
                        "developers": [
                            {
                                "username": dev.username,
                                "full_name": dev.full_name,
                                "popular_repo": dev.popular_repo,
                                "repo_description": dev.repo_description,
                                "company": dev.company
                            } for dev in st.session_state.trending_data.developers
                        ]
                    },
                    indent=2
                )
                st.download_button(
                    label="Download as JSON",
                    data=json_data,
                    file_name="github_trending_developers.json",
                    mime="application/json"
                )
        else:
            st.warning("No data available. Please try refreshing.")

    # Tab 2: Explore (moved from tab3)
    with tab2:
        if st.button("Refresh Explore Data"):
            st.session_state.explore_data = fetch_github_explore(api_key)
        
        if 'explore_data' not in st.session_state:
            st.session_state.explore_data = fetch_github_explore(api_key)
        
        if st.session_state.explore_data:
            # Convert explore data to DataFrame
            repos_data = []
            for repo in st.session_state.explore_data.repositories:
                repos_data.append({
                    "Repository": repo.name,
                    "Description": repo.description or "N/A",
                    "Stars": repo.stars,
                    "Language": repo.language or "Unknown"
                })
            
            explore_df = pd.DataFrame(repos_data)
            
            # Display the DataFrame
            st.dataframe(
                explore_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Stars": st.column_config.NumberColumn(
                        "Stars",
                        help="Number of GitHub stars",
                        format="%d ⭐"
                    ),
                    "Language": st.column_config.TextColumn(
                        "Language",
                        help="Primary programming language"
                    )
                }
            )
            
            # Create pie chart of programming languages
            st.subheader("Programming Languages Distribution")
            
            # Count languages and handle repositories with no language
            language_counts = explore_df['Language'].value_counts()
            
            # Create pie chart using Streamlit
            fig = {
                "data": [{
                    "values": language_counts.values,
                    "labels": language_counts.index,
                    "type": "pie",
                    "hole": 0.4,  # Makes it a donut chart
                    "hoverinfo": "label+percent",
                    "textinfo": "value"
                }],
                "layout": {
                    "showlegend": True,
                    "width": 800,
                    "height": 500,
                    "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
                    "legend": {"orientation": "h", "y": -0.1}
                }
            }
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add download buttons for Explore data
            col1, col2 = st.columns(2)
            with col1:
                # CSV download
                csv = explore_df.to_csv(index=False)
                st.download_button(
                    label="Download Repositories as CSV",
                    data=csv,
                    file_name="github_trending_repos.csv",
                    mime="text/csv"
                )
            with col2:
                # JSON download
                json_data = json.dumps(
                    {
                        "repositories": [
                            {
                                "name": repo.name,
                                "description": repo.description,
                                "stars": repo.stars,
                                "language": repo.language
                            } for repo in st.session_state.explore_data.repositories
                        ]
                    },
                    indent=2
                )
                st.download_button(
                    label="Download Repositories as JSON",
                    data=json_data,
                    file_name="github_trending_repos.json",
                    mime="application/json"
                )
        else:
            st.warning("No explore data available. Please try refreshing.")

    # Tab 3: Topics (moved from tab2)
    with tab3:
        if st.button("Refresh Topics Data"):
            st.session_state.topics_data = fetch_github_topics(api_key)
        
        if 'topics_data' not in st.session_state:
            st.session_state.topics_data = fetch_github_topics(api_key)
        
        if st.session_state.topics_data:
            # Convert topics data to DataFrame
            if 'featured_topics' in st.session_state.topics_data:
                topics_df = pd.DataFrame(st.session_state.topics_data['featured_topics'])
                
                # Display the DataFrame
                st.dataframe(
                    topics_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "name": "Topic Name",
                        "description": "Description"
                    }
                )
                
                # Add download buttons for Topics data
                col1, col2 = st.columns(2)
                with col1:
                    # CSV download
                    csv = topics_df.to_csv(index=False)
                    st.download_button(
                        label="Download Topics as CSV",
                        data=csv,
                        file_name="github_topics.csv",
                        mime="text/csv"
                    )
                with col2:
                    # JSON download
                    st.download_button(
                        label="Download Topics as JSON",
                        data=json.dumps(st.session_state.topics_data, indent=2),
                        file_name="github_topics.json",
                        mime="application/json"
                    )
            else:
                st.error("Invalid topics data format received")
        else:
            st.warning("No topics data available. Please try refreshing.")

    # Tab 4: Collections
    with tab4:
        if st.button("Refresh Collections Data"):
            st.session_state.collections_data = fetch_github_collections(api_key)
        
        if 'collections_data' not in st.session_state:
            st.session_state.collections_data = fetch_github_collections(api_key)
        
        if st.session_state.collections_data:
            # Convert collections data to DataFrame
            if 'collections' in st.session_state.collections_data:
                collections_df = pd.DataFrame(st.session_state.collections_data['collections'])
                
                # Display the DataFrame
                st.dataframe(
                    collections_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "title": "Collection",
                        "description": st.column_config.TextColumn(
                            "Description",
                            width="large",
                            help="Collection description"
                        )
                    }
                )
                
                # Add download buttons for Collections data
                col1, col2 = st.columns(2)
                with col1:
                    # CSV download
                    csv = collections_df.to_csv(index=False)
                    st.download_button(
                        label="Download Collections as CSV",
                        data=csv,
                        file_name="github_collections.csv",
                        mime="text/csv"
                    )
                with col2:
                    # JSON download
                    st.download_button(
                        label="Download Collections as JSON",
                        data=json.dumps(st.session_state.collections_data, indent=2),
                        file_name="github_collections.json",
                        mime="application/json"
                    )
            else:
                st.error("Invalid collections data format received")
        else:
            st.warning("No collections data available. Please try refreshing.")

if __name__ == "__main__":
    main()
