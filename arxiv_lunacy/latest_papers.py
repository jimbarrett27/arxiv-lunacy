from util.constants import INTERESTING_ARXIV_CATEGORIES
import feedparser
from html2text import html2text
from arxiv_lunacy.embeddings import embed_abstract
import pandas as pd
import numpy as np

def get_arxiv_rss_url(arxiv_category: str):

    return f"http://export.arxiv.org/rss/{arxiv_category}"

def get_latest_ids_and_abstracts():

    paper_id_to_abstract = {}
    for category in INTERESTING_ARXIV_CATEGORIES:

        url = get_arxiv_rss_url(category)
        rss_content = feedparser.parse(url)
        for entry in rss_content['entries']:
            paper_id = entry['id'].split('/')[-1]
            paper_id_to_abstract[paper_id] = html2text(entry['summary'])

    return paper_id_to_abstract


def get_latest_embedding_df():

    paper_id_to_abstract = get_latest_ids_and_abstracts()

    paper_ids = []
    embeddings = []
    for paper_id, abstract in paper_id_to_abstract.items():

        paper_ids.append(str(paper_id))
        embeddings.append(embed_abstract(abstract))

    embeddings = np.array(embeddings).squeeze()
    embeddings_df = pd.DataFrame(embeddings)
    # feather doesn't like numerical column names
    embeddings_df = embeddings_df.rename(columns={i:f"dim{i}" for i in embeddings_df.columns})
    embeddings_df["id"] = paper_ids

    return embeddings_df