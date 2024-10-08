"""
Este módulo contém a classe Mapper, responsável por mapear páginas web a
partir de um domínio fornecido.

O mapeamento é realizado de forma recursiva, identificando e seguindo links
até uma profundidade máxima especificada.
A classe utiliza BeautifulSoup para fazer parsing do conteúdo HTML e Rich
para logar o progresso das requisições.

Classes
-------
Mapper
    Classe que realiza o mapeamento de URLs a partir de um domínio fornecido.
"""

from time import sleep
from typing import List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from rich.console import Console

from web_mapper.scrapers.mapper_errors import MapperURLInvalidError
from web_mapper.scrapers.patterns import DOMAIN_PATTERN, LINK_PATTERN

console = Console()


class Mapper:
    """
    Classe responsável por mapear páginas web a partir do domínio fornecido.
    Pode realizar mapeamento recursivo até uma profundidade
    máxima especificada.

    Attributes
    ----------
    domain : str
        Domínio base para mapeamento.
    max_depth : int
        Profundidade máxima de mapeamento.
    rate_limit : float
        Limite de requisições por segundo.
    visited : set of str
        Conjunto de URLs visitadas.
    all_links : set of str
        Conjunto de todas as URLs encontradas.

    Methods
    -------
    crawl(url: str, depth: int) -> None
        Realiza o mapeamento recursivo de URLs a partir da URL fornecida.
    map_web_site() -> List[str]
        Inicia o mapeamento do site e retorna a lista de URLs encontradas.

    Raises
    ------
    MapperURLInvalidError
        Se a URL fornecida não for válida.
    """

    def __init__(
        self, domain: str, max_depth: int = 2, rate_limit: float = 0.5
    ) -> None:
        """
        Inicializa a classe Mapper com o domínio,
        profundidade máxima e rate limit.

        Parameters
        ----------
        domain : str
            Domínio base para mapeamento.
        max_depth : int, optional
            Profundidade máxima de mapeamento, por padrão 2.
        rate_limit : float, optional
            Limite de requisições por segundo, por padrão 0.5.

        Raises
        ------
        MapperURLInvalidError
            Se a URL fornecida não for válida.
        """
        match = DOMAIN_PATTERN.findall(domain)

        if not match:
            raise MapperURLInvalidError()

        self.domain = match[0].strip('/')
        self.max_depth = max_depth
        self.rate_limit = rate_limit
        self.visited: Set[str] = set()
        self.all_links: Set[str] = set()

    @classmethod
    def _get_page(cls, url: str) -> BeautifulSoup:
        """
        Realiza uma requisição GET para a URL fornecida e
        retorna um objeto BeautifulSoup.

        Parameters
        ----------
        url : str
            URL para acessar.

        Returns
        -------
        BeautifulSoup
            Objeto BeautifulSoup com o conteúdo HTML da página ou
            uma página vazia se ocorrer um erro.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
        except RequestException as e:
            console.print(f'[red]Erro ao acessar {url}:[/red] {str(e)}')
            return BeautifulSoup('', 'html.parser')

        return BeautifulSoup(response.text, 'html.parser')

    @classmethod
    def _find_links(cls, soup: BeautifulSoup) -> List[str]:
        """
        Encontra todos os links em uma página HTML.

        Parameters
        ----------
        soup : BeautifulSoup
            Objeto BeautifulSoup da página.

        Returns
        -------
        List[str]
            Lista com os links encontrados na página.
        """
        return [link.get('href') for link in soup.find_all('a', href=True)]

    @classmethod
    def _clean_links(cls, links: List[str]) -> List[str]:
        """
        Limpa a lista de links, removendo links inválidos.

        Parameters
        ----------
        links : List[str]
            Lista de links.

        Returns
        -------
        List[str]
            Lista de links válidos.
        """
        cleaned = {link for link in links if link and LINK_PATTERN.match(link)}
        return list(cleaned)

    def _is_valid_url(self, url: str) -> bool:
        """
        Verifica se a URL fornecida é válida para o mapeamento.

        Parameters
        ----------
        url : str
            URL para verificar.

        Returns
        -------
        bool
            True se a URL for válida para o mapeamento, False caso contrário.
        """
        parsed_url = urlparse(url)
        domain_parsed = urlparse(self.domain)

        if parsed_url.netloc != domain_parsed.netloc:
            return False

        if any(parsed_url.path.endswith(ext) for ext in [
            '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg'
            ]
        ):
            return False

        return True

    def _rate_limit_wait(self) -> None:
        """
        Aguarda o tempo de espera do rate limit.
        """
        sleep(self.rate_limit)

    def crawl(self, url: str, depth: int) -> None:
        """
        Realiza o mapeamento recursivo de URLs a partir da URL fornecida.

        Parameters
        ----------
        url : str
            URL para iniciar o mapeamento.
        depth : int
            Profundidade atual do mapeamento.
        """
        if depth > self.max_depth:
            return
        if url in self.visited:
            return

        self.visited.add(url)
        console.log(f'Visitando: [blue]{url}[/blue]')

        html = self._get_page(url)
        links = self._find_links(html)
        clean_links = self._clean_links(links)

        for link in clean_links:
            absolute_url = urljoin(self.domain, link)
            if (self._is_valid_url(absolute_url)
                and absolute_url not in self.visited):
                self.all_links.add(absolute_url)
                self.crawl(absolute_url, depth + 1)
                self._rate_limit_wait()

    def map_web_site(self) -> List[str]:
        """
        Inicia o mapeamento do site a partir do domínio base.

        Returns
        -------
        List[str]
            Lista de URLs mapeadas no site.
        """
        self.crawl(self.domain, 0)
        return sorted(self.all_links)
