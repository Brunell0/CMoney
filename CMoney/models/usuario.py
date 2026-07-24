class Usuario:
    def __init__(self, username: str, password: str, perfil: str):
        self.__username = username
        self.__password = password
        self.__perfil = perfil

    # Getters
    @property
    def username(self) -> str:
        return self.__username

    @property
    def password(self) -> str:
        return self.__password

    @property
    def perfil(self) -> str:
        return self.__perfil

    def to_dict(self) -> dict:
        return {
            "senha": self.__password,
            "perfil": self.__perfil
        }