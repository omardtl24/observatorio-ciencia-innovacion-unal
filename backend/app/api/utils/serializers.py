"""Serializer utilities for converting models to dictionaries for API responses."""


def serialize_user(user):
    """Serialize a user object with their roles.
    
    Args:
        user: The user object with roles relationship.
    
    Returns:
        dict: User data with email, names, last_names, and roles.
    """
    return {
        "email": user.email,
        "names": user.names,
        "last_names": user.last_names,
        "roles": [
            {
                "id": role.id,
                "name": role.name,
            }
            for role in getattr(user, "roles", [])
        ],
    }


def serialize_resource_with_roles(resource):
    """Serialize a resource object with its roles.
    
    Args:
        resource: The resource object (visor, report, simulator, etc) with roles relationship.
    
    Returns:
        dict: Resource data with roles as a list of role names.
    """
    payload = resource.to_dict()
    payload["roles"] = [role.name for role in getattr(resource, "roles", [])]
    return payload


def serialize_data_source(data_source):
    """Serialize a data source object with all related IDs.
    
    Args:
        data_source: The data source object with role, report, visor, and simulator relationships.
    
    Returns:
        dict: Data source data with role_ids, report_ids, visor_ids, and simulator_ids.
    """
    payload = data_source.to_dict(include=["id", "name", "description", "file_id", "updated_at"])
    payload["role_ids"] = [role.id for role in getattr(data_source, "roles", [])]
    payload["report_ids"] = [report.id for report in getattr(data_source, "reports", [])]
    payload["visor_ids"] = [visor.id for visor in getattr(data_source, "visors", [])]
    payload["simulator_ids"] = [simulator.id for simulator in getattr(data_source, "simulators", [])]
    payload["file_history"] = [
        {
            "file_id": version.file_id,
            "published_at": version.published_at.isoformat() if version.published_at else None,
        }
        for version in getattr(data_source, "file_versions", [])
    ]
    return payload
