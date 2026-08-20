from abc import ABC, abstractmethod
import time


class TransientNotificationError(Exception):
    """Raised when notification delivery may succeed if retried."""


class Notifier(ABC):
    """Abstract interface for notification delivery channels."""

    @abstractmethod
    def deliver(self, recipient, message):
        """Deliver a rendered notification message."""
        raise NotImplementedError


class ConsoleNotifier(Notifier):
    """Delivers notifications by printing them to the console."""

    MAX_ATTEMPTS = 3
    BASE_DELAY = 1

    def deliver(self, recipient, message):
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError("Recipient cannot be empty.")

        if not isinstance(message, str) or not message.strip():
            raise ValueError("Message cannot be empty.")

        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                self._send(recipient, message)
                return

            except TransientNotificationError:
                if attempt == self.MAX_ATTEMPTS:
                    raise

                delay = self.BASE_DELAY * (2 ** (attempt - 1))
                time.sleep(delay)

    def _send(self, recipient, message):
        """Perform the actual notification delivery."""
        print(f"Notification for {recipient}")
        print(message)