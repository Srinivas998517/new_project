
from Bio import Entrez
import xml.etree.ElementTree as ET
import csv
import sys
import ssl # Import the ssl module


Entrez.email = "srinu@gmail.com" # Replace with your actual email

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    # Handle target environment that doesn't have certificate verification
    ssl._create_default_https_context = _create_unverified_https_context

def fetch_pubmed_ids(query: str, retmax: int = 10) -> list[str]:
    """
    Fetches PubMed IDs for a given query.
    """
    try:
        # Use esearch to get a list of PubMed IDs
        handle = Entrez.esearch(db="pubmed", term=query, retmax=retmax)
        record = Entrez.read(handle)
        handle.close()
        return record["IdList"]
    except Exception as e:
        print(f"Error fetching PubMed IDs: {e}")
        return []


def fetch_paper_details(pubmed_ids: list[str]) -> list[dict]:
    """
    Fetches details for a list of PubMed IDs.
    """
    if not pubmed_ids:
        return []

    id_list_str = ",".join(pubmed_ids)
    papers_data = []

    try:
        # Use efetch to get full article details in XML format
        handle = Entrez.efetch(db="pubmed", id=id_list_str, retmode="xml")
        xml_data = handle.read()
        handle.close()

        root = ET.fromstring(xml_data)

        # Parse XML to extract required details
        for article in root.findall(".//PubmedArticle"):
            pubmed_id = article.find(".//PMID").text if article.find(".//PMID") is not None else "N/A"
            title = article.find(".//ArticleTitle").text if article.find(".//ArticleTitle") is not None else "N/A"

            pub_date_node = article.find(".//PubDate")
            publication_date = "N/A"
            if pub_date_node is not None:
                year = pub_date_node.find(".//Year")
                month = pub_date_node.find(".//Month")
                day = pub_date_node.find(".//Day")

                date_parts = []
                if year is not None:
                    date_parts.append(year.text)
                if month is not None:
                    date_parts.append(month.text)
                if day is not None:
                    date_parts.append(day.text)

                publication_date = "-".join(date_parts) if date_parts else "N/A"

            authors_info = []
            corresponding_author_email = "N/A"

            for author in article.findall(".//AuthorList/Author"):
                last_name = author.find(".//LastName").text if author.find(".//LastName") is not None else ""
                fore_name = author.find(".//ForeName").text if author.find(".//ForeName") is not None else ""
                full_name = f"{fore_name} {last_name}".strip()

                affiliation_node = author.find(".//AffiliationInfo/Affiliation")
                affiliation = affiliation_node.text if affiliation_node is not None else ""

                authors_info.append({
                    "name": full_name,
                    "affiliation": affiliation
                })

            papers_data.append({
                "PubmedID": pubmed_id,
                "Title": title,
                "Publication Date": publication_date,
                "AuthorsInfo": authors_info,
                "Corresponding Author Email": corresponding_author_email # This will often be N/A for now
            })
    except ET.ParseError as e:
        print(f"Error parsing XML data: {e}")
    except Exception as e:
        print(f"Error fetching or processing paper details: {e}")

    return papers_data


def is_non_academic_affiliation(affiliation: str) -> bool:
    """
    Checks if an affiliation indicates a pharmaceutical or biotech company.
    Uses simple keyword matching (heuristics).
    """
    affiliation_lower = affiliation.lower()

    company_keywords = [
        "pharmaceutical", "pharma", "biotech", "biotechnology", "inc.", "llc",
        "corp", "corporation", "company", "gmbh", "ag", "laboratories",
        "labs", "medicines", "drug development", "research and development",
        "rd", "bio-", # e.g., "bio-rad"
        "diagnostics", "therapeutics", "novartis", "pfizer", "roche",
        "merck", "janssen", "amgen", "genentech", "gilead", "astrazeneca",
        "sanofi", "eli lilly", "bayer", "glaxosmithkline", "abbvie"
    ]

    academic_keywords = [
        "university", "college", "institute", "hospital", "clinic", "school",
        "department", "center for disease control", "cdc", "nih", "fda",
        "national institutes of health", "medical school", "academia",
        "government", "public health", "foundation", "research center",
        "academy"
    ]

    # Check for company keywords
    for keyword in company_keywords:
        if keyword in affiliation_lower:
            is_company = True
            for academic_keyword in academic_keywords:
                if academic_keyword in affiliation_lower:
                    is_company = False
                    break
            if is_company:
                return True

    for comp_k in company_keywords:
        if comp_k in affiliation_lower:
            is_academic = False
            for acad_k in academic_keywords:
                if acad_k in affiliation_lower:
                    is_academic = True
                    break
            if not is_academic:
                return True

    return False


def filter_papers_by_affiliation(papers: list[dict]) -> list[dict]:
    """
    Filters papers to include only those with at least one non-academic author.
    Adds 'Non-academic Author(s)' and 'Company Affiliation(s)' fields.
    """
    filtered_results = []
    for paper in papers:
        non_academic_authors = []
        company_affiliations = []

        for author_info in paper['AuthorsInfo']:
            if is_non_academic_affiliation(author_info['affiliation']):
                non_academic_authors.append(author_info['name'])
                if author_info['affiliation'] not in company_affiliations:
                    company_affiliations.append(author_info['affiliation'])

        if non_academic_authors: # If there's at least one non-academic author
            filtered_paper = {
                "PubmedID": paper['PubmedID'],
                "Title": paper['Title'],
                "Publication Date": paper['Publication Date'],
                "Non-academic Author(s)": ", ".join(non_academic_authors),
                "Company Affiliation(s)": "; ".join(company_affiliations),
                "Corresponding Author Email": paper['Corresponding Author Email']
            }
            filtered_results.append(filtered_paper)

    return filtered_results


def write_results_to_csv(data: list[dict], filename: str):
    """
    Writes the filtered paper data to a CSV file.
    """
    if not data:
        print("No data to write.")
        return

    fieldnames = [
        "PubmedID",
        "Title",
        "Publication Date",
        "Non-academic Author(s)",
        "Company Affiliation(s)",
        "Corresponding Author Email"
    ]

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Results successfully saved to {filename}")
    except IOError as e:
        print(f"Error writing to CSV file {filename}: {e}")

def print_results_to_console(data: list[dict]):
    """
    Prints the filtered paper data to the console.
    """
    if not data:
        print("No papers found with non-academic affiliations.")
        return

    for paper in data:
        print(f"PubmedID: {paper.get('PubmedID', 'N/A')}")
        print(f"Title: {paper.get('Title', 'N/A')}")
        print(f"Publication Date: {paper.get('Publication Date', 'N/A')}")
        print(f"Non-academic Author(s): {paper.get('Non-academic Author(s)', 'N/A')}")
        print(f"Company Affiliation(s): {paper.get('Company Affiliation(s)', 'N/A')}")
        print(f"Corresponding Author Email: {paper.get('Corresponding Author Email', 'N/A')}")
        print("-" * 50)

if __name__ == "__main__":
    test_query = "CRISPR gene editing"
    print(f"Fetching IDs for query: '{test_query}'")
    ids = fetch_pubmed_ids(test_query, retmax=5)
    print(f"Fetched IDs: {ids}")

    if ids:
        print("\nFetching details for these IDs...")
        papers = fetch_paper_details(ids)
        papers = filter_papers_by_affiliation(papers) # Filter here for direct test
        for paper in papers:
            print(f"PubmedID: {paper['PubmedID']}")
            print(f"Title: {paper['Title']}")
            print(f"Publication Date: {paper['Publication Date']}")
            print(f"Non-academic Author(s): {paper['Non-academic Author(s)']}")
            print(f"Company Affiliation(s): {paper['Company Affiliation(s)']}")
            print(f"Corresponding Author Email: {paper['Corresponding Author Email']}")
            print("-" * 20)
