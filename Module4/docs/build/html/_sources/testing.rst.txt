Testing Guide
=============

This project uses pytest with multiple markers.

Markers
-------

- web → Flask routes
- buttons → UI behavior
- analysis → SQL/output formatting
- data → cleaning and ETL
- integration → end-to-end tests

Fixtures
--------

- client → Flask test client
- app → test Flask app factory

Mocking / Test Doubles
----------------------

Tests use:
- monkeypatch for replacing scraper
- MagicMock for Selenium driver
- fake DB connections for isolation

Example:

monkeypatch.setattr("src.scrape.webdriver.Chrome", lambda: mock_driver)