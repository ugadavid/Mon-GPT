"""Les particularités ChatGPT restent dans cet adaptateur."""
from dataclasses import dataclass, asdict
from urllib.parse import urlsplit, urlunsplit
from uuid import UUID
import re


@dataclass
class Conversation:
    record_id: str
    conversation_id: str
    url: str


def parse_url(url):
    try:
        parsed = urlsplit(url.strip())
        if parsed.scheme != "https" or parsed.netloc.lower() != "chatgpt.com":
            raise ValueError()
        match = re.fullmatch(r"/(?:g/[A-Za-z0-9_-]+/)?c/([0-9a-fA-F-]{36})/?", parsed.path)
        if not match:
            raise ValueError()
        identity = str(UUID(match[1]))
        return identity, urlunsplit(("https", "chatgpt.com", parsed.path.rstrip("/"), parsed.query, ""))
    except (ValueError, AttributeError):
        raise ValueError("Utilisez https://chatgpt.com/c/UUID ou https://chatgpt.com/g/SLUG/c/UUID.") from None


class ChatGPT:
    def __init__(self, catalog, conversations=()):
        self.catalog = catalog
        self.conversations = {c.record_id: c for c in conversations}

    def ingest(self, title, url):
        identity, source = parse_url(url)
        for c in self.conversations.values():
            if c.conversation_id == identity:
                return self.catalog.records[c.record_id], False
        r = self.catalog.add(title)
        self.conversations[r.id] = Conversation(r.id, identity, source)
        return r, True

    def change_url(self, record_id, url):
        identity, source = parse_url(url)
        if any(c.record_id != record_id and c.conversation_id == identity for c in self.conversations.values()):
            raise ValueError("Cette conversation possède déjà une fiche.")
        self.conversations[record_id] = Conversation(record_id, identity, source)

    def to_list(self):
        return [asdict(c) for key, c in self.conversations.items() if key in self.catalog.records]
