"""Polite HTTP fetching: robots.txt, identifying User-Agent, rate limit, retries, disk cache.

Fetching lives here and nowhere else; the parsers in the sibling modules are pure functions of
HTML text. Everything that touches the clock, the network or the disk can be injected, so the
behaviour is unit-tested offline with a fake session (see tests/test_ingestion_fetch.py).

Personal / portfolio use only. Check the target site's terms of use before running a live fetch.
"""
from __future__ import annotations

import hashlib
import logging
import time
from pathlib import Path
from typing import Callable
from urllib import robotparser
from urllib.parse import urlsplit

import requests

log = logging.getLogger(__name__)

MIN_INTERVAL_SECONDS = 1.0
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


class FetchError(RuntimeError):
    """A page could not be fetched (after retries, or a non-retryable HTTP status)."""


class RobotsDisallowed(FetchError):
    """robots.txt does not allow this User-Agent to fetch the URL. The run should stop politely."""


class PoliteFetcher:
    def __init__(
        self,
        user_agent: str,
        cache_dir: str | Path | None = "data/raw_html",
        min_interval: float = 1.5,
        max_retries: int = 3,
        backoff_base: float = 2.0,
        timeout: float = 15.0,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ):
        if min_interval < MIN_INTERVAL_SECONDS:
            raise ValueError(f"min_interval must be >= {MIN_INTERVAL_SECONDS}s (got {min_interval})")
        if not user_agent or not user_agent.strip():
            raise ValueError("an identifying user_agent is required")
        self.user_agent = user_agent
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.min_interval = min_interval
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.timeout = timeout
        self.session = session or requests.Session()
        self._sleep = sleep
        self._clock = clock
        self._last_request: float | None = None
        self._robots: dict[str, robotparser.RobotFileParser | None] = {}
        self.network_requests = 0  # includes robots.txt fetches; handy for tests and logs

    # ---- rate limiting -------------------------------------------------------------------
    def _wait_turn(self) -> None:
        if self._last_request is not None:
            wait = self.min_interval - (self._clock() - self._last_request)
            if wait > 0:
                self._sleep(wait)
        self._last_request = self._clock()

    # ---- HTTP with retries ---------------------------------------------------------------
    def _get(self, url: str) -> requests.Response:
        headers = {"User-Agent": self.user_agent}
        last: Exception | None = None
        for attempt in range(self.max_retries + 1):
            self._wait_turn()
            self.network_requests += 1
            try:
                resp = self.session.get(url, headers=headers, timeout=self.timeout)
            except requests.RequestException as exc:
                last = exc
                log.warning("GET %s failed (%s), attempt %d/%d", url, exc, attempt + 1, self.max_retries + 1)
            else:
                if resp.status_code not in RETRY_STATUS:
                    return resp
                last = FetchError(f"HTTP {resp.status_code}")
                log.warning("GET %s -> HTTP %s, attempt %d/%d", url, resp.status_code, attempt + 1, self.max_retries + 1)
                retry_after = resp.headers.get("Retry-After", "")
                if attempt < self.max_retries and retry_after.isdigit():
                    self._sleep(min(float(retry_after), 60.0))
            if attempt < self.max_retries:
                self._sleep(self.backoff_base * (2 ** attempt))
        raise FetchError(f"giving up on {url} after {self.max_retries + 1} attempts: {last}")

    # ---- robots.txt ----------------------------------------------------------------------
    def _robots_for(self, url: str) -> robotparser.RobotFileParser | None:
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._robots:
            robots_url = origin + "/robots.txt"
            rp = robotparser.RobotFileParser()
            try:
                resp = self._get(robots_url)
            except FetchError as exc:
                # Unreachable / 5xx robots.txt: be conservative and treat the site as off limits.
                log.error("could not read %s (%s); treating as disallowed", robots_url, exc)
                self._robots[origin] = None
                return None
            if resp.status_code in (401, 403):
                rp.disallow_all = True
            elif resp.status_code >= 400:  # 404 etc.: no robots.txt means no restrictions
                rp.allow_all = True
            else:
                rp.parse(resp.text.splitlines())
            self._robots[origin] = rp
        return self._robots[origin]

    def allowed(self, url: str) -> bool:
        rp = self._robots_for(url)
        return bool(rp and rp.can_fetch(self.user_agent, url))

    # ---- cache ---------------------------------------------------------------------------
    def _cache_path(self, url: str) -> Path | None:
        if self.cache_dir is None:
            return None
        return self.cache_dir / (hashlib.sha256(url.encode("utf-8")).hexdigest()[:32] + ".html")

    # ---- public --------------------------------------------------------------------------
    def get_html(self, url: str) -> str:
        """Return the page HTML: from the disk cache if present, else after a polite live fetch."""
        cached = self._cache_path(url)
        if cached is not None and cached.exists():
            log.info("cache hit %s", url)
            return cached.read_text(encoding="utf-8")
        if not self.allowed(url):
            raise RobotsDisallowed(f"robots.txt disallows {url} for user-agent {self.user_agent!r}")
        resp = self._get(url)
        if resp.status_code >= 400:
            raise FetchError(f"HTTP {resp.status_code} for {url}")
        html = resp.text
        if cached is not None:
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_text(html, encoding="utf-8")
        log.info("fetched %s (%d chars)", url, len(html))
        return html
