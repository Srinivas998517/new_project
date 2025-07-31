import argparse
import sys
from new_project.pubmed_module import (
    fetch_pubmed_ids,
    fetch_paper_details,
    filter_papers_by_affiliation,
    write_results_to_csv,
    print_results_to_console
)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch research papers from PubMed and filter by non-academic affiliations.",
        formatter_class=argparse.RawTextHelpFormatter # For better help message formatting
    )
    parser.add_argument("query", type=str,
                        help="The search query for PubMed. Supports PubMed's full query syntax.")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="Print debug information during execution.")
    parser.add_argument("-f", "--file", type=str,
                        help="Specify the filename to save the results as a CSV file. If not provided, output to console.")
    parser.add_argument("-r", "--retmax", type=int, default=100,
                        help="Maximum number of papers to retrieve from PubMed (default: 100).")

    args = parser.parse_args()

    if args.debug:
        print(f"Debug mode enabled.")
        print(f"Query: {args.query}")
        print(f"Output file: {args.file}")
        print(f"Max results (retmax): {args.retmax}")

    # Step 1: Fetch PubMed IDs
    if args.debug: print(f"Fetching PubMed IDs for query: '{args.query}'...")
    pubmed_ids = fetch_pubmed_ids(args.query, retmax=args.retmax)
    if not pubmed_ids:
        print("No PubMed IDs found for the given query.")
        sys.exit(0)
    if args.debug: print(f"Fetched {len(pubmed_ids)} PubMed IDs.")

    # Step 2: Fetch paper details
    if args.debug: print(f"Fetching details for {len(pubmed_ids)} papers...")
    all_papers = fetch_paper_details(pubmed_ids)
    if not all_papers:
        print("Could not retrieve details for any papers.")
        sys.exit(0)
    if args.debug: print(f"Successfully retrieved details for {len(all_papers)} papers.")

    # Step 3: Filter papers by non-academic affiliation
    if args.debug: print("Filtering papers for non-academic affiliations...")
    filtered_papers = filter_papers_by_affiliation(all_papers)
    if not filtered_papers:
        print("No papers found with authors from pharmaceutical or biotech companies.")
        sys.exit(0)
    if args.debug: print(f"Found {len(filtered_papers)} papers with non-academic affiliations.")

    # Step 4: Output results
    if args.file:
        write_results_to_csv(filtered_papers, args.file)
    else:
        print_results_to_console(filtered_papers)

if __name__ == "__main__":
    main()