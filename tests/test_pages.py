"""Smoke-test every page with Streamlit's AppTest: it must render without exceptions."""
import time

import pytest
from streamlit.testing.v1 import AppTest

PAGES = ["overview", "explorer", "build_fighter", "stance_lab", "brian", "data_notes"]

SCRIPT = """
import ui, ufc_core as core
from views import {page} as view
ui.inject_css()
view.render(core.load_fighters())
"""


@pytest.mark.parametrize("page", PAGES)
def test_page_renders(page):
    at = AppTest.from_string(SCRIPT.format(page=page), default_timeout=60)
    t = time.time()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert time.time() - t < 20, "page too slow"


def test_overview_filters_to_empty_state():
    at = AppTest.from_string(SCRIPT.format(page="overview"), default_timeout=60)
    at.run()
    at.selectbox(key="ov_wc").set_value("Women's Featherweight").run()
    at.selectbox(key="ov_st").set_value("Southpaw").run()
    assert not at.exception


def test_stance_lab_every_outcome():
    at = AppTest.from_string(SCRIPT.format(page="stance_lab"), default_timeout=60)
    at.run()
    for label in at.selectbox[0].options:
        at.selectbox[0].set_value(label).run()
        assert not at.exception, label


def test_build_fighter_cross_dominant_grappler():
    at = AppTest.from_string(SCRIPT.format(page="build_fighter"), default_timeout=60)
    at.run()
    at.radio(key="bf_foot").set_value("Left").run()
    at.selectbox(key="bf_style").set_value("Grappler").run()
    at.slider(key="bf_freq").set_value(1).run()
    assert not at.exception
