# Testing Rules

> **Priority**: HIGH — Enforced before merge

---

## Test-Driven Development

- **WRITE** tests before implementation (Red → Green → Refactor)
- **80%** minimum coverage required for new code
- **NEVER** merge code that breaks existing tests

---

## Test Types

| Type        | Required       | Coverage                | Framework                         |
| :---------- | :------------- | :---------------------- | :-------------------------------- |
| Unit        | MANDATORY      | All service logic       | pytest (backend), Jest (frontend) |
| Integration | MANDATORY      | API endpoints           | pytest + httpx / supertest        |
| E2E         | Critical flows | Auth, onboarding, core  | Playwright                        |

---

## Backend Testing (Python — pytest)

### Conventions

- File naming: `test_<module>.py`
- Function naming: `test_<action>_<expected_result>()`
- Use `@pytest.fixture` for reusable test data
- Use `TestClient` from `httpx` for API endpoint testing
- Mock external services (AI providers, third-party APIs) with `unittest.mock`
- Each test file: `client` and `auth_headers` fixtures from `conftest.py`

### Example Pattern

```python
def test_create_resource_success(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    """Test successful resource creation."""
    response = client.post(
        "/api/v1/resources",
        json={"name": "test_resource", "metadata": {}},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_resource"
```

---

## Frontend Testing (TypeScript — Jest/Vitest)

### Naming Convention

```typescript
describe("[Component]", () => {
  describe("[method]", () => {
    it("should [expected behavior]", () => {
      // Given / When / Then
    });
  });
});
```

---

## Test Quality

| Principle     | Rule                                   |
| :------------ | :------------------------------------- |
| Independent   | Tests don't depend on each other       |
| Deterministic | Same result every run — no random data |
| Fast          | Unit tests < 100ms each               |
| Isolated      | External services always mocked        |
| Readable      | Test name describes the scenario       |
