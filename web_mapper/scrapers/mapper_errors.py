class MapperErros(Exception):
    """
    Classe base para exceções em Mapper.
    """

    pass


class MapperURLInvalidError(MapperErros):
    """
    Exceção para URL inválida.
    """

    def __init__(self):
        super().__init__('URL fornecida não é válida.')
