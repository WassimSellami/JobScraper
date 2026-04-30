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
    r"(flie[sß]end|verhandlungssicher|muttersprachlich).{0,40}deutsch",
    r"flie[sß]end deutsch",
    r"gute deutschkenntnisse",
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
    r"gute deutsch",
    r"deutsch als unternehmenssprache",
    r"deutsch(kenntnisse)? (auf )?(einem )?(professionell|gesch[äa]ftlich|verhandlungs)",
    r"(arbeitssprache|unternehmenssprache|firmensprache) (ist )?deutsch",
    r"deutsch (ist )?(die )?(arbeitssprache|unternehmenssprache|firmensprache)",
    r"(team|kommunikation|kommunizier).{0,30}auf deutsch",
    r"(gute|sehr gute).{0,20}deutsch-?\s*und\s*englischkenntnisse.{0,30}(in )?wort und schrift",
    r"(gute|sehr gute).{0,20}englisch-?\s*und\s*deutschkenntnisse.{0,30}(in )?wort und schrift",
]
