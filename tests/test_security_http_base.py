from fastapi import FastAPI, Security
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBase
from fastapi.testclient import TestClient

app = FastAPI()

security = HTTPBase(scheme="Other")


@app.get("/users/me")
def read_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    return {"scheme": credentials.scheme, "credentials": credentials.credentials}


client = TestClient(app)


def test_security_http_base():
    response = client.get("/users/me", headers={"Authorization": "Other foobar"})
    assert response.status_code == 200, response.text
    assert response.json() == {"scheme": "Other", "credentials": "foobar"}


def test_security_http_base_no_credentials():
    response = client.get("/users/me")
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["WWW-Authenticate"] == "Other"


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "openapi": "3.1.0",
        "info": {"title": "FastAPI", "version": "0.1.0"},
        "paths": {
            "/users/me": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {"application/json": {"schema": {}}},
                        }
                    },
                    "summary": "Read Current User",
                    "operationId": "read_current_user_users_me_get",
                    "security": [{"HTTPBase": []}],
                }
            }
        },
        "components": {
            "securitySchemes": {"HTTPBase": {"type": "http", "scheme": "Other"}}
        },
    }
