from enum import Enum, StrEnum


class Role(str, Enum):
    INSPECTOR = "inspector"
    MASTER = "master"
    ENGINEER = "engineer"
    MANAGEMENT = "management"
    ADMIN = "admin"


class OrgLevel(StrEnum):
    ENTERPRISE = "enterprise"
    SHOP = "shop"
    AREA = "area"


class Block(StrEnum):
    SAFETY = "safety"
    QUALITY = "quality"
    PRODUCTION = "production"
    COSTS = "costs"
    CULTURE = "culture"
    ALL = "all" 


class Action(StrEnum):
    VIEW = "view"
    MANAGE = "manage"
    MANAGE_PERMISSIONS = "manage_permissions"