"""Orchestrate routing, deterministic tools, knowledge, and responders (Step 9)."""

import logging

from assistant_core.config import Settings
from assistant_core.errors import InvalidRequest, ProviderError
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message, Response, Source
from assistant_core.responder import Responder, TemplateResponder
from assistant_core.router import route
from assistant_core.tools import parse_credits, tuition

log = logging.getLogger(__name__)


class AssistantService:
    def __init__(
        self,
        settings: Settings,
        offices: OfficeDirectory,
        handbook: Handbook,
        responder: Responder,
    ) -> None:
        self.settings, self.offices, self.handbook = settings, offices, handbook
        self.responder = responder
        self.fallback = TemplateResponder()

    def handle(self, msg: Message) -> Response:
        intent = route(msg.text, self.offices.names)

        if intent is Intent.GREETING:
            return Response(
                answer="Hello! I can help with offices, fees and rules.",
                intent=intent,
            )

        if intent is Intent.FEE:
            return self._fee(msg.text)

        if intent is Intent.OFFICE:
            o = self.offices.find(msg.text)
            if o is None:
                return Response(answer="Sorry, I don't know that yet.", intent=Intent.UNKNOWN)
            return Response(
                answer=f"{o.name}: room {o.room}, open {o.hours}.",
                intent=intent,
            )

        return self._rule(msg.text)

    def _fee(self, text: str) -> Response:
        try:
            credits, retake = parse_credits(text)
            total = tuition(
                credits,
                retake,
                self.settings.credit_rate_vnd,
                self.settings.retake_multiplier,
                self.settings.max_credits,
            )
        except InvalidRequest as exc:
            return Response(answer=str(exc), intent=Intent.FEE)

        return Response(answer=f"Your tuition is {total:,} VND.", intent=Intent.FEE)

    def _rule(self, text: str) -> Response:
        rule = self.handbook.search(text)

        if rule is None:
            return Response(
                answer="Sorry, I don't know that yet.",
                intent=Intent.UNKNOWN,
            )

        sources = [Source(id=rule.id, title=rule.title)]

        try:
            return Response(
                answer=self.responder.explain(text, rule),
                intent=Intent.RULE,
                sources=sources,
            )
        except ProviderError:
            log.warning("provider failed; using template fallback")
            answer = self.fallback.explain(text, rule)
            return Response(
                answer=answer,
                intent=Intent.RULE,
                sources=sources,
                degraded=True,
            )
