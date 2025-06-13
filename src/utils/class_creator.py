from typing import List
from src.models.class_ import Class

def create_classes(num_classes: int = 3) -> List[Class]:
    """Create a specified number of Class objects."""
    return [Class(id=i, name=f"Class {i}", max_size=30) for i in range(1, num_classes + 1)] 