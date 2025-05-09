import gspread
from google.oauth2.service_account import Credentials


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]
CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("leaderboard")
SCORES_SHEET = SHEET.worksheet("scores")


def get_high_scores(limit=10):
    """
    Fetches and returns the top `limit` high scores from the sheet,
    sorted in descending order by score. Returned as a single string
    formatted for use in a Rich Panel.
    """
    records = SCORES_SHEET.get_all_records()
    sorted_scores = sorted(
                            records,
                            key=lambda r: int(r["score"]),
                            reverse=True
                            )
    top_scores = sorted_scores[:limit]

    lines = ["[bold underline]HIGH SCORES[/bold underline]"]
    for i, entry in enumerate(top_scores, 1):
        name = entry.get("Name", "Anon")
        score = entry.get("score", 0)
        lines.append(f"{i}. {name:<10} {score}")
        lines.append("")  # blank line for spacing

    return "\n".join(lines)


def submit_score(name, score):
    """
    Adds a new row to the Scores sheet.
    """
    SCORES_SHEET.append_row([name, score])
