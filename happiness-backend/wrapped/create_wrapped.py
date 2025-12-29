"""
ideas:
how many entries and top x% of users by entries
how many words
average score value
longest streak of consecutive days with entries


min and max score value, include description
largest score difference between 2 consecutive days
months with the highest and lowest average score value
weeks with the highest and lowest average score value

AI component:
3 words/phrases which describe the year
things which made you sad vs happy (using 0-4 vs 8-10 days)
strangest or craziest entry
overthinking entry
most down bad entry

short summary of highest and lowest day
short summary of highest and lowest week
short summary of highest and lowest month
short summary of largest score swing between 2 consecutive days


top person who appears
top place which appears

"""

import json
import re
import psycopg2
from datetime import date, datetime, timedelta

from wrapped_db import db_config, gemini_api_key

from google import genai

from gemini_prompts import (
    build_day_summaries_prompt,
    build_largest_swing_prompt,
    build_month_summaries_prompt,
    build_score_bands_prompt,
    build_week_summaries_prompt,
    build_yearly_prompt,
)

current_year = datetime.now().year
all_results = {}


def _next_month_start(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def _fetch_entries_in_range(
    cursor: psycopg2._psycopg.cursor,
    user_id: int,
    start_date,
    end_date,
) -> str:
    cursor.execute(
        """
        SELECT timestamp, comment
        FROM happiness
        WHERE user_id = (%s) AND timestamp >= %s AND timestamp < %s
        ORDER BY timestamp ASC;
        """,
        (user_id, start_date, end_date),
    )

    return "\n\n".join([entry[1] for entry in cursor.fetchall()])


def _extract_first_json_object(text: str) -> dict:
    """
    Best-effort extraction of the first JSON object in a response.
    Gemini can occasionally wrap JSON in prose or code fences.
    """
    text = text.strip()
    # Strip code fences if present.
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    # Fast path.
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    # Best-effort: find first {...} block.
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in Gemini response.")
    return json.loads(match.group(0))


def run_gemini_json(name: str, prompt: str) -> dict:
    print(f'executing Gemini analysis for {name} at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}...')
    try:
        client = genai.Client(api_key=gemini_api_key)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )
        # save response to file
        with open('gemini_response.txt', 'a') as f:
            f.write(response.text)
            f.write("\n")
        return _extract_first_json_object(response.text)
    except Exception as e:
        return {"error": "gemini_call_failed", "details": str(e)}


def execute_queries(cursor: psycopg2._psycopg.cursor, user_id, entry_count, pct, username):

    results = {}
    results['username'] = username
    results['entries'] = entry_count
    results['top_pct'] = pct

    print('executing database queries...')

    # get average score value
    cursor.execute('''
        SELECT AVG(value)
        FROM happiness
        WHERE user_id = (%s) AND timestamp >= %s;
    ''', (user_id, f'{current_year}-01-01'))
    results['average_score'] = cursor.fetchone()[0]

    # get longest streak of consecutive days with entries
    cursor.execute('''
        SELECT DISTINCT ON (user_id) user_id, min(timestamp), max(timestamp)
        FROM (SELECT happiness.*,
                     row_number() OVER (PARTITION BY user_id ORDER BY timestamp) AS seqnum
              FROM happiness
              WHERE user_id = (%s) AND timestamp >= %s
             ) happiness
        GROUP BY user_id, timestamp - seqnum * interval '1 day'
        ORDER BY user_id, count(*) DESC;
    ''', (user_id, f'{current_year}-01-01'))
    streak = cursor.fetchone()
    results['longest_streak'] = {
        'start': datetime.isoformat(streak[1]),
        'end': datetime.isoformat(streak[2]),
        'days': (streak[2] - streak[1]).days
    }

    # get min and max score value
    cursor.execute('''
        SELECT value, timestamp, comment
        FROM happiness
        WHERE user_id = (%s) AND timestamp >= %s
        ORDER BY value ASC, timestamp ASC
    ''', (user_id, f'{current_year}-01-01'))
    entries_sorted = cursor.fetchall()
    results['min_score'] = {
        'score': entries_sorted[0][0],
        'date': datetime.isoformat(entries_sorted[0][1])
    }
    results['max_score'] = {
        'score': entries_sorted[-1][0],
        'date': datetime.isoformat(entries_sorted[-1][1]),
    }
    min_score_comment = entries_sorted[0][2]
    max_score_comment = entries_sorted[-1][2]

    # get all entries with scores 0-4
    cursor.execute('''
        SELECT comment FROM happiness
        WHERE user_id = (%s) AND timestamp >= %s AND value >= 0 AND value <= 4
        ORDER BY timestamp ASC
    ''', (user_id, f'{current_year}-01-01'))
    entries_0_4 = "\n\n".join([entry[0] for entry in cursor.fetchall()])

    # get all entries with scores 8-10
    cursor.execute('''
        SELECT comment FROM happiness
        WHERE user_id = (%s) AND timestamp >= %s AND value >= 8 AND value <= 10
        ORDER BY timestamp ASC
    ''', (user_id, f'{current_year}-01-01'))
    entries_8_10 = "\n\n".join([entry[0] for entry in cursor.fetchall()])

    # get largest score difference between 2 consecutive days
    cursor.execute('''
        WITH daily_scores AS (
            SELECT timestamp AS entry_date,
                   AVG(value) AS scores,
                   (array_agg(comment ORDER BY timestamp))[1] AS comment
            FROM happiness
            WHERE user_id = (%s) AND timestamp >= %s
            GROUP BY timestamp
        ),
             score_differences AS (
                 SELECT entry_date,
                        LEAD(entry_date) OVER (ORDER BY entry_date) AS next_date,
                        scores,
                        LEAD(scores) OVER (ORDER BY entry_date) - scores AS score_diff,
                        ABS(LEAD(scores) OVER (ORDER BY entry_date) - scores) AS abs_score_diff,
                        comment AS start_comment,
                        LEAD(comment) OVER (ORDER BY entry_date) AS end_comment
                 FROM daily_scores
             )
        SELECT entry_date AS start_date,
               next_date AS end_date,
               score_diff AS score_difference,
               start_comment,
               end_comment
        FROM score_differences
        ORDER BY abs_score_diff DESC, score_diff DESC
        LIMIT 2;
     ''', (user_id, f'{current_year}-01-01'))
    score_diff = cursor.fetchall()[1]
    results['largest_diff'] = {
        'start_date': datetime.isoformat(score_diff[0]),
        'end_date': datetime.isoformat(score_diff[1]),
        'score_difference': score_diff[2] if score_diff[2] < 0 else '+' + str(score_diff[2]),
    }
    largest_diff_comment = f"Score Difference: {str(score_diff[2])}\nStart Day: {score_diff[3]}\nEnd Day: {score_diff[4]}"

    # get months with the highest and lowest average score value
    cursor.execute('''
        WITH monthly_scores AS (
            SELECT DATE_TRUNC('month', timestamp) AS month, AVG(value) AS avg_score
            FROM happiness
            WHERE user_id = (%s) AND timestamp >= %s
            GROUP BY DATE_TRUNC('month', timestamp)
        )
        SELECT month, avg_score
        FROM monthly_scores
        ORDER BY avg_score DESC;
    ''', (user_id, f'{current_year}-01-01'))
    month_data = cursor.fetchall()
    results['month_highest'] = {
        'month': month_data[0][0].month,
        'avg_score': month_data[0][1]
    }
    results['month_lowest'] = {
        'month': month_data[-1][0].month,
        'avg_score': month_data[-1][1]
    }

    highest_month_start = month_data[0][0].date()
    lowest_month_start = month_data[-1][0].date()
    highest_month_entries = _fetch_entries_in_range(
        cursor, user_id, highest_month_start, _next_month_start(
            highest_month_start)
    )
    lowest_month_entries = _fetch_entries_in_range(
        cursor, user_id, lowest_month_start, _next_month_start(
            lowest_month_start)
    )

    # get weeks with the highest and lowest average score value
    cursor.execute('''
        WITH weekly_scores AS (
            SELECT DATE_TRUNC('week', timestamp) AS week, AVG(value) AS avg_score
            FROM happiness
            WHERE user_id = (%s) AND timestamp >= %s
            GROUP BY DATE_TRUNC('week', timestamp)
        )
        SELECT week, avg_score
        FROM weekly_scores
        ORDER BY avg_score DESC;
    ''', (user_id, f'{current_year}-01-01'))
    week_data = cursor.fetchall()
    results['week_highest'] = {
        'week_start': datetime.isoformat(week_data[0][0]),  # mondays only
        'avg_score': week_data[0][1]
    }
    results['week_lowest'] = {
        'week_start': datetime.isoformat(week_data[-1][0]),
        'avg_score': week_data[-1][1]
    }

    highest_week_start = week_data[0][0].date()
    lowest_week_start = week_data[-1][0].date()
    highest_week_entries = _fetch_entries_in_range(
        cursor, user_id, highest_week_start, highest_week_start +
        timedelta(days=7)
    )
    lowest_week_entries = _fetch_entries_in_range(
        cursor, user_id, lowest_week_start, lowest_week_start +
        timedelta(days=7)
    )

    # get all entries for the year
    cursor.execute('''
        SELECT timestamp, comment FROM happiness
        WHERE user_id = (%s) AND timestamp >= %s
        ORDER BY timestamp ASC
    ''', (user_id, f'{current_year}-01-01'))
    all_entries = "\n\n".join(
        [f"{datetime.strftime(entry[0], '%Y-%m-%d')}: {entry[1]}" for entry in cursor.fetchall()])

    # AI analysis (Gemini)
    print('executing Gemini analysis...')

    results.update({
        "yearly": run_gemini_json('yearly', build_yearly_prompt(all_entries)),
        "score_bands": run_gemini_json('score_bands', build_score_bands_prompt(entries_0_4, entries_8_10))
    })

    day_summaries = run_gemini_json(
        'day_summaries', build_day_summaries_prompt(max_score_comment, min_score_comment))
    results['min_score']['ai_summary'] = day_summaries['lowest_day_summary']
    results['max_score']['ai_summary'] = day_summaries['highest_day_summary']

    week_summaries = run_gemini_json('week_summaries', build_week_summaries_prompt(
        highest_week_entries, lowest_week_entries))
    results['week_highest']['ai_summary'] = week_summaries['highest_week_summary']
    results['week_lowest']['ai_summary'] = week_summaries['lowest_week_summary']

    month_summaries = run_gemini_json('month_summaries', build_month_summaries_prompt(
        highest_month_entries, lowest_month_entries))
    results['month_highest']['ai_summary'] = month_summaries['highest_month_summary']
    results['month_lowest']['ai_summary'] = month_summaries['lowest_month_summary']

    results['largest_diff']['ai_summary'] = run_gemini_json('largest_swing_summary',
                                                            build_largest_swing_prompt(largest_diff_comment))

    all_results[user_id] = results


# db_config is a dictionary with the keys: dbname, user, password, host, and port
conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

cursor.execute('''SELECT id, "user".username FROM "user"''')
users_dict = dict(cursor.fetchall())

cursor.execute('''
    SELECT user_id, COUNT(*) AS entry_count
    FROM happiness
    WHERE timestamp >= %s
    GROUP BY user_id
    ORDER BY entry_count DESC;
''', (f'{current_year}-01-01',))
active_users = cursor.fetchall()

for i, (user_id, entry_count) in enumerate(active_users):
    if entry_count > 20 and user_id == 3:
        print('processing ' + users_dict[user_id])
        execute_queries(cursor, user_id, entry_count, (i+1) /
                        len(active_users), users_dict[user_id])

with open(f'wrapped_data_{current_year}.json', 'w') as f:
    json.dump(all_results, f)

cursor.close()
conn.close()
