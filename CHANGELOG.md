# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-06-17

### Added
- `Client.next_page(page)` — fetches the next page of any previous paginated
  call without naming the originating endpoint again. Decodes the cursor on
  `page.pagination.next_page` and re-dispatches to the correct method with
  the same arguments. Raises `NoMorePagesError` when `page.pagination.has_next`
  is `False`.

### Changed
- The internal format of `NextPageToken` now carries the originating endpoint
  name and bound kwargs in addition to the page number. Tokens remain opaque
  to callers, but cursors issued by 1.2.x are not decodable by 1.3.0 (and
  vice versa) — exhaust or discard any in-flight cursors before upgrading.
