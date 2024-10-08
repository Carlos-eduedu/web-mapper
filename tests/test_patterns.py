from web_mapper.scrapers import DOMAIN_PATTERN, LINK_PATTERN


def test_domain_pattern():
    assert DOMAIN_PATTERN.findall('https://www.google.com') == [
        'https://www.google.com'
    ]
    assert DOMAIN_PATTERN.findall('http://www.google.com') == [
        'http://www.google.com'
    ]
    assert DOMAIN_PATTERN.findall('https://google.com') == [
        'https://google.com'
    ]


def test_domain_pattern_invalid():
    assert DOMAIN_PATTERN.findall('google.com') == []
    assert DOMAIN_PATTERN.findall('http://google') == []
    assert DOMAIN_PATTERN.findall('http://google.') == []
    assert DOMAIN_PATTERN.findall('http://google..') == []
    assert DOMAIN_PATTERN.findall('http://google.com.')


def test_link_pattern():
    assert LINK_PATTERN.match('/path/to/page')
    assert LINK_PATTERN.match('/path/to/page/')
    assert LINK_PATTERN.match('/path/to/page.html')


def test_link_pattern_invalid():
    assert not LINK_PATTERN.match('http://google.com')
    assert not LINK_PATTERN.match('https://google.com')
    assert not LINK_PATTERN.match('ftp://google.com')
