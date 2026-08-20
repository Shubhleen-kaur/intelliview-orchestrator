import pytest

from notifier import ConsoleNotifier, Notifier, TransientNotificationError


def test_notifier_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        Notifier()


def test_console_notifier_delivers_message(capsys):
    notifier = ConsoleNotifier()

    notifier.deliver("alex@gmail.com", "Hello Alex")

    output = capsys.readouterr().out

    assert "alex@gmail.com" in output
    assert "Hello Alex" in output


def test_console_notifier_rejects_empty_recipient():
    notifier = ConsoleNotifier()

    with pytest.raises(ValueError, match="Recipient cannot be empty"):
        notifier.deliver("", "Hello Alex")


def test_console_notifier_rejects_empty_message():
    notifier = ConsoleNotifier()

    with pytest.raises(ValueError, match="Message cannot be empty"):
        notifier.deliver("alex@gmail.com", "")


def test_transient_failure_retries_and_eventually_succeeds(monkeypatch):
    notifier = ConsoleNotifier()

    attempts = []
    delays = []

    def fake_send(recipient, message):
        attempts.append(1)

        if len(attempts) < 3:
            raise TransientNotificationError("Temporary failure")

    monkeypatch.setattr(notifier, "_send", fake_send)
    monkeypatch.setattr("notifier.time.sleep", delays.append)

    notifier.deliver("alex@gmail.com", "Hello Alex")

    assert len(attempts) == 3
    assert delays == [1, 2]


def test_transient_failure_stops_after_max_attempts(monkeypatch):
    notifier = ConsoleNotifier()

    attempts = []
    delays = []

    def fake_send(recipient, message):
        attempts.append(1)
        raise TransientNotificationError("Temporary failure")

    monkeypatch.setattr(notifier, "_send", fake_send)
    monkeypatch.setattr("notifier.time.sleep", delays.append)

    with pytest.raises(TransientNotificationError, match="Temporary failure"):
        notifier.deliver("alex@gmail.com", "Hello Alex")

    assert len(attempts) == 3
    assert delays == [1, 2]


def test_validation_errors_are_not_retried(monkeypatch):
    notifier = ConsoleNotifier()

    attempts = []

    def fake_send(recipient, message):
        attempts.append(1)

    monkeypatch.setattr(notifier, "_send", fake_send)

    with pytest.raises(ValueError, match="Recipient cannot be empty"):
        notifier.deliver("", "Hello Alex")

    assert len(attempts) == 0