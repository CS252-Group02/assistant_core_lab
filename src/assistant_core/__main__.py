"""Command-line entry point for :mod:`assistant_core`."""

import sys

from assistant_core.config import load_settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Message
from assistant_core.responder import TemplateResponder
from assistant_core.service import AssistantService


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m assistant_core "your question"', file=sys.stderr)
        raise SystemExit(2)

    settings = load_settings()
    setup_logging(settings.log_level)

    offices = OfficeDirectory.from_csv(settings.data_dir / "offices.csv")
    handbook = Handbook.from_json(settings.data_dir / "handbook.json")
    responder = TemplateResponder()
    service = AssistantService(settings, offices, handbook, responder)

    message = Message(text=" ".join(sys.argv[1:]))
    response = service.handle(message)
    print(response.answer)


if __name__ == "__main__":
    main()
