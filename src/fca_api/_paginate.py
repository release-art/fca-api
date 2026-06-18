"""The ``@paginated`` decorator and the task-local channel it feeds.

Internal; not part of the public API.
"""

import contextvars
import dataclasses
import functools
import inspect
import typing

_PaginatedFn = typing.TypeVar("_PaginatedFn", bound=typing.Callable[..., typing.Awaitable[typing.Any]])


@dataclasses.dataclass(frozen=True, slots=True)
class _ResumeState:
    """Endpoint name and call arguments of the active ``@paginated`` call.

    The fetch helpers read it to build the ``next_page`` token; an empty
    ``endpoint`` means no paginated call is active.
    """

    endpoint: str = ""
    params: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)


#: Task-local channel from :func:`paginated` to the fetch helpers. Task-local so
#: concurrent paginated calls on one client don't clash.
_resume_ctx: contextvars.ContextVar[typing.Optional[_ResumeState]] = contextvars.ContextVar(
    "fca_api_resume_ctx", default=None
)


def current_resume_state() -> _ResumeState:
    """The active ``@paginated`` call's :class:`_ResumeState`, or an empty one."""
    return _resume_ctx.get() or _ResumeState()


def paginated(*, exclude: typing.Collection[str] = ("self",)) -> typing.Callable[[_PaginatedFn], _PaginatedFn]:
    """Decorate an async ``Client`` method that returns a ``MultipageList``.

    * Publishes the endpoint name and arguments on :data:`_resume_ctx` so the
      fetch helpers can build a replayable ``next_page`` token.
    * Binds the client to the result so :meth:`MultipageList.get_next` works.

    Args:
        exclude: Argument names left out of the resume token's ``params``
            (cursor position is tracked separately). Defaults to ``self``.
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
                result = await func(*args, **kwargs)
            finally:
                _resume_ctx.reset(ctx_token)
            result._client = args[0]  # bind the Client (self) for get_next()
            return result

        return typing.cast(_PaginatedFn, wrapper)

    return decorate
