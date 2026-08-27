from fastapi import FastAPI

from app.api.v1.counterfactual_maintenance import router


def test_counterfactual_router_exposes_analysis_endpoint():
    paths = {
        getattr(route, "path", "")
        for route in router.routes
    }

    assert "/machines/{machine_id}/counterfactual-maintenance" in paths


def test_counterfactual_endpoint_is_present_in_openapi_schema():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    schema = app.openapi()

    assert (
        "/api/v1/machines/{machine_id}/counterfactual-maintenance"
        in schema["paths"]
    )
    operation = schema["paths"][
        "/api/v1/machines/{machine_id}/counterfactual-maintenance"
    ]
    assert "post" in operation
