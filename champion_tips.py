import mobafire
import pandas as pd

BASE_URL = "https://www.mobafire.com"
BASE_URL_GAME_LOL = BASE_URL + "/league-of-legends/"
BASE_URL_GUIDE_LIST_POSTFIX = "champions"

if __name__ == "__main__":
    url, soup = mobafire.get_soup_from_browse_url(
        browse_url=BASE_URL_GAME_LOL + BASE_URL_GUIDE_LIST_POSTFIX)
    is_df_empty = True

    champion_pages = mobafire.get_champion_pages(soup)

    for idx, champion_page in enumerate(champion_pages, 1):
        print("Fetching champion tips page for",
              champion_page, f"{idx}/{len(champion_pages)}...")
        _, _soup = mobafire.get_soup_from_browse_url(champion_page)

        guides = mobafire.get_top_guides(_soup)
        print("Found", len(guides), "guides:", guides)

        rows = []

        for idx, guide_url in enumerate(guides, 1):
            try:
                print(f"Fetching guide {idx}/{len(guides)}...")
                # print("Guide URL:", BASE_URL+guide_url)
                html_content = mobafire.get_page_html(BASE_URL + guide_url)
                parsed_data = mobafire.parse_guide(html_content)
                rows.extend(parsed_data)
            except Exception as e:
                print(f"Error fetching guide {idx}/{len(guides)}:", e)

        # Convert rows to a DataFrame and then to CSV
        df = pd.DataFrame(rows)
        print(df)
        if is_df_empty:
            df.to_csv('champion_threat_synergy.csv',
                      index=False, header=True, mode='w', encoding='utf-8')
            is_df_empty = False
        else:
            df.to_csv('champion_threat_synergy.csv',
                      index=False, header=None, mode='a', encoding='utf-8')

        print("Saved results to output.csv")
