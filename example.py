import mobafire
import pandas as pd

if __name__ == "__main__":
    url, soup = mobafire.get_soup_from_browse_url()
    next_page_url = url
    is_df_empty = True
    while next_page_url:
        print("Fetching guides from:", next_page_url)
        # html_content = mobafire.get_page_html(next_page_url)
        url, soup = mobafire.get_soup_from_browse_url(next_page_url)

        guides = mobafire.get_guides(soup)
        print("Found", len(guides), "guides:")

        rows = []

        for idx, guide_url in enumerate(guides, 1):
            try:
                print(f"Fetching guide {idx}/{len(guides)}...")
                html_content = mobafire.get_page_html(guide_url)
                parsed_data = mobafire.parse_guide(html_content)
                rows.extend(parsed_data)
            except Exception as e:
                print(f"Error fetching guide {idx}/{len(guides)}:", e)

        # Convert rows to a DataFrame and then to CSV
        df = pd.DataFrame(rows)
        print(df)
        if is_df_empty:
            df.to_csv('output.csv', index=False, header=True, mode='w')
            is_df_empty = False
        else:
            df.to_csv('output.csv', index=False, header=None, mode='a')

        print("Saved results to output.csv")

        next_page_url = mobafire.get_next_page_url(soup)
