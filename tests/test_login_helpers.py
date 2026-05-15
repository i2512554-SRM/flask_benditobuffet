from datetime import datetime, timedelta, timezone

from app import app, get_client_ip, is_blocked, increment_failure, reset_block


def test_get_client_ip():
    with app.test_request_context('/', environ_overrides={'REMOTE_ADDR': '203.0.113.5'}):
        assert get_client_ip() == '203.0.113.5'


def test_block_helpers():
    now = datetime.now(timezone.utc)
    blocked = type('B', (), {'intentos': 5, 'bloqueado_hasta': now + timedelta(minutes=10), 'tipo': 'usuario'})
    expired = type('B', (), {'intentos': 3, 'bloqueado_hasta': now - timedelta(minutes=10), 'tipo': 'usuario'})
    user_block = type('B', (), {'intentos': 4, 'bloqueado_hasta': now - timedelta(minutes=10), 'tipo': 'usuario'})
    ip_block = type('B', (), {'intentos': 9, 'bloqueado_hasta': now - timedelta(minutes=10), 'tipo': 'ip'})

    assert is_blocked(blocked) is True
    assert is_blocked(expired) is False

    increment_failure(expired)
    assert expired.intentos == 4
    assert expired.bloqueado_hasta == now - timedelta(minutes=10)

    increment_failure(user_block)
    assert user_block.intentos == 5
    assert user_block.bloqueado_hasta > now

    increment_failure(ip_block)
    assert ip_block.intentos == 10
    assert ip_block.bloqueado_hasta > now

    reset_block(blocked)
    assert blocked.intentos == 0
    assert blocked.bloqueado_hasta is None


if __name__ == '__main__':
    test_get_client_ip()
    test_block_helpers()
    print('helper tests passed')
