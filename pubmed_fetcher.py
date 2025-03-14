import requests
import pandas as pd
from typing import List, Dict, Optional

# Declare your API key here
API_KEY = "3c893e45295c254a481e3f70371727dfca08"  

def fetch_papers(query: str) -> List[Dict[str, Optional[str]]]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "api_key": API_KEY,
        "retmax": 100  # Adjust the number of results as needed
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        raise Exception("Failed to fetch data from PubMed API")
    
    # Extract the PubMed IDs from the response
    pmids = response.json().get('esearchresult', {}).get('idlist', [])
    
    papers = []
    for pmid in pmids:
        paper_details = fetch_paper_details(pmid)
        papers.append(paper_details)
    
    return papers

def fetch_paper_details(pmid: str) -> Dict[str, Optional[str]]:
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "json",
        "api_key": API_KEY
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch details for PMID {pmid}")
    
    item = response.json().get('result', {}).get(pmid, {})
    
    # Extract authors correctly
    authors = item.get("authors", [])
    if isinstance(authors, list):
        authors = [author.get("name", "") for author in authors if isinstance(author, dict)]

    paper = {
        "PubmedID": item.get("uid"),
        "Title": item.get("title"),
        "Publication Date": item.get("pubdate"),
        "Non-academic Author(s)": extract_non_academic_authors(authors),
        "Company Affiliation(s)": extract_company_affiliations(item.get("affiliations", [])),
        "Corresponding Author Email": item.get("email", "")  # Adjust based on actual data structure
    }
    
    return paper

def extract_non_academic_authors(authors: List[str]) -> str:
    # Heuristic to identify non-academic authors
    non_academic_authors = [author for author in authors if isinstance(author, str) and "university" not in author.lower() and "lab" not in author.lower()]
    return ", ".join(non_academic_authors)

def extract_company_affiliations(affiliations: List[str]) -> str:
    # Heuristic to identify pharmaceutical/biotech companies
    companies = [aff for aff in affiliations if isinstance(aff, str) and ("pharma" in aff.lower() or "biotech" in aff.lower())]
    return ", ".join(companies)

def save_to_csv(papers: List[Dict[str, Optional[str]]], filename: str):
    df = pd.DataFrame(papers)
    df.to_csv(filename, index=False, sep=',')  # Ensure it's saved as a CSV with commas

# Example usage (uncomment to run)
if __name__ == "__main__":
    query = "cancer treatment"
    papers = fetch_papers(query)
    save_to_csv(papers, "output.csv")