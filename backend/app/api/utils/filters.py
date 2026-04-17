"""Filter utilities for common filtering operations."""


def filter_exclude_admin(items, field_name="name", admin_name="Administrador"):
    """Filter out admin role from a list of roles or items.
    
    Args:
        items (list): List of items to filter.
        field_name (str): Field name to check for admin name (default: 'name').
        admin_name (str): Admin role name to exclude (default: 'Administrador').
    
    Returns:
        list: Filtered list without admin items.
    """
    return [item for item in items if item.get(field_name) != admin_name]
