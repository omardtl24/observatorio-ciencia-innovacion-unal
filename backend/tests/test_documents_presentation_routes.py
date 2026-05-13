import pytest # type: ignore

def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_get_all_and_get_by_id_unauthorized(monkeypatch, app):
    from app.api import documents_presentation_routes

    monkeypatch.setattr('app.api.documents_presentation_routes.DocumentPresentationService.get_all', lambda: [])
    f = _unwrap(documents_presentation_routes.get_documents_presentations)
    with app.test_request_context('/fake'):
        resp, code = f()
        assert code == 200

    monkeypatch.setattr('app.api.documents_presentation_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.documents_presentation_routes.AccessChecker.check_access', lambda u, i, t: False)
    f2 = _unwrap(documents_presentation_routes.get_document_presentation_by_id)
    with pytest.raises(Exception):
        with app.test_request_context('/fake'):
            f2(1)
