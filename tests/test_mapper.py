import pytest
from bs4 import BeautifulSoup

from web_mapper.scrapers import Mapper, MapperURLInvalidError


@pytest.fixture
def mapper():
    return Mapper('https://www.google.com')


def test_mapper_init(mapper):
    expected_max_depth = 2
    expected_rate_limit = 0.5

    assert mapper.domain == 'https://www.google.com'
    assert mapper.max_depth == expected_max_depth
    assert mapper.rate_limit == expected_rate_limit
    assert mapper.visited == set()
    assert mapper.all_links == set()


def test_mapper_init_custom():
    domain = 'https://www.google.com'
    max_depth = 3
    rate_limit = 1

    mapper = Mapper(domain, max_depth, rate_limit)

    assert mapper.domain == domain
    assert mapper.max_depth == max_depth
    assert mapper.rate_limit == rate_limit
    assert mapper.visited == set()
    assert mapper.all_links == set()


def test_mapper_init_invalid_domain():
    with pytest.raises(MapperURLInvalidError) as exception:
        Mapper('google.com')

    assert str(exception.value) == 'URL fornecida não é válida.'


def test_mapper_get_page(mapper):
    url = 'https://www.google.com'
    page = mapper._get_page(url)

    assert page.title.string == 'Google'
    assert page.find('input', {'name': 'q'})


def test_mapper_get_page_invalid(mapper):
    url = 'https://www.google.com/invalid'
    page = mapper._get_page(url)

    assert isinstance(page, BeautifulSoup)


def test_mapper_find_links(mapper):
    url = 'https://www.google.com'
    page = mapper._get_page(url)
    links = mapper._find_links(page)

    assert links


def test_mapper_find_links_invalid(mapper):
    url = 'https://www.google.com/invalid'
    page = mapper._get_page(url)
    links = mapper._find_links(page)

    assert not links


def test_mapper_clean_links(mapper):
    links = ['/path/to/page', '/path/to/page/', '/path/to/page.html']
    cleaned_links = mapper._clean_links(links)

    assert len(cleaned_links) == len(links)


def test_mapper_clean_links_invalid(mapper):
    links = ['http://google.com', 'https://google.com', 'ftp://google.com']
    cleaned_links = mapper._clean_links(links)

    assert not cleaned_links


def test_mapper_is_valid_url(mapper):
    assert mapper._is_valid_url('https://www.google.com')
    assert mapper._is_valid_url('http://www.google.com')
    assert not mapper._is_valid_url('http://www.google.com/test.pdf')
    assert not mapper._is_valid_url('https://google.com')
    assert not mapper._is_valid_url('google.com')
    assert not mapper._is_valid_url('http://google')
    assert not mapper._is_valid_url('http://google.')
    assert not mapper._is_valid_url('http://google..')
    assert not mapper._is_valid_url('http://google.com.')


def test_mapper_rate_limit_wait(mapper):
    mapper._rate_limit_wait()
    assert True


def test_mapper_crawl(mapper):
    url = 'https://www.google.com'
    depth = 0

    mapper.crawl(url, depth)

    assert mapper.visited
    assert mapper.all_links
    assert len(mapper.visited) != len(mapper.all_links)


def test_mapper_map_web_site(mapper):
    mapped_links = mapper.map_web_site()

    assert mapped_links
    assert len(mapped_links) == len(mapper.all_links)
    assert all(link in mapper.all_links for link in mapped_links)
    assert all(link in mapped_links for link in mapper.all_links)
