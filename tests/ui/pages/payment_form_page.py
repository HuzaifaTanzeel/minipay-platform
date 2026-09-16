"""Create-payment form at /payments/new."""


class PaymentFormPage:
    def __init__(self, page, base: str):
        self.p = page
        self.base = base.rstrip("/")

    def open(self):
        self.p.goto(self.base + "/payments/new")
        self.p.get_by_test_id("payment-form").wait_for()
        return self

    def fill_customer(self, customer_ref: str):
        self.p.get_by_test_id("pay-customer").fill(customer_ref)

    def fill_amount(self, amount: str):
        self.p.get_by_test_id("pay-amount").fill(amount)

    def submit(self):
        self.p.get_by_test_id("pay-submit").click()

    def create(self, customer_ref: str, amount: str):
        self.fill_customer(customer_ref)
        self.fill_amount(amount)
        self.submit()
