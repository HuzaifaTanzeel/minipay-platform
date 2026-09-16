"""jsonschema dicts for payment create/get and the MiniPay error envelope."""

PAYMENT = {
    "type": "object",
    "required": [
        "id",
        "transaction_ref",
        "customer_ref",
        "amount",
        "status",
        "created_at",
    ],
    "properties": {
        "id": {"type": "integer"},
        "transaction_ref": {"type": "string"},
        "customer_ref": {"type": "string"},
        "amount": {"type": ["number", "string"]},
        "status": {"type": "string"},
        "created_at": {"type": "string"},
    },
}

ERROR_ENVELOPE = {
    "type": "object",
    "required": ["error"],
    "properties": {
        "error": {
            "type": "object",
            "required": ["code", "message", "request_id"],
            "properties": {
                "code": {"type": "string"},
                "message": {"type": "string"},
                "request_id": {"type": "string"},
            },
        }
    },
}
