"""Tests for `zoom_api_helper` package."""

import pytest


from zoom_api_helper import ZoomAPI


def test_create_zoom_client():
    """Sample pytest test function with the pytest fixture as an argument."""
    zoom = ZoomAPI.dummy_client()
    print(zoom)
