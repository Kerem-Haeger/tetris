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


def get_high_scores(limit=10, two_columns=False):
    """
    Fetches and returns the top high scores from the sheet,
    sorted in descending order by score.
    If two_columns=True, returns the entries formatted in two columns.
    """
    records = SCORES_SHEET.get_all_records()
    sorted_scores = sorted(
        records,
        key=lambda r: (
            int(r.get("Score", 0))
            if str(r.get("Score", "")).isdigit()
            else 0
        ),
        reverse=True
    )
    top_scores = sorted_scores[:limit]

    if not two_columns:
        lines = [""]
        for i, entry in enumerate(top_scores, 1):
            name = entry.get("Name", "Anon")
            score = entry.get("Score", 0)
            lines.append(f"{i}. {name:<10} {score}")
            lines.append("")
        return "\n".join(lines)

    # Format for two columns (limit should be even)
    column_1 = top_scores[:limit // 2]
    column_2 = top_scores[limit // 2:]

    lines = [""]
    for i in range(len(column_1)):
        left = column_1[i]
        right = column_2[i] if i < len(column_2) else {"Name": "", "Score": ""}
        left_text = (
            f"{i+1}. "
            f"{left.get('Name', 'Anon'):<10} "
            f"{left.get('Score', 0)}"
        )
        right_text = (
            f"{i+1 + limit // 2}. "
            f"{right.get('Name', 'Anon'):<10} "
            f"{right.get('Score', 0)}"
        )
        lines.append(f"{left_text:<25} {right_text}")
    return "\n".join(lines)


def submit_score(name, score):
    """ Adds a new row to the Scores sheet. """
    try:
        SCORES_SHEET.append_row([name, int(score)])
    except Exception as e:
        print(f"Error submitting score: {e}")
