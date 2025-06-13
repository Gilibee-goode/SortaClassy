import pytest
from src.utils.class_creator import create_classes

def test_create_classes():
    """Test that the class creator correctly creates the specified number of Class objects."""
    classes = create_classes(num_classes=3)
    
    # Verify the number of classes created
    assert len(classes) == 3
    
    # Verify the properties of each class
    for i, class_ in enumerate(classes, 1):
        assert class_.id == i
        assert class_.name == f"Class {i}"
        assert class_.max_size == 30
        assert len(class_.students) == 0 