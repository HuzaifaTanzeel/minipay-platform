"""Header search: type a transaction reference and submit."""


class SearchPage:
    def __init__(self, page, base: str):
        self.p = page
        self.base = base.rstrip("/")

    def open(self):
        self.p.goto(self.base + "/")
        self.p.get_by_test_id("search-input").wait_for()
        return self

    def search(self, ref: str):
        self.p.get_by_test_id("search-input").fill(ref)
        self.p.get_by_test_id("search-submit").click()
