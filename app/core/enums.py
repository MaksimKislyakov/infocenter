from enum import Enum


class Role(str, Enum):
    INSPECTOR = "inspector"
    MASTER = "master"
    ENGINEER = "engineer"
    MANAGEMENT = "management"
    ADMIN = "admin"