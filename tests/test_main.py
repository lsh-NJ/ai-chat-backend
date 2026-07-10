from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# 检查后端是否运行
def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# 检查是否正常拒绝空消息并返回正确的错误状态
def test_chat_rejects_blank_message() -> None:
    response = client.post(
        "/chat",
        json={
            "message": "   ",
        },
    )

    assert response.status_code == 422

# 检查是否能正常拒绝不存在的消息并返回正确的错误状态
def test_messages_reject_unknown_conversation() -> None:
    response = client.get(
        "/conversations/999999/messages"
    )

    assert response.status_code == 404