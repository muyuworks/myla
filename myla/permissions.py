

def check(resource_type, resource_id, org_id, project_id, owner_id, user_id, orgs, permission) -> bool:

    role = None
    for org_id in orgs:
        role = orgs[org_id].role

    if permission == "read":
        if role == "reader" or role == "owner":
            return True
    elif permission == "write":
        if role == "owner":
            return True

    return False
