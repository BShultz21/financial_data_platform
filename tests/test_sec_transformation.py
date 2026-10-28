import datetime
from transformation import sec_bronze_to_silver as sec


def test_sec_flatten_element(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    assert len(compiled_data) == 10

def test__sec_every_row_has_identity_columns(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    for element in compiled_data:
        assert element['load_date'] == datetime.datetime(2026, 10, 19, 0, 0)
        assert element['cik']
        assert element['taxonomy'] == 'us-gaap'
        assert element['unit']
        assert element['conceptfact']

def test_sec_known_value(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    assert compiled_data[1]['conceptfact'] == 'AffordableHousingTaxCreditsAndOtherTaxBenefitsAmount'
    assert compiled_data[1]['value'] == 1200000000
    assert compiled_data[1]['accountnum'] == '0000019617-15-000464'

def test_sec_data_types(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    for element in compiled_data:
        assert type(element['load_date']) == datetime.datetime
        assert type(element['cik'] == int)
        assert type(element['taxonomy']) == str
        assert type(element['conceptfact']) == str
        assert type(element['unit']) == str
        if element['start_date']:
            assert type(element['start_date']) == datetime.datetime
        assert type(element['end_date']) == datetime.datetime
        assert type(element['value']) == float
        assert type(element['accountnum']) == str
        assert type(element['fy']) == int
        assert type(element['fp']) == str
        assert type(element['form']) == str
        assert type(element['filed']) == datetime.datetime
        if element['frame']:
            assert type(element['frame']) == str

def test_sec_data_quality(sec_data):
    compiled_data = []
    for row in sec_data:
        data,row_count = sec.flatten_element(row)
        compiled_data.extend(data)

    for element in compiled_data:
        if element['start_date']:
            assert element['end_date'] >= element['start_date']

        assert element['filed'] >= element['end_date']
        assert element['form'] in ['10-K', '10-Q', '8-K', '10-Q/A', '10-K/A']
        assert element['fp'] in ['FY', 'Q1', 'Q2', 'Q3', 'Q4']