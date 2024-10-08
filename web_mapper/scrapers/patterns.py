from re import compile

DOMAIN_PATTERN = compile(
    r'https?://(?:www\.)?[-a-zA-Z0-9]{1,63}(?:\.[a-zA-Z]{2,6})+/?'
)
LINK_PATTERN = compile(r'^/')
