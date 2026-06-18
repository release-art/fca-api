# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-06-17

Pagination is restructured around self-contained, restartable cursors. The
`next_page` token now embeds the originating endpoint and its arguments, so a
fresh process can fetch the next batch with only the token — designed for
stateless services and AI-agent tools that return one page plus an opaque
cursor and resume on a later, independent request.

### Added
- `Client.fetch_next_page(token)` — resume any paginated request from a
  self-contained `next_page` cursor. Validates the token against a
  `_RESUMABLE_ENDPOINTS` allowlist before dispatching, so a malformed token
  cannot dispatch to an arbitrary client method.

### Changed
- **Breaking:** paginated endpoint methods no longer accept a `next_page`
  parameter. Resume goes through `Client.fetch_next_page(token)`. Migration::

      # before
      page2 = await client.search_frn("Barclays", next_page=page1.pagination.next_page)

      # after
      page2 = await client.fetch_next_page(page1.pagination.next_page)

- **Breaking:** `MultipageList.data` is now a `tuple` rather than a `list`.
  Iteration and indexing are unchanged; `.append`/`.extend`/`__setitem__` are
  no longer available. Reflects that `data` is a snapshot and must not be
  mutated after leaving the client.
- `MultipageList` is now a pure-data value object — no client reference, no
  behavior. Pickle, JSON, deepcopy, and equality all work without special
  handling. Advance pagination via `Client.fetch_next_page(page.pagination.next_page)`.
- The `next_page` token format now embeds the endpoint name and bound kwargs
  in addition to the page number. Tokens remain opaque to callers, but
  cursors issued by 1.2.x are not decodable by 1.3.0 (and vice versa) —
  exhaust or discard any in-flight cursors before upgrading.
