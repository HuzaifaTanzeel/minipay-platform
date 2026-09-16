"""Browser journeys against the Compose-served operations console."""
from __future__ import annotations

from playwright.sync_api import expect

from pages.payment_detail_page import PaymentDetailPage
from pages.payment_form_page import PaymentFormPage
from pages.search_page import SearchPage

SEED_REF = "TXN00000001"


def test_open_home(page, base_url):
    """home opens with the search box."""
    SearchPage(page, base_url).open()
    expect(page.get_by_test_id("search-input")).to_be_visible()
    expect(page.get_by_role("heading", name="Operations dashboard")).to_be_visible()


def test_search_existing_transaction_shows_card(page, base_url):
    """search an existing seed reference shows the result card."""
    SearchPage(page, base_url).open().search(SEED_REF)
    detail = PaymentDetailPage(page)
    expect(detail.result_card).to_be_visible()
    expect(detail.result_card).to_contain_text(SEED_REF)
    expect(detail.status).to_be_visible()


def test_create_payment_success(page, base_url, unique_customer):
    """create payment lands on the detail page as PROCESSING."""
    form = PaymentFormPage(page, base_url).open()
    form.create(unique_customer["customer_ref"], "12.50")
    detail = PaymentDetailPage(page)
    expect(detail.success_banner).to_be_visible()
    expect(detail.result_card).to_be_visible()
    expect(detail.status).to_have_text("PROCESSING")


def test_search_unknown_reference_shows_error(page, base_url):
    """unknown reference shows the error banner."""
    SearchPage(page, base_url).open().search("TXNNOPE0001")
    expect(PaymentDetailPage(page).error).to_be_visible()


def test_create_payment_invalid_amount_shows_validation(page, base_url):
    """negative amount is rejected in the form without a round-trip."""
    form = PaymentFormPage(page, base_url).open()
    form.create("CUST000001", "-1")
    expect(page.get_by_test_id("error-amount")).to_be_visible()
    expect(page.get_by_test_id("error-amount")).to_contain_text("greater than 0")
    expect(page).to_have_url(base_url.rstrip("/") + "/payments/new")
