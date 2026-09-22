"""The guarded request path.

Replaces the pipeline in ``multi_agent_server.py:3276``. Ordering is the whole
point and is enforced by tests:

    authenticate -> resolve in canonical registry -> validate arguments
      -> policy -> execute -> report actual outcome -> audit every stage

Four defects in the current path are fixed here:

* a client string no longer reaches ``getattr``;
* unknown arguments are rejected instead of silently filtered;
* a failure is never returned as a success envelope with HTTP 200;
* the audit trail records what actually happened, not an optimistic guess.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Mapping

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ..audit import AuditStage, AuditTrail
from ..auth import AuthError, LoginFailed, LoginService, TokenIssuer, principal_from_request
from ..policy import Decision, PolicyEngine, Principal
from ..registry import CanonicalToolRegistry
from ..schemas import UnknownArgument, validate_arguments


@dataclass(frozen=True)
class CallResponse:
    """What the caller — human or agent — is told."""

    status: int
    body: dict[str, Any]


def _error(code: str, message: str, status: int, run_id: str, **extra: Any) -> CallResponse:
    body = {
        "success": False,
        "run_id": run_id,
        "error": {"code": code, "message": message},
        "executed": False,
    }
    body["error"].update(extra)
    return CallResponse(status=status, body=body)


class ToolCallService:
    """Transport-independent implementation, so it can be tested without HTTP."""

    def __init__(
        self,
        registry: CanonicalToolRegistry,
        engine: PolicyEngine,
        issuer: TokenIssuer,
        audit_sink,
    ):
        self._registry = registry
        self._engine = engine
        self._issuer = issuer
        self._sink = audit_sink

    def call(self, headers: Mapping[str, str], payload: Mapping[str, Any]) -> CallResponse:
        trail = AuditTrail(self._sink)
        run_id = trail.run_id

        params = payload.get("params") or {}
        tool = params.get("name")
        arguments = params.get("arguments") or {}

        trail.record(AuditStage.REQUESTED, tool=tool, arguments=arguments)

        # 1. Authenticate. Identity comes from a verified token, never the body.
        try:
            principal: Principal = principal_from_request(headers, self._issuer)
        except AuthError as exc:
            trail.record(AuditStage.AUTHENTICATION_FAILED, tool=tool, detail=exc.code)
            trail.record(AuditStage.NOT_EXECUTED, tool=tool)
            return _error(exc.code, "authentication required", exc.http_status, run_id)

        trail.record(
            AuditStage.AUTHENTICATED, tool=tool, user_id=principal.user_id, role=principal.role
        )

        if not tool or not isinstance(tool, str):
            trail.record(AuditStage.VALIDATION_FAILED, detail="missing tool name")
            trail.record(AuditStage.NOT_EXECUTED)
            return _error("MISSING_TOOL_NAME", "params.name is required", 400, run_id)

        # 2. The tool must exist in the canonical registry. Dict lookup only.
        handler = self._registry.resolve(tool)
        if handler is None:
            trail.record(
                AuditStage.VALIDATION_FAILED, tool=tool,
                user_id=principal.user_id, role=principal.role, detail="unknown tool",
            )
            trail.record(AuditStage.NOT_EXECUTED, tool=tool)
            return _error("UNKNOWN_TOOL", f"no tool named '{tool}'", 404, run_id)

        # 3. Arguments must satisfy the declared schema. Unknown keys are fatal.
        try:
            validated = validate_arguments(tool, arguments)
        except UnknownArgument as exc:
            trail.record(
                AuditStage.VALIDATION_FAILED, tool=tool, user_id=principal.user_id,
                role=principal.role, arguments=arguments, detail="schema violation",
            )
            trail.record(AuditStage.NOT_EXECUTED, tool=tool)
            return _error(
                "INVALID_ARGUMENTS", f"arguments rejected for '{tool}'", 400, run_id,
                violations=exc.errors,
            )

        # 4. Policy. Deterministic, and a function of (role, tool) only.
        decision = self._engine.check(principal, tool, validated)

        if decision.decision is Decision.DENY:
            trail.record(
                AuditStage.POLICY_DENIED, tool=tool, user_id=principal.user_id,
                role=principal.role, detail=decision.rule_id,
            )
            trail.record(AuditStage.NOT_EXECUTED, tool=tool)
            return _error("POLICY_DENIED", decision.reason, 403, run_id, rule=decision.rule_id)

        if decision.decision in (Decision.REQUIRE_HUMAN_APPROVAL, Decision.REQUIRE_CONFIRMATION):
            stage = (
                AuditStage.APPROVAL_REQUIRED
                if decision.decision is Decision.REQUIRE_HUMAN_APPROVAL
                else AuditStage.CONFIRMATION_REQUIRED
            )
            trail.record(
                stage, tool=tool, user_id=principal.user_id, role=principal.role,
                arguments=validated, detail=decision.rule_id,
            )
            trail.record(AuditStage.NOT_EXECUTED, tool=tool)
            # 202: accepted, deliberately not executed. Never 200 — an agent must
            # not read a pause as an observation that the action happened.
            return CallResponse(
                status=202,
                body={
                    "success": False,
                    "executed": False,
                    "run_id": run_id,
                    "status": decision.decision.value,
                    "tool": tool,
                    "reason": decision.reason,
                },
            )

        # 5. Execute.
        trail.record(
            AuditStage.EXECUTING, tool=tool, user_id=principal.user_id,
            role=principal.role, arguments=validated,
        )
        started = time.perf_counter()
        try:
            value = handler(**validated)
        except Exception as exc:
            elapsed = int((time.perf_counter() - started) * 1000)
            trail.record(
                AuditStage.FAILED, tool=tool, user_id=principal.user_id, role=principal.role,
                detail=type(exc).__name__, latency_ms=elapsed,
            )
            # Type name only. No traceback crosses the boundary.
            return _error(
                "TOOL_EXECUTION_FAILED", f"'{tool}' did not complete", 502, run_id,
                failure_type=type(exc).__name__,
            )

        elapsed = int((time.perf_counter() - started) * 1000)
        trail.record(
            AuditStage.SUCCEEDED, tool=tool, user_id=principal.user_id,
            role=principal.role, latency_ms=elapsed,
        )
        return CallResponse(
            status=200,
            body={
                "success": True,
                "executed": True,
                "run_id": run_id,
                "tool": tool,
                "result": value,
                "latency_ms": elapsed,
            },
        )


def build_login_route(login: LoginService, path: str = "/auth/login") -> list[Route]:
    """POST /auth/login -> a signed token whose role comes from the database.

    The request body supplies credentials only. Any 'role' the caller includes is
    ignored; the issued token carries the role stored on the user row.
    """

    async def handler(request: Request) -> JSONResponse:
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                {"success": False, "error": {"code": "MALFORMED_BODY",
                                             "message": "request body must be JSON"}},
                status_code=400,
            )

        username = body.get("username") or body.get("email")
        password = body.get("password")
        if not username or not password:
            return JSONResponse(
                {"success": False, "error": {"code": "MISSING_CREDENTIALS",
                                             "message": "username and password are required"}},
                status_code=400,
            )

        try:
            result = login.authenticate(str(username), str(password))
        except LoginFailed as exc:
            # One message for every failure mode: no user enumeration.
            return JSONResponse(
                {"success": False, "error": {"code": exc.code,
                                             "message": "invalid credentials"}},
                status_code=exc.http_status,
            )

        return JSONResponse(
            {
                "success": True,
                "token": result.token,
                "token_type": "Bearer",
                "expires_in_minutes": result.expires_in_minutes,
                "user": {"id": result.user_id, "role": result.role},
            },
            status_code=200,
        )

    return [Route(path, handler, methods=["POST"])]


def build_guarded_routes(service: ToolCallService, path: str = "/v2/tools/call") -> list[Route]:
    async def handler(request: Request) -> JSONResponse:
        try:
            payload = await request.json()
        except Exception:
            return JSONResponse(
                {"success": False, "executed": False,
                 "error": {"code": "MALFORMED_BODY", "message": "request body must be JSON"}},
                status_code=400,
            )
        response = service.call(request.headers, payload)
        return JSONResponse(response.body, status_code=response.status)

    return [Route(path, handler, methods=["POST"])]
