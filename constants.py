INPUT_FILE = "stepstone.csv"
FULL_OUTPUT_FILE = "stepstone_cleaned_filtered_full.csv"
RECENT_OUTPUT_FILE = "stepstone_cleaned_filtered_recent.csv"

GERMAN_FILTER_FULL_INPUT_CSV = FULL_OUTPUT_FILE
GERMAN_FILTER_RECENT_INPUT_CSV = RECENT_OUTPUT_FILE
GERMAN_FILTER_FULL_OUTPUT_CSV = "stepstone_apply_full.csv"
GERMAN_FILTER_RECENT_OUTPUT_CSV = "stepstone_apply_recent.csv"

GERMAN_FILTER_REQUEST_DELAY = 2

LAST_DAYS = 2

POSITION_EXCLUSION_TERMS = [
    "Senior",
    "Lead",
    "Professor",
    "Projektleiter",
    "Manager",
    "ERP",
    "Defence",
    "Architect",
]

DEUTSCH_VALUE = "Deutsch"


GERMAN_REQUIRED_PATTERNS = [
    r"(flie[sß]end|verhandlungssicher|muttersprachlich).{0,40}deutsch",
    r"deutsch.{0,40}(flie[sß]end|verhandlungssicher|muttersprachlich)",
    r"\b(c1|c2)[- ]deutsch",
    r"deutsch[- ](c1|c2)",
    r"mindestens (c1|c2).{0,30}deutsch",
    r"deutsch.{0,30}mindestens (c1|c2)",
    r"german (language )?(skills? )?(is |are )?(required|mandatory|must|essential)",
    r"(required|mandatory|must|essential).{0,30}german (language )?skills?",
    r"deutsch(kenntnisse)? (sind )?(zwingend |unbedingt )?(erforderlich|vorausgesetzt|voraussetzung|notwendig|pflicht)",
    r"(zwingend|unbedingt).{0,20}deutsch",
    r"(erforderlich|voraussetzung|notwendig).{0,30}deutsch",
    r"deutsch.{0,30}(erforderlich|voraussetzung|notwendig|pflicht)",
    r"(sehr gut|ausgezeichnet|exzellent).{0,20}deutsch",
    r"deutsch.{0,20}(sehr gut|ausgezeichnet|exzellent)",
    r"deutsch(kenntnisse)? (auf )?(einem )?(professionell|gesch[äa]ftlich|verhandlungs)",
    r"(arbeitssprache|unternehmenssprache|firmensprache) (ist )?deutsch",
    r"deutsch (ist )?(die )?(arbeitssprache|unternehmenssprache|firmensprache)",
    r"(team|kommunikation|kommunizier).{0,30}auf deutsch",
    r"(gute|sehr gute).{0,20}deutsch-?\s*und\s*englischkenntnisse.{0,30}(in )?wort und schrift",
    r"(gute|sehr gute).{0,20}englisch-?\s*und\s*deutschkenntnisse.{0,30}(in )?wort und schrift",
]
