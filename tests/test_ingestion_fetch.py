"""PoliteFetcher: robots.txt, rate limit, retries, cache. All HTTP is mocked; runs offline."""
import pytest
import requests

from ingestion.fetch import FetchError, PoliteFetcher, RobotsDisallowed

UA = "test-agent/1.0 (unit tests)"


class Resp:
    def __init__(self, status=200, text="", headers=None):
        self.status_code, self.text, self.headers = status, text, headers or {}


class FakeSession:
    """Maps URL -> a response, an exception, or a list of them consumed in order."""

    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get(self, url, headers=None, timeout=None):
        self.calls.append((url, headers, timeout))
        item = self.routes[url]
        if isinstance(item, list):
            item = item.pop(0) if len(item) > 1 else item[0]
        if isinstance(item, Exception):
            raise item
        return item


class Clock:
    def __init__(self):
        self.now, self.sleeps = 1000.0, []

    def time(self):
        return self.now

    def sleep(self, s):
        self.sleeps.append(s)
        self.now += s


def make(routes, tmp_path, **kw):
    clock = Clock()
    sess = FakeSession(routes)
    f = PoliteFetcher(UA, tmp_path / "cache", session=sess, sleep=clock.sleep, clock=clock.time, **kw)
    return f, sess, clock


OPEN = Resp(200, "User-agent: *\nDisallow: /private/\n")
URL = "http://x.test/page"


def test_rejects_fast_rate_and_missing_user_agent(tmp_path):
    with pytest.raises(ValueError):
        PoliteFetcher(UA, tmp_path, min_interval=0.5)
    with pytest.raises(ValueError):
        PoliteFetcher("  ", tmp_path)


def test_sends_identifying_user_agent_and_checks_robots_first(tmp_path):
    f, sess, _ = make({"http://x.test/robots.txt": OPEN, URL: Resp(200, "<p>hi</p>")}, tmp_path)
    assert f.get_html(URL) == "<p>hi</p>"
    assert [c[0] for c in sess.calls] == ["http://x.test/robots.txt", URL]
    assert all(c[1]["User-Agent"] == UA for c in sess.calls)


def test_disallowed_path_aborts_without_fetching(tmp_path):
    f, sess, _ = make({"http://x.test/robots.txt": OPEN}, tmp_path)
    with pytest.raises(RobotsDisallowed):
        f.get_html("http://x.test/private/secret")
    assert [c[0] for c in sess.calls] == ["http://x.test/robots.txt"]


def test_robots_is_fetched_once_per_host(tmp_path):
    f, sess, _ = make({"http://x.test/robots.txt": OPEN, URL: Resp(200, "a"), URL + "2": Resp(200, "b")}, tmp_path)
    f.get_html(URL)
    f.get_html(URL + "2")
    assert sum(c[0].endswith("robots.txt") for c in sess.calls) == 1


@pytest.mark.parametrize("status,allowed", [(404, True), (403, False), (401, False)])
def test_robots_status_handling(tmp_path, status, allowed):
    f, _, _ = make({"http://x.test/robots.txt": Resp(status), URL: Resp(200, "ok")}, tmp_path)
    assert f.allowed(URL) is allowed


def test_unreachable_robots_is_treated_as_disallowed(tmp_path):
    f, _, _ = make({"http://x.test/robots.txt": requests.ConnectionError("down")}, tmp_path, max_retries=1)
    with pytest.raises(RobotsDisallowed):
        f.get_html(URL)


def test_rate_limit_spaces_requests_by_at_least_min_interval(tmp_path):
    f, sess, clock = make({"http://x.test/robots.txt": OPEN, URL: Resp(200, "a"), URL + "2": Resp(200, "b")},
                          tmp_path, min_interval=1.5)
    t = []
    orig = sess.get

    def spy(url, **kw):  # time at which each request actually hits the (fake) network
        t.append(clock.now)
        return orig(url, **kw)

    sess.get = spy
    f.get_html(URL)
    f.get_html(URL + "2")
    assert len(t) == 3
    assert all(b - a >= 1.5 - 1e-9 for a, b in zip(t, t[1:]))


def test_retries_with_exponential_backoff_then_succeeds(tmp_path):
    routes = {"http://x.test/robots.txt": OPEN,
              URL: [Resp(503), requests.Timeout("slow"), Resp(200, "finally")]}
    f, sess, clock = make(routes, tmp_path, backoff_base=2.0, max_retries=3)
    assert f.get_html(URL) == "finally"
    assert sum(c[0] == URL for c in sess.calls) == 3
    assert 2.0 in clock.sleeps and 4.0 in clock.sleeps  # backoff 2s then 4s


def test_gives_up_after_max_retries(tmp_path):
    f, sess, _ = make({"http://x.test/robots.txt": OPEN, URL: Resp(500)}, tmp_path, max_retries=2)
    with pytest.raises(FetchError):
        f.get_html(URL)
    assert sum(c[0] == URL for c in sess.calls) == 3


def test_non_retryable_status_fails_immediately(tmp_path):
    f, sess, _ = make({"http://x.test/robots.txt": OPEN, URL: Resp(404)}, tmp_path)
    with pytest.raises(FetchError):
        f.get_html(URL)
    assert sum(c[0] == URL for c in sess.calls) == 1


def test_retry_after_header_is_honoured(tmp_path):
    routes = {"http://x.test/robots.txt": OPEN, URL: [Resp(429, headers={"Retry-After": "7"}), Resp(200, "ok")]}
    f, _, clock = make(routes, tmp_path)
    f.get_html(URL)
    assert 7.0 in clock.sleeps


def test_disk_cache_avoids_second_network_call(tmp_path):
    f, sess, _ = make({"http://x.test/robots.txt": OPEN, URL: Resp(200, "<p>cached</p>")}, tmp_path)
    f.get_html(URL)
    n = len(sess.calls)
    assert f.get_html(URL) == "<p>cached</p>"
    assert len(sess.calls) == n
    assert list((tmp_path / "cache").glob("*.html"))  # raw HTML is on disk
