from coldwing.core.scope import validate_scope


def test_scope_enforcement_missing_target():
    try:
        validate_scope({"allow_active_scan": True, "tenant_id": "t1"})
    except ValueError:
        assert True
    else:
        assert False
