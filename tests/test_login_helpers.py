from datetime import datetime, timedelta, timezone

from app import app, get_client_ip, is_blocked, increment_failure, reset_block


def test_get_client_ip():
    with app.test_request_context('/', environ_overrides={'REMOTE_ADDR': '203.0.113.5'}):
        assert get_client_ip() == '203.0.113.5'


def test_block_helpers():
    now = datetime.now(timezone.utc)
    blocked = type('B', (), {'intentos': 5, 'bloqueado_hasta': now + timedelta(minutes=10)})
    expired = type('B', (), {'intentos': 3, 'bloqueado_hasta': now - timedelta(minutes=10)})

    assert is_blocked(blocked) is True
    assert is_blocked(expired) is False

    increment_failure(expired)
    assert expired.intentos == 4
    assert expired.bloqueado_hasta == now - timedelta(minutes=10)

    reset_block(blocked)
    assert blocked.intentos == 0
    assert blocked.bloqueado_hasta is None


if __name__ == '__main__':
    test_get_client_ip()
    test_block_helpers()
    print('helper tests passed')
