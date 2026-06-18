# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-06-17

Pagination is restructured around self-contained, restartable cursors —
aligning with the design landed in `ch-api`. The `next_page` token now embeds
the originating endpoint and its arguments, so a fresh process can fetch the
next batch with only the token. Designed for stateless services and AI-agent
tools that return one page plus an opaque cursor and resume on a later,
independent request.

### Added
- `Client.fetch_next_page(token)` — resume any paginated request from a
  self-contained `next_page` cursor. Validates the token against a
  `_RESUMABLE_ENDPOINTS` allowlist before dispatching, so malformed or
  tampered tokens cannot call arbitrary client methods.
- `MultipageList.get_next()` — sugar over `Client.fetch_next_page(token)`
  using the page's own cursor. Available whenever the page was produced by a
  `Client` call (the client is bound on the result automatically).
- `MultipageList.with_client(client)` — rebind a client to a deserialized or
  manually-constructed page so `get_next()` works on it.

### Changed
- **Breaking:** paginated endpoint methods no longer accept a `next_page`
  parameter. Resume is now done exclusively via `Client.fetch_next_page(token)`
  or `MultipageList.get_next()`. Migration::

      # before
      page2 = await client.search_frn("Barclays", next_page=page1.pagination.next_page)

      # after
      page2 = await client.fetch_next_page(page1.pagination.next_page)
      # or
      page2 = await page1.get_next()

- The `next_page` token format now embeds the endpoint name and bound kwargs
  in addition to the page number. Tokens remain opaque to callers, but
  cursors issued by 1.2.x are not decodable by 1.3.0 (and vice versa) —
  exhaust or discard any in-flight cursors before upgrading.
