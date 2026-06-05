from enum import Enum, StrEnum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class OrgLevel(StrEnum):
    ENTERPRISE = "enterprise"
    SHOP = "shop"
    AREA = "area"


class Block(StrEnum):
    SAFETY = "safety" #Безопасность
    QUALITY = "quality" #Качество
    PRODUCTION = "production" #Производство / Исполнение заказов
    ECONOMY = "economy" #Экономика и затраты
    CULTURE = "culture" #Корпоративная культура
    ALL = "all"


class Action(StrEnum):
    VIEW = "view"
    MANAGE = "manage"
