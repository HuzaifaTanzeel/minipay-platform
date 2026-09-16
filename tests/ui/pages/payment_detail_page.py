"""Payment detail card shown after search or create."""


class PaymentDetailPage:
    def __init__(self, page):
        self.p = page

    @property
    def result_card(self):
        return self.p.get_by_test_id("result-card")

    @property
    def status(self):
        return self.p.get_by_test_id("result-status")

    @property
    def error(self):
        return self.p.get_by_test_id("error-banner")

    @property
    def success_banner(self):
        return self.p.get_by_test_id("success-banner")
