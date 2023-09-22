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
        print("Fetching champion abilities page for",
              champion_page, f"{idx}/{len(champion_pages)}...")
        _, _soup = mobafire.get_soup_from_browse_url(champion_page)

        champion_name = mobafire.get_champion_name(_soup)

        passive_abilities, abilities = mobafire.get_champion_abilities(_soup)

        rows = []

        for passive_ability in passive_abilities:
            rows.append({
                **champion_name,
                **passive_ability,
            })

        for ability in abilities:
            rows.append({
                **champion_name,
                **ability,
            })

        # Convert rows to a DataFrame and then to CSV
        df = pd.DataFrame(rows)
        print(df)
        if is_df_empty:
            df.to_csv('champion_abilities.csv',
                      index=False, header=True, mode='w', encoding='utf-8')
            is_df_empty = False
        else:
            df.to_csv('champion_abilities.csv',
                      index=False, header=None, mode='a', encoding='utf-8')

        print("Saved results to output.csv")
