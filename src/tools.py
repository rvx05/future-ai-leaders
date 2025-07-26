"""
Tools Module - Define a set of tools for the agent to use.
Part of the Agentic AI Architecture for the hackathon.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

def search_web(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a web search using DuckDuckGo and returns the top results.
    
    Args:
        query: The search query.
        num_results: The maximum number of results to return.
        
    Returns:
        A list of dictionaries, where each dictionary contains the 'title', 'link', and 'snippet' of a search result.
    """
    search_url = "https://html.duckduckgo.com/html/"
    params = {"q": query}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        response = requests.post(search_url, data=params, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.find_all('div', class_='result'):
            title_tag = result.find('a', class_='result__a')
            snippet_tag = result.find('a', class_='result__snippet')
            
            if title_tag and snippet_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag['href']
                snippet = snippet_tag.get_text(strip=True)
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
                
                if len(results) >= num_results:
                    break
                    
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Error during web search: {e}")
        return [{"error": f"Failed to perform web search: {e}"}]
