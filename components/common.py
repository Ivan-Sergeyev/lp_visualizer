from typing import Literal


type StorageType = Literal['local', 'session', 'memory'] | None

STORAGE_TYPE: StorageType = 'memory'
