PROCESS_GLASSDOOR = False
PROCESS_STEPSTONE = False
PROCESS_XING = True


INPUT_FILE = "input/stepstone.csv"
FULL_OUTPUT_FILE = "stepstone_cleaned_full.csv"
RECENT_OUTPUT_FILE = "stepstone_cleaned_recent.csv"

XING_INPUT_FILE = "input/xing.csv"
XING_FULL_OUTPUT_FILE = "xing_cleaned_full.csv"
XING_RECENT_OUTPUT_FILE = "xing_cleaned_recent.csv"
XING_GERMAN_FILTER_FULL_OUTPUT_CSV = "xing_apply_full.csv"
XING_GERMAN_FILTER_RECENT_OUTPUT_CSV = "xing_apply_recent.csv"

GERMAN_FILTER_FULL_INPUT_CSV = FULL_OUTPUT_FILE
GERMAN_FILTER_RECENT_INPUT_CSV = RECENT_OUTPUT_FILE
GERMAN_FILTER_FULL_OUTPUT_CSV = "stepstone_apply_full.csv"
GERMAN_FILTER_RECENT_OUTPUT_CSV = "stepstone_apply_recent.csv"

GLASSDOOR_INPUT_FILE = "input/glassdoor.csv"
GLASSDOOR_RECENT_OUTPUT_FILE = "glassdoor_cleaned_recent.csv"
GLASSDOOR_GERMAN_FILTER_RECENT_OUTPUT_CSV = "glassdoor_apply_recent.csv"

GERMAN_FILTER_REQUEST_DELAY = 0.2

LAST_DAYS = 7

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
]

DEUTSCH_VALUE = "Deutsch"

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
    # Broad / non-strict German wording
    r"\b(?:gut|gute|sehr gut|sehr gute|ausgezeichnet|ausgezeichnete|exzellent|exzellente|solide|fundiert|fundierte|sicher|sichere|kommunikationssicher|kommunikationssichere)\s+deutschkenntnisse\b",
    r"\bdeutschkenntnisse\b.{0,30}\b(?:gut|gute|sehr gut|sehr gute|ausgezeichnet|ausgezeichnete|exzellent|exzellente|solide|fundiert|fundierte|sicher|sichere|kommunikationssicher|kommunikationssichere)\b",
    r"\b(?:gut|gute|sehr gut|sehr gute)\s+deutsch\b",
    r"\bdeutsch\b.{0,20}\b(?:gut|gute|sehr gut|sehr gute)\b",
    r"\b(?:gut|gute|sehr gut|sehr gute|sicher|sichere|fundiert|fundierte)\s+kenntnisse\s+der\s+deutschen\s+sprache\b",
    r"\bkenntnisse\s+der\s+deutschen\s+sprache\b.{0,30}\b(?:gut|gute|sehr gut|sehr gute|sicher|sichere|fundiert|fundierte)\b",
    r"\b(?:gut|gute|sehr gut|sehr gute)\s+kenntnisse\s+in\s+deutsch\b",
    r"\bdeutschkenntnisse\s+auf\s+(?:gutem|sehr gutem|sicherem|professionellem)\s+niveau\b",
    # English broad wording
    r"\b(?:good|very good|strong|excellent|solid)\s+german(?:\s+language)?\s+skills\b",
    r"\bgerman(?:\s+language)?\s+skills\b.{0,30}\b(?:good|very good|strong|excellent|solid)\b",
    r"\bproficient\s+in\s+german\b",
    r"\bprofessional(?:ly)?\s+proficient\s+in\s+german\b",
    r"\bstrong\s+command\s+of\s+german\b",
    r"\bgood\s+command\s+of\s+german\b",
    # Spoken / written German
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
    # Common combined German + English phrasing
    r"\b(?:gute|sehr gute|flie(?:ß|ss)ende)\b.{0,20}\bdeutsch-?\s*und\s*englischkenntnisse\b",
    r"\b(?:gute|sehr gute|flie(?:ß|ss)ende)\b.{0,20}\benglisch-?\s*und\s*deutschkenntnisse\b",
    r"\b(?:good|very good|fluent)\s+german\s+and\s+english\b",
    r"\b(?:good|very good|fluent)\s+english\s+and\s+german\b",
]
