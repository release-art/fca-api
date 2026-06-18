"""Internal: ``@paginated`` decorator and the task-local resume channel."""

import contextvars
import dataclasses
import functools
import inspect
import typing

_PaginatedFn = typing.TypeVar("_PaginatedFn", bound=typing.Callable[..., typing.Awaitable[typing.Any]])


@dataclasses.dataclass(frozen=True, slots=True)
class _ResumeState:
    """Endpoint name and call arguments of the active ``@paginated`` call.

    Fetch helpers read it to stamp the outgoing ``next_page`` token; an empty
    ``endpoint`` means no paginated call is active.
    """

    endpoint: str = ""
    params: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)


#: Task-local so concurrent paginated calls on one client don't clash.
_resume_ctx: contextvars.ContextVar[typing.Optional[_ResumeState]] = contextvars.ContextVar(
    "fca_api_resume_ctx", default=None
)


def current_resume_state() -> _ResumeState:
    """Active call's :class:`_ResumeState`, or an empty one."""
    return _resume_ctx.get() or _ResumeState()


def paginated(*, exclude: typing.Collection[str] = ("self",)) -> typing.Callable[[_PaginatedFn], _PaginatedFn]:
    """Mark an async ``Client`` method as returning a ``MultipageList``.

    Publishes the endpoint name and bound arguments on :data:`_resume_ctx`
    for the fetch helpers to stamp into the ``next_page`` token.

    Args:
        exclude: Argument names omitted from the token's ``params`` (cursor
            position is tracked separately). Defaults to ``self``.
    """
    excluded = set(exclude)

    def decorate(func: _PaginatedFn) -> _PaginatedFn:
        endpoint = func.__name__
        sig = inspect.signature(func)

        @functools.wraps(func)
        async def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = {name: value for name, value in bound.arguments.items() if name not in excluded}
            ctx_token = _resume_ctx.set(_ResumeState(endpoint=endpoint, params=params))
            try:
                return await func(*args, **kwargs)
            finally:
                _resume_ctx.reset(ctx_token)

        return typing.cast(_PaginatedFn, wrapper)

    return decorate
