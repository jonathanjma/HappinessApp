def build_yearly_prompt(all_entries_text: str) -> str:
    return f"""
You are analyzing entries from a user's happiness journal from the past year. Each entry has a score between 0 and 10 describing the user's happiness level that day,
with 0 being the lowest and 10 being the highest, and a comment describing what happened that day.

INPUTS:
- all_entries: a single text block where each entry is formatted like "YYYY-MM-DD: <comment>", separated by blank lines.

TASKS:
1) Themes of the year: Using all_entries, extract the top 3 words or short phrases that best describe the user's year overall.
Each item must be less than 4 words, written in present tense, only use verbs ending in 'ing', and be an incomplete sentence (no subject).
Please capitalize the first word of each item.
Use specific events, situations, or behaviors seen across multiple entries, avoiding adjectives or abstract traits.
Output as a list of strings.

2) Strangest / craziest entry: Identify the single most unusual, unexpected, or absurd entry in all_entries.
Output the date (YYYY-MM-DD) and a 1-sentence summary (less than 25 words) referencing specific details from the entry.

3) Most overthinking entry: Identify the entry with the highest concentration of rumination, repeated doubts, hypothetical scenarios, or mental spirals.
Output the date (YYYY-MM-DD) and a 1-sentence summary (less than 25 words) referencing specific details from the entry.

4) Most "down bad" entry: Identify the entry with the strongest romantic longing, fixation, or emotional vulnerability toward another person.
Output the date (YYYY-MM-DD) and a 1-sentence summary (less than 25 words) referencing specific details and the context from the entry.

OUTPUT REQUIREMENTS (critical):
- Output ONLY valid JSON. No markdown, no prose.
- Use this exact schema:
{{
  "top_3_themes": list[string],
  "strangest_entry": {{"date": "YYYY-MM-DD", "summary": string}},
  "overthinking_entry": {{"date": "YYYY-MM-DD", "summary": string}},
  "down_bad_entry": {{"date": "YYYY-MM-DD", "summary": string}}
}}
- The analysis should be written in past-tense and second person, addressing the user.
- The analysis should also avoid generic phrases and only use details which appear in all_entries.
- Be specific but concise.

all_entries:
{all_entries_text}
""".strip()


def build_score_bands_prompt(entries_0_4_text: str, entries_8_10_text: str) -> str:
    return f"""
You are analyzing entries from a user's happiness journal. Each entry has a score between 0 and 10 describing the user's happiness level that day,
with 0 being the lowest and 10 being the highest, and a comment describing what happened that day.

INPUTS:
- entries_0_4: comments from entries with score 0-4 (sad days)
- entries_8_10: comments from entries with score 8-10 (happy days)

TASK:
List the top 3 words or short phrases that best describe what made the user feel sad, for entries_0_4, and happy, for entries_8_10.
Each item must be less than 4 words, written in present tense, only use verbs ending in 'ing', and be an incomplete sentence (no subject).
Please capitalize the first word of each item.
Base each item on specific events, situations, or emotions from the entry.
Keep each item less than 4 words.
Avoid generic words or phrases.

OUTPUT REQUIREMENTS (critical):
- Output ONLY valid JSON. No markdown, no prose.
- Use this exact schema:
{{
  "theme_0_4": list[string],
  "theme_8_10": list[string]
}}
- Be specific but concise.

entries_0_4:
{entries_0_4_text}

entries_8_10:
{entries_8_10_text}
""".strip()


def build_day_summaries_prompt(highest_day: str, lowest_day: str) -> str:
    return f"""
You are analyzing entries from a user's happiness journal. Each entry has a score between 0 and 10 describing the user's happiness level that day,
with 0 being the lowest and 10 being the highest, and a comment describing what happened that day.

TASK:
Write exactly one sentence (less than 25 words) summarizing the user's highest- and one sentence for the lowest-rated day.
Emphasize the specific event, action, or emotion that made the day especially happy (highest) or sad (lowest).
Include at least one concrete detail from the entry.
Avoid generic phrases.
This sentence will be shown as a short preview on a webpage.

OUTPUT REQUIREMENTS (critical):
- Output ONLY valid JSON. No markdown, no prose.
- Use this exact schema:
{{
  "highest_day_summary": string,
  "lowest_day_summary": string
}}
- Write in past-tense and second person, addressing the user.
- Be specific but concise.

highest_day:
{highest_day}

lowest_day:
{lowest_day}
""".strip()


def build_week_summaries_prompt(highest_week_entries: str, lowest_week_entries: str) -> str:
    return f"""
You are analyzing entries from a user's happiness journal. Each entry has a score between 0 and 10 describing the user's happiness level that day,
with 0 being the lowest and 10 being the highest, and a comment describing what happened that day.

TASK:
Write exactly one sentence (less than 25 words) summarizing the user's week with the highest average score and one sentence for the week with the lowest average score.
Emphasize specific events, actions, or emotions that made the week especially happy (highest) or sad (lowest).
Include at least one concrete detail from the entries.
Avoid generic phrases.
This sentence will be shown as a short preview on a webpage.

OUTPUT REQUIREMENTS (critical):
- Output ONLY valid JSON. No markdown, no prose.
- Use this exact schema:
{{
  "highest_week_summary": string,
  "lowest_week_summary": string
}}
- Write in past-tense and second person, addressing the user.
- Be specific but concise.

highest_week_entries:
{highest_week_entries}

lowest_week_entries:
{lowest_week_entries}
""".strip()


def build_month_summaries_prompt(highest_month_entries: str, lowest_month_entries: str) -> str:
    return f"""
You are analyzing entries from a user's happiness journal. Each entry has a score between 0 and 10 describing the user's happiness level that day,
with 0 being the lowest and 10 being the highest, and a comment describing what happened that day.

TASK:
Write exactly one sentence (less than 25 words) summarizing the user's month with the highest average score and one sentence for the month with the lowest average score.
Emphasize any recurring events, situations, or emotions that most influenced the month's mood (positive for highest, negative for lowest).
Include at least one concrete, repeated detail from multiple entries (not a single-day event).
Avoid generic phrases.
This sentence will be shown as a short preview on a webpage.

OUTPUT REQUIREMENTS (critical):
- Output ONLY valid JSON. No markdown, no prose.
- Use this exact schema:
{{
  "highest_month_summary": string,
  "lowest_month_summary": string
}}
- Write in past-tense and second person, addressing the user.
- Be specific but concise.

highest_month_entries:
{highest_month_entries}

lowest_month_entries:
{lowest_month_entries}
""".strip()


def build_largest_swing_prompt(swing_context: str) -> str:
    return f"""
You are analyzing entries from a user's happiness journal. Each entry has a score between 0 and 10 describing the user's happiness level that day,
with 0 being the lowest and 10 being the highest, and a comment describing what happened that day.

TASK:
Write exactly one sentence (less than 25 words) summarizing the user's largest swing in happiness between two consecutive days.
Emphasize the specific event, action, or emotion that made the start day or end day especially happy or sad.
Include at one concrete detail from the start day entry and one concrete detail from the end day entry.
Do not mention the exact numerical jump in score, but mentioning the trend is fine.
Avoid generic phrases.
This sentence will be shown as a short preview on a webpage.

OUTPUT REQUIREMENTS (critical):
- Output ONLY valid JSON. No markdown, no prose.
- Use this exact schema:
{{
  "largest_swing_summary": string
}}
- Write in past-tense and second person, addressing the user.
- Be specific but concise.

swing_context:
{swing_context}
""".strip()
