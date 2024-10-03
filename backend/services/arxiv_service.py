import arxiv
from datetime import datetime, timedelta
from dateutil.parser import parse
from dateutil.tz import tzutc

def fetch_arxiv_papers():
    # Define the search query for ML papers related to mining/metallurgy
    search_query = 'cat:cs.LG AND (mining OR metallurgy OR "mineral processing")'
    
    # Set up the API client
    client = arxiv.Client()
    
    # Get papers from the last 30 days
    start_date = datetime.now(tzutc()) - timedelta(days=30)
    
    # Fetch papers
    search = arxiv.Search(
        query=search_query,
        max_results=100,  # Adjust as needed
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    papers = []
    for result in client.results(search):
        # Parse the published date and make it timezone-aware
        published_date = parse(result.published.isoformat()).replace(tzinfo=tzutc())
        if published_date > start_date:
            # Fetch the full text (if possible)
            full_text = result.summary  # Use the abstract as a placeholder
            paper = {
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'abstract': result.summary,
                'arxiv_id': result.entry_id.split('/')[-1],
                'publication_date': published_date,
                'full_text': full_text
            }
            papers.append(paper)
    
    return papers