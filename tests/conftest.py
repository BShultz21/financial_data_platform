import pytest

@pytest.fixture
def sec_data():
    return [{"load_date": "2026-10-19",
        "cik": "0000019617",
         "api_data":
            {"AffordableHousingTaxCreditsAndOtherTaxBenefitsAmount":
                {"label": "Affordable Housing Tax Credits and Other Tax Benefits, Amount",
                "description": "Amount of affordable housing tax credits and other tax benefits recognized.",
                "units":
                    {"USD":
                        [{"start": "2013-01-01",
                        "end": "2013-12-31",
                        "val": 1500000000,
                        "accn": "0000019617-16-000902",
                        "fy": 2015,
                        "fp": "FY",
                        "form": "10-K",
                        "filed": "2016-02-23",
                        "frame": "CY2013"},
                        {"start": "2014-01-01",
                        "end": "2014-09-30",
                        "val": 1200000000,
                        "accn": "0000019617-15-000464",
                        "fy": 2015,
                        "fp": "Q3",
                        "form": "10-Q",
                        "filed": "2015-11-02"}]}},
            "Assets":
                {"label": "Assets",
                "description": "Sum of the carrying amounts as of the balance sheet date of all assets that are recognized.",
                "units":
                    {"USD":
                        [{"end": "2008-12-31",
                        "val": 2175052000000,
                        "accn": "0000950123-09-032832",
                        "fy": 2009,
                        "fp": "Q2",
                        "form": "10-Q",
                        "filed": "2009-08-10"},
                        {"end": "2008-12-31",
                        "val": 2175052000000,
                        "accn": "0000950123-09-060099",
                        "fy": 2009,
                        "fp": "Q3",
                        "form": "10-Q",
                        "filed": "2009-11-09"}]}},
            "CommonStockDividendsPerShareDeclared":
                {"label": "Common Stock, Dividends, Per Share, Declared",
                "description": "Aggregate dividends declared during the period for each share of common stock outstanding.",
                "units":
                    {"USD/shares":
                        [{"start": "2009-01-01",
                        "end": "2009-12-31",
                        "val": 0.2,
                        "accn": "0000019617-12-000163",
                        "fy": 2011,
                        "fp": "FY",
                        "form": "10-K",
                        "filed": "2012-02-29",
                        "frame": "CY2009"},
                        {"start": "2010-01-01",
                        "end": "2010-06-30",
                        "val": 0.1,
                        "accn": "0001193125-11-212045",
                        "fy": 2011,
                        "fp": "Q2",
                        "form": "10-Q",
                        "filed": "2011-08-05"}]}}}},
            {"load_date": "2026-10-19",
             "cik": "0000320193",
             "api_data":
                 {
                     "Assets": {
                         "label": "Assets",
                         "description": "Sum of the carrying amounts as of the balance sheet date of all assets that are recognized",
                         "units":
                             {"USD":
                                  [{"end": "2008-09-27",
                                    "val": 39572000000,
                                    "accn": "0001193125-09-153165",
                                    "fy": 2009,
                                    "fp": "Q3",
                                    "form": "10-Q",
                                    "filed": "2009-07-22"},
                                   {"end": "2008-09-27",
                                    "val": 39572000000,
                                    "accn": "0001193125-09-214859",
                                    "fy": 2009,
                                    "fp": "FY",
                                    "form": "10-K",
                                    "filed": "2009-10-27"}]}},
                     "CommonStockDividendsPerShareDeclared":
                         {"label": "Common Stock, Dividends, Per Share, Declared",
                          "description": "Aggregate dividends declared during the period for each share of common stock outstanding.",
                          "units":
                              {"USD/shares":
                                   [{"start": "2009-09-27",
                                     "end": "2010-09-25",
                                     "val": 0,
                                     "accn": "0001193125-12-444068",
                                     "fy": 2012,
                                     "fp": "FY",
                                     "form": "10-K",
                                     "filed": "2012-10-31"},
                                    {"start": "2009-09-27",
                                     "end": "2010-09-25",
                                     "val": 0,
                                     "accn": "0001193125-13-170623",
                                     "fy": 2012,
                                     "fp": "FY",
                                     "form": "8-K",
                                     "filed": "2013-04-24",
                                     "frame": "CY2010"}]}}}}
            ]