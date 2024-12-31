"""
ideas:
how many entries (top x%)
average and mode score value
longest streak of consecutive days with entries
min and max score value, include description
largest score difference between 2 consecutive days
months with the highest and lowest average score value
weeks with the highest and lowest average score value
top 10 most common words in entry description
"""

import json
import psycopg2
from datetime import datetime

from wrapped.wrapped_db import db_config

all_results = {}

def execute_queries(cursor: psycopg2._psycopg.cursor, user_id, entry_count, pct, username):

    results = {}
    results['username'] = username
    results['entries'] = entry_count
    results['top_pct'] = pct

    cursor.execute('''
        SELECT AVG(value)
        FROM happiness
        WHERE user_id = (%s) AND timestamp >= '2024-01-01';
    ''', (user_id,))
    results['average_score'] = cursor.fetchone()[0]

    cursor.execute('''
        SELECT value, COUNT(*)
        FROM happiness
        WHERE user_id = (%s) AND timestamp >= '2024-01-01'
        GROUP BY value
        ORDER BY COUNT(*) DESC;
    ''', (user_id,))
    value_counts = cursor.fetchone()
    results['mode_score'] = {
        'score': value_counts[0],
        'count': value_counts[1]
    }

    cursor.execute('''
        SELECT DISTINCT ON (user_id) user_id, min(timestamp), max(timestamp)
        FROM (SELECT happiness.*,
                     row_number() OVER (PARTITION BY user_id ORDER BY timestamp) AS seqnum
              FROM happiness
              WHERE user_id = (%s) AND timestamp >= '2024-01-01'
             ) happiness
        GROUP BY user_id, timestamp - seqnum * interval '1 day'
        ORDER BY user_id, count(*) DESC;
    ''', (user_id,))
    streak = cursor.fetchone()
    results['longest_streak'] = {
        'start': datetime.isoformat(streak[1]),
        'end': datetime.isoformat(streak[2]),
        'days': (streak[2] - streak[1]).days
    }

    cursor.execute('''
        SELECT value, timestamp
        FROM happiness
        WHERE user_id = (%s) AND timestamp >= '2024-01-01'
        ORDER BY value ASC, timestamp ASC
    ''', (user_id,))
    entries_sorted = cursor.fetchall()
    results['min_score'] = {
        'score': entries_sorted[0][0],
        'date': datetime.isoformat(entries_sorted[0][1])
    }
    results['max_score'] = {
        'score': entries_sorted[-1][0],
        'date': datetime.isoformat(entries_sorted[-1][1])
    }

    cursor.execute('''
        WITH daily_scores AS (
            SELECT timestamp AS entry_date, AVG(value) AS scores
            FROM happiness
            WHERE user_id = (%s) AND timestamp >= '2024-01-01'
            GROUP BY timestamp
        ),
             score_differences AS (
                 SELECT entry_date,
                        LEAD(entry_date) OVER (ORDER BY entry_date) AS next_date,
                        scores,
                        LEAD(scores) OVER (ORDER BY entry_date) - scores AS score_diff,
                        ABS(LEAD(scores) OVER (ORDER BY entry_date) - scores) AS abs_score_diff
                 FROM daily_scores
             )
        SELECT entry_date AS start_date,
               next_date AS end_date,
               score_diff AS score_difference
        FROM score_differences
        ORDER BY abs_score_diff DESC, score_diff DESC
        LIMIT 2;
     ''', (user_id,))
    score_diff = cursor.fetchall()[1]
    results['largest_diff'] = {
        'start': datetime.isoformat(score_diff[0]),
        'end': datetime.isoformat(score_diff[1]),
        'diff': score_diff[2] if score_diff[2] < 0 else '+' + str(score_diff[2])
    }

    cursor.execute('''
        WITH monthly_scores AS (
            SELECT DATE_TRUNC('month', timestamp) AS month, AVG(value) AS avg_score
            FROM happiness
            WHERE user_id = (%s) AND timestamp >= '2024-01-01'
            GROUP BY DATE_TRUNC('month', timestamp)
        )
        SELECT month, avg_score
        FROM monthly_scores
        ORDER BY avg_score DESC;
    ''', (user_id,))
    month_data = cursor.fetchall()
    results['month_highest'] = {
        'month': month_data[0][0].month,
        'avg_score': month_data[0][1]
    }
    results['month_lowest'] = {
        'month': month_data[-1][0].month,
        'avg_score': month_data[-1][1]
    }

    cursor.execute('''
        WITH weekly_scores AS (
            SELECT DATE_TRUNC('week', timestamp) AS week, AVG(value) AS avg_score
            FROM happiness
            WHERE user_id = (%s) AND timestamp >= '2024-01-01'
            GROUP BY DATE_TRUNC('week', timestamp)
        )
        SELECT week, avg_score
        FROM weekly_scores
        ORDER BY avg_score DESC;
    ''', (user_id,))
    week_data = cursor.fetchall()
    results['week_highest'] = {
        'week_start': datetime.isoformat(week_data[0][0]), # mondays only
        'avg_score': week_data[0][1]
    }
    results['week_lowest'] = {
        'week_start': datetime.isoformat(week_data[-1][0]),
        'avg_score': week_data[-1][1]
    }

    cursor.execute('''
        WITH words AS (
            SELECT LOWER(UNNEST(string_to_array(comment, ' '))) AS word
            FROM happiness
            WHERE user_id = (%s) AND timestamp >= '2024-01-01'
        ),
            filtered_words AS (
                 SELECT word
                 FROM words
                 WHERE word ~ '^[a-z]+$'
                    AND word NOT IN (
                      'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
                      'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
                      'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                      'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                      'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
                      'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
                      'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
                      'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
                      'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most',
                      'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                      'can', 'will', 'just','should'
                )
            )
        SELECT word, COUNT(*) AS count
        FROM filtered_words
        GROUP BY word
        ORDER BY count DESC
        LIMIT 10;
    ''', (user_id,))
    results['top_words'] = list(map(lambda x: x[0] + ',' + str(x[1]), cursor.fetchall()))

    all_results[user_id] = results

# db_config is a dictionary with the keys: dbname, user, password, host, and port
conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

cursor.execute('''SELECT id, "user".username FROM "user"''')
users_dict = dict(cursor.fetchall())

cursor.execute('''
    SELECT user_id, COUNT(*) AS entry_count
    FROM happiness
    WHERE timestamp >= '2024-01-01'
    GROUP BY user_id
    ORDER BY entry_count DESC;
''')
active_users = cursor.fetchall()

for i, (user_id, entry_count) in enumerate(active_users):
    if entry_count > 20:
        print('processing ' + users_dict[user_id])
        execute_queries(cursor, user_id, entry_count, (i+1)/len(active_users), users_dict[user_id])

with open('wrapped_data_2024.json', 'w') as f:
    json.dump(all_results, f)

cursor.close()
conn.close()