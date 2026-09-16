"""Customer create: success, duplicate, missing field."""


def test_create_customer_201(api, uniq):
    """successful requests — POST /api/customers."""
    ref = "CUST" + uniq[1:]
    r = api.request("POST", "/api/customers", json={"customer_ref": ref, "name": "Ada"})
    assert r.status_code == 201
    body = r.json()
    assert body["customer_ref"] == ref
    assert body["name"] == "Ada"
    assert "id" in body


def test_create_customer_duplicate_409(api, uniq):
    """invalid/missing fields / duplicate resource — second create is 409."""
    ref = "CUST" + uniq[1:]
    payload = {"customer_ref": ref, "name": "Ada"}
    first = api.request("POST", "/api/customers", json=payload)
    assert first.status_code == 201
    second = api.request("POST", "/api/customers", json=payload)
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "CUSTOMER_EXISTS"


def test_create_customer_missing_name_422(api, uniq):
    """invalid/missing fields — name required."""
    r = api.request("POST", "/api/customers", json={"customer_ref": "CUST" + uniq[1:]})
    assert r.status_code == 422
