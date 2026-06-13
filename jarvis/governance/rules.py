import re

TIER1_PATTERNS: list[re.Pattern] = [
    re.compile(r'^(who|what)\s+(are\s+)?you', re.IGNORECASE),
    re.compile(r'^(hello|hi|hey|greetings|good\s+(morning|afternoon|evening))', re.IGNORECASE),
    re.compile(r'^(how\s+are\s+you|how\'?re?\s+you|how\s+do\s+you\s+do)', re.IGNORECASE),
    re.compile(r'^(what\s+(can|do)\s+you\s+(do|help))', re.IGNORECASE),
    re.compile(r'^(thanks|thank\s+you|ty)', re.IGNORECASE),
    re.compile(r'^(yes|no|ok|okay|sure|fine|good)', re.IGNORECASE),
    re.compile(r'^(bye|goodbye|see\s+you|talk\s+later)', re.IGNORECASE),
    re.compile(r'^(what(\'s|\sis)\s+(my|the)\s+goal)', re.IGNORECASE),
    re.compile(r'^(what(\'s|\sis)\s+(my|the|our)\s+)?(plan|progress|status|current)', re.IGNORECASE),
    re.compile(r'^(tell|show)\s+me\s+(about|my|the)', re.IGNORECASE),
]

TIER3_PATTERNS: list[re.Pattern] = [
    re.compile(r'modify\s+(own\s+)?identity', re.IGNORECASE),
    re.compile(r'(delete|remove|alter|change)\s+(own\s+)?identity\.yaml', re.IGNORECASE),
    re.compile(r'(delete|remove|alter|change)\s+genesis\.md', re.IGNORECASE),
    re.compile(r'(delete|remove|alter|change)\s+personality\.yaml', re.IGNORECASE),
    re.compile(r'(delete|remove|alter|change)\s+soul\.yaml', re.IGNORECASE),
    re.compile(r'rewrite\s+personality', re.IGNORECASE),
    re.compile(r'rewrite\s+soul', re.IGNORECASE),
    re.compile(r'rewrite\s+identity', re.IGNORECASE),
    re.compile(r'rewrite\s+genesis', re.IGNORECASE),
    re.compile(r'ignore.*(constitution|rule\s+CR_\d+|safety.rule)', re.IGNORECASE),
    re.compile(r'(remove|delete|overwrite|empty)\s+safety_rules', re.IGNORECASE),
    re.compile(r'claim.*human|pretend.*(human|to\s+be)', re.IGNORECASE),
    re.compile(r'act\s+as\s+(a\s+)?human', re.IGNORECASE),
    re.compile(r'autonomous\s+copy|self.?replicat', re.IGNORECASE),
    re.compile(r'how\s+to\s+(make|build)\s+(a\s+)?(bomb|weapon|explosive)', re.IGNORECASE),
    re.compile(r'denial.?of.?service', re.IGNORECASE),
    re.compile(r'fabricate\s+(memory|knowledge)', re.IGNORECASE),
    re.compile(r'delete\s+memory', re.IGNORECASE),
    re.compile(r'grant.*(new\s+)?(permission|admin|root)\s+access', re.IGNORECASE),
]

TIER2_PATTERNS: list[re.Pattern] = [
    re.compile(r'(create|make)\s+(?:(?:a|the)\s+)?(?:new\s+)?(?:folder|directory)', re.IGNORECASE),
    re.compile(r'(delete|remove)\s+(?:(?:the|a)\s+)?(?:file|files|backup|log)', re.IGNORECASE),
    re.compile(r'execute\s+(?:this\s+|the\s+)?(?:python\s+)?code', re.IGNORECASE),
    re.compile(r'run\s+(?:a\s+)?(?:system\s+)?(?:check|command|script)', re.IGNORECASE),
    re.compile(r'install\s+(?:(?:the|a)\s+)?(?:python\s+)?(?:library|package|tool)', re.IGNORECASE),
    re.compile(r'shut\s+down\s+(the\s+)?server', re.IGNORECASE),
    re.compile(r'read\s+the\s+contents\s+of\s+(the\s+)?file', re.IGNORECASE),
    re.compile(r'modify\s+(the\s+)?configuration', re.IGNORECASE),
    re.compile(r'write\s+(a\s+)?script', re.IGNORECASE),
    re.compile(r'open\s+(port|connection|network)', re.IGNORECASE),
    re.compile(r'kill\s+(process|task)', re.IGNORECASE),
    re.compile(r'format\s+(drive|disk)', re.IGNORECASE),
]
