from enum import Enum, StrEnum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class OrgLevel(StrEnum):
    ENTERPRISE = "enterprise"
    SHOP = "shop"
    AREA = "area"


class Block(StrEnum):
    SAFETY = "safety"
    QUALITY = "quality"
    PRODUCTION = "production"
    ECONOMY = "economy"
    CULTURE = "culture"
    ALL = "all"


class Action(StrEnum):
    VIEW = "view"
    MANAGE = "manage"
