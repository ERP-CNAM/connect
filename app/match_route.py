def match_route(template: str, path: str) -> bool:
    """
    Match a route with the template ignoring wildcard values and query params.

    Args:
        template: The template URL (/user/{id})
        path: The URL to check (/user/1?info)

    Returns:
        True if route match the template, False otherwise.
    """

    # Ignore query params
    template = template.split("?", 1)[0]
    path = path.split("?", 1)[0]

    t_parts = template.strip("/").split("/")
    p_parts = path.strip("/").split("/")

    if len(t_parts) != len(p_parts):
        return False

    for t, p in zip(t_parts, p_parts):
        if t.startswith("{") and t.endswith("}"):
            # Wildcard
            continue
        if t != p:
            return False

    return True
