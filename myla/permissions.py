#from ._logging import logger


def check(resource_type, resource_id, org_id, project_id, owner_id, user_id, orgs, permission) -> bool:
    #logger.debug(f"Checking permission {permission} for {resource_type} {resource_id} in org {org_id} and project {project_id}, orgs={orgs}")

    role = None
    if org_id in orgs:
        role = orgs[org_id].role

    if permission == "read":
        if role == "reader" or role == "owner":
            return True
    elif permission == "write":
        if role == "owner":
            return True

    return False
