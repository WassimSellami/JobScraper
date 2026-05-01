from settings import (
    GLASSDOOR_USE_GERMAN_FILTER,
    LAST_DAYS,
    PROCESS_GLASSDOOR,
    PROCESS_STEPSTONE,
    PROCESS_XING,
    STEPSTONE_USE_GERMAN_FILTER,
    XING_USE_GERMAN_FILTER,
)

OUTPUT_DIR = "output"
STEPSTONE_CLEANED_RECENT_TEMP_FILE = "stepstone_cleaned_recent.csv"
STEPSTONE_APPLY_RECENT_TEMP_FILE = "stepstone_apply_recent.csv"

XING_INPUT_FILE = "input/xing.csv"
XING_CLEANED_RECENT_TEMP_FILE = "xing_cleaned_recent.csv"
XING_APPLY_RECENT_TEMP_FILE = "xing_apply_recent.csv"

GLASSDOOR_INPUT_FILE = "input/glassdoor.csv"
GLASSDOOR_CLEANED_RECENT_TEMP_FILE = "glassdoor_cleaned_recent.csv"
GLASSDOOR_APPLY_RECENT_TEMP_FILE = "glassdoor_apply_recent.csv"

GERMAN_FILTER_REQUEST_DELAY = 0.2

STEPSTONE_INPUT_FILE = "input/stepstone.csv"
STEPSTONE_GERMAN_FILTER_RECENT_TEMP_FILE = STEPSTONE_APPLY_RECENT_TEMP_FILE
STEPSTONE_FINAL_RECENT_OUTPUT_TEMPLATE = "stepstone_recent_{days}days_{date}.csv"
GLASSDOOR_FINAL_RECENT_OUTPUT_TEMPLATE = "glassdoor_recent_{days}days_{date}.csv"
XING_FINAL_RECENT_OUTPUT_TEMPLATE = "xing_recent_{days}days_{date}.csv"

STEPSTONE_TITLE_KEYWORDS = [
    "Softwareentwickler",
    "Developer",
    "Engineer",
    "Entwickler",
]
STEPSTONE_URL_KEYWORDS = [
    r"stepstone\.de/stellenangebote--",
    r"stepstone\.de/stellenangebote",
    r"-inline\.html",
]
STEPSTONE_DATE_KEYWORDS = [r"vor\s+\d+"]
STEPSTONE_MATCH_KEYWORDS = ["Passt"]

GLASSDOOR_TITLE_KEYWORDS = [
    r"m/w/d",
    r"all gender",
    r"\b(?:engineer|developer|scientist|architect|manager|specialist|consultant|analyst|devops|data|application|software|process|test|quality|security|sales|product)\b",
]
GLASSDOOR_URL_KEYWORDS = [r"/job-listing/"]
GLASSDOOR_DATE_KEYWORDS = [r"^\d+(?:Std|T)$"]

XING_TITLE_COLUMN_KEYWORDS = ["headline"]
XING_URL_KEYWORDS = [r"(?:www\.)?xing\.com/jobs/|/jobs/"]
XING_DATE_KEYWORDS = [
    r"^(?:\d+\s+(?:hour|hours|day|days|week|weeks|month|months|year|years)\s+ago|yesterday|just now|today)$",
]

POSITION_EXCLUSION_TERMS = [
    "Senior",
    "Lead",
    "Professor",
    "Projektleiter",
    "Manager",
    "ERP",
    "Defence",
    "Architect",
    "architekt",
    "Working Student",
    "Werkstudent",
    "Internship",
    "Praktikum",
    "Head of",
    "Leiter",
    "Teamleiter",
    "Geschäftsführer",
    "Chief",
    "Masterthesis",
    "Masterarbeit",
    "student assistant",
    "Embedded Software Engineer",
    "Site Reliability Engineer",
    "Staff Frontend Developer",
]

COMPANY_EXCLUSION_TERMS = [
    "Helsing",
    "Ferchau",
    "check24",
    "Bending Spoons",
    "BMW Group",
    "NVIDIA",
]

LINKEDIN_JOB_LEVEL_ALLOWED_VALUES = [
    "entry level",
    "mid-senior level",
    "not applicable",
]

DEUTSCH_VALUE = "Deutsch"

STEPSTONE_REMOVE_EXACT_VALUE = DEUTSCH_VALUE

SITE_PIPELINE_CONFIGS = {
    "stepstone": {
        "enabled": PROCESS_STEPSTONE,
        "input_file": STEPSTONE_INPUT_FILE,
        "recent_temp_output_file": STEPSTONE_CLEANED_RECENT_TEMP_FILE,
        "title_column_name_keywords": [],
        "title_content_keywords": STEPSTONE_TITLE_KEYWORDS,
        "title_exclude_url": True,
        "url_content_keywords": STEPSTONE_URL_KEYWORDS,
        "date_content_keywords": STEPSTONE_DATE_KEYWORDS,
        "extra_columns": [
            {
                "name": "match",
                "content_keywords": STEPSTONE_MATCH_KEYWORDS,
            }
        ],
        "drop_exact_value_rows": [STEPSTONE_REMOVE_EXACT_VALUE],
        "date_parser": "stepstone",
        "use_german_filter": STEPSTONE_USE_GERMAN_FILTER,
        "german_filter_temp_output_file": STEPSTONE_GERMAN_FILTER_RECENT_TEMP_FILE,
        "final_output_template": STEPSTONE_FINAL_RECENT_OUTPUT_TEMPLATE,
        "sort_columns": ["match", "_date_age_days"],
        "output_column_order": ["match", "date", "position", "job_url"],
        "categorical_columns": [
            {
                "name": "match",
                "exclude_value": "Passt weniger",
                "replacements": {"Passt hervorragend": "per", "Passt gut": "gut"},
                "categories": ["per", "gut"],
            }
        ],
    },
    "glassdoor": {
        "enabled": PROCESS_GLASSDOOR,
        "input_file": GLASSDOOR_INPUT_FILE,
        "recent_temp_output_file": GLASSDOOR_CLEANED_RECENT_TEMP_FILE,
        "title_column_name_keywords": [],
        "title_content_keywords": GLASSDOOR_TITLE_KEYWORDS,
        "title_exclude_url": True,
        "url_content_keywords": GLASSDOOR_URL_KEYWORDS,
        "date_content_keywords": GLASSDOOR_DATE_KEYWORDS,
        "extra_columns": [],
        "drop_exact_value_rows": [],
        "date_parser": "glassdoor",
        "use_german_filter": GLASSDOOR_USE_GERMAN_FILTER,
        "german_filter_temp_output_file": None,
        "final_output_template": GLASSDOOR_FINAL_RECENT_OUTPUT_TEMPLATE,
        "sort_columns": ["_date_age_days"],
        "output_column_order": ["date", "position", "job_url"],
        "categorical_columns": [],
    },
    "xing": {
        "enabled": PROCESS_XING,
        "input_file": XING_INPUT_FILE,
        "recent_temp_output_file": XING_CLEANED_RECENT_TEMP_FILE,
        "title_column_name_keywords": XING_TITLE_COLUMN_KEYWORDS,
        "title_content_keywords": [],
        "title_exclude_url": True,
        "url_content_keywords": XING_URL_KEYWORDS,
        "date_content_keywords": XING_DATE_KEYWORDS,
        "extra_columns": [],
        "drop_exact_value_rows": [],
        "date_parser": "xing",
        "use_german_filter": XING_USE_GERMAN_FILTER,
        "german_filter_temp_output_file": XING_APPLY_RECENT_TEMP_FILE,
        "final_output_template": XING_FINAL_RECENT_OUTPUT_TEMPLATE,
        "sort_columns": ["_date_age_days", "position"],
        "output_column_order": ["date", "position", "job_url"],
        "categorical_columns": [],
    },
}

GERMAN_REQUIRED_PATTERNS = [
    # Explicit CEFR / strict
    r"\b(?:c1|c2)[- ]?(?:niveau|level)?[- ]?(?:deutsch|german)\b",
    r"\b(?:deutsch|german)[- ]?(?:c1|c2)\b",
    r"\b(?:mindestens|at least|minimum|min\.?)\s*(?:c1|c2)\b.{0,30}\b(?:deutsch|german)\b",
    r"\b(?:deutsch|german)\b.{0,30}\b(?:mindestens|at least|minimum|min\.?)\s*(?:c1|c2)\b",
    r"\b(?:deutschkenntnisse|german language skills?)\b.{0,30}\b(?:c1|c2)\b",
    r"\b(?:c1|c2)\b.{0,30}\b(?:deutschkenntnisse|german language skills?)\b",
    # Fluent / business fluent / native-like
    r"\b(?:flie(?:ß|ss)end|verhandlungssicher|muttersprachlich)\b.{0,40}\bdeutsch\b",
    r"\bdeutsch\b.{0,40}\b(?:flie(?:ß|ss)end|verhandlungssicher|muttersprachlich)\b",
    r"\b(?:flie(?:ß|ss)ende|verhandlungssichere|muttersprachliche)\s+deutschkenntnisse\b",
    r"\bdeutschkenntnisse\b.{0,30}\b(?:flie(?:ß|ss)end|verhandlungssicher|muttersprachlich)\b",
    r"\b(?:fluent|business[- ]fluent|native(?:[- ]level)?|near[- ]native)\b.{0,30}\bgerman\b",
    r"\bgerman\b.{0,30}\b(?:fluent|business[- ]fluent|native(?:[- ]level)?|near[- ]native)\b",
    r"\b(?:fluent|business[- ]fluent|native(?:[- ]level)?|near[- ]native)\s+german(?:\s+skills?)?\b",
    r"sprichst\s+(flie[sß]end|sehr gut|gut)\s+deutsch",
    r"gut und sprichst\s+flie[sß]end\s+deutsch",
    # Parenthetical / colon format
    r"\bdeutsch\s*[:(]\s*(?:c1|c2|flie(?:ß|ss)end|verhandlungssicher|muttersprachlich|gut|sehr gut)\b",
    # "Sie/Du sprechen/beherrschen Deutsch"
    r"\b(?:sie\s+sprechen|du\s+sprichst|sie\s+beherrschen|du\s+beherrschst)\s+(?:(?:flie(?:ß|ss)end|gut|sehr gut|verhandlungssicher)\s+)?deutsch\b",
    r"\bbeherrschung\s+der\s+deutschen\s+sprache\b",
    # "Deutsch als Muttersprache" / Muttersprachenniveau
    r"\bdeutsch\s+als\s+muttersprache\b",
    r"\bdeutsch(?:kenntnisse)?\s+auf\s+muttersprachlichem?\s+niveau\b",
    # Patterns to detect explicit language lists like "Erforderliche Sprachen\nDeutsch"
    r"erforderliche sprachen[\s\S]{0,80}\bdeutsch\b",
    r"sprachkenntnisse[\s\S]{0,80}\bdeutsch\b",
    # Patterns to catch constructs like "Deutsch- und guten Englischkenntnisse"
    r"\bdeutsch(?:-|[ \-])?und[\s\S]{0,40}\benglisch(?:kenntnisse)?\b",
    # Broad / non-strict German wording
    r"\b(?:gut|gute|sehr gut|sehr gute|ausgezeichnet|ausgezeichnete|exzellent|exzellente|solide|fundiert|fundierte|sicher|sichere|kommunikationssicher|kommunikationssichere)\s+deutschkenntnisse\b",
    r"\bdeutschkenntnisse\b.{0,30}\b(?:gut|gute|sehr gut|sehr gute|ausgezeichnet|ausgezeichnete|exzellent|exzellente|solide|fundiert|fundierte|sicher|sichere|kommunikationssicher|kommunikationssichere)\b",
    r"\b(?:gut|gute|sehr gut|sehr gute)\s+deutsch\b",
    r"\bdeutsch\b.{0,20}\b(?:gut|gute|sehr gut|sehr gute)\b",
    r"\b(?:gut|gute|sehr gut|sehr gute|sicher|sichere|fundiert|fundierte)\s+kenntnisse\s+der\s+deutschen\s+sprache\b",
    r"\bkenntnisse\s+der\s+deutschen\s+sprache\b.{0,30}\b(?:gut|gute|sehr gut|sehr gute|sicher|sichere|fundiert|fundierte)\b",
    r"\b(?:gut|gute|sehr gut|sehr gute)\s+kenntnisse\s+in\s+deutsch\b",
    r"\bdeutschkenntnisse\s+auf\s+(?:gutem|sehr gutem|sicherem|professionellem)\s+niveau\b",
    # "Sprachkenntnisse in Deutsch"
    r"\b(?:gute|sehr gute|ausgezeichnete|flie(?:ß|ss)ende)\s+sprachkenntnisse\s+in\s+deutsch\b",
    r"\bsprachkenntnisse\b.{0,20}\bin\s+deutsch\b",
    # English broad wording
    r"\bgerman\s+language\s+skills\b",
    r"\bfluency\s+in\s+german\b",
    r"\b(?:good|very good|strong|excellent|solid)\s+german(?:\s+language)?\s+skills\b",
    r"\bgerman(?:\s+language)?\s+skills\b.{0,30}\b(?:good|very good|strong|excellent|solid)\b",
    r"\bproficient\s+in\s+german\b",
    r"\bprofessional(?:ly)?\s+proficient\s+in\s+german\b",
    r"\bstrong\s+command\s+of\s+german\b",
    r"\bgood\s+command\s+of\s+german\b",
    # Spoken / written German
    r"\bdeutsch\b.{0,20}\bin\s+wort\s+und\s+schrift\b",
    r"\bin\s+wort\s+und\s+schrift\b.{0,20}\bdeutsch\b",
    r"\bdeutschkenntnisse\b.{0,30}\bin\s+wort\s+und\s+schrift\b",
    r"\bin\s+wort\s+und\s+schrift\b.{0,30}\bdeutschkenntnisse\b",
    r"\b(?:gute|sehr gute|flie(?:ß|ss)ende|verhandlungssichere)\s+deutschkenntnisse\s+in\s+wort\s+und\s+schrift\b",
    r"\b(?:written\s+and\s+spoken|oral\s+and\s+written)\s+german\b",
    r"\b(?:good|very good|strong|excellent)\s+(?:written\s+and\s+spoken|oral\s+and\s+written)\s+german\b",
    r"\b(?:written\s+and\s+spoken|oral\s+and\s+written)\s+german\b.{0,20}\b(?:good|very good|strong|excellent)\b",
    # Required / mandatory wording
    r"\bgerman(?:\s+language)?\s+skills?\s+(?:is|are)?\s*(?:required|mandatory|must|essential|necessary)\b",
    r"\b(?:required|mandatory|must|essential|necessary)\b.{0,30}\bgerman(?:\s+language)?\s+skills?\b",
    r"\bdeutsch(?:kenntnisse)?\s+(?:sind\s+)?(?:zwingend|unbedingt\s+)?(?:erforderlich|vorausgesetzt|voraussetzung|notwendig|pflicht)\b",
    r"\b(?:zwingend|unbedingt)\b.{0,20}\bdeutsch(?:kenntnisse)?\b",
    r"\b(?:erforderlich|voraussetzung|notwendig|pflicht)\b.{0,30}\bdeutsch(?:kenntnisse)?\b",
    r"\bdeutsch(?:kenntnisse)?\b.{0,30}\b(?:erforderlich|voraussetzung|notwendig|pflicht)\b",
    # Work / company language
    r"\bdeutsch\s+als\s+(?:unternehmenssprache|arbeitssprache|firmensprache)\b",
    r"\b(?:arbeitssprache|unternehmenssprache|firmensprache)\s+(?:ist\s+)?deutsch\b",
    r"\bdeutsch\s+ist\s+die\s+(?:arbeitssprache|unternehmenssprache|firmensprache)\b",
    r"\b(?:team|kommunikation|kommunizieren|austausch|abstimmung)\b.{0,30}\bauf\s+deutsch\b",
    # "Deutschsprachig" in work-context nouns
    r"\bdeutschsprachig(?:e[nrms]?)?\s+(?:kommunikation|umfeld|team|umgebung|arbeitsumfeld)\b",
    # Common combined German + English phrasing
    r"\b(?:gute|sehr gute|flie(?:ß|ss)ende)\b.{0,20}\bdeutsch-?\s*und\s*englischkenntnisse\b",
    r"\b(?:gute|sehr gute|flie(?:ß|ss)ende)\b.{0,20}\benglisch-?\s*und\s*deutschkenntnisse\b",
    r"\bflie(?:ß|ss)ende\s+deutsch-?\s*und\s*(?:sehr\s+guten|guten|sehr\s+gute|gute)\s+englischkenntnisse\b",
    r"\b(?:good|very good|fluent)\s+german\s+and\s+english\b",
    r"\b(?:good|very good|fluent)\s+english\s+and\s+german\b",
]
