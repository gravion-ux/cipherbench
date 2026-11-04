import json

from cipherbench.benchmark import summarize


def test_median_and_invalid_rows():
    out=summarize([{"algorithm":"A","elapsed_ms":2},{"algorithm":"A","elapsed_ms":4},{"algorithm":"A","elapsed_ms":-1}])
    assert out[0]["median_ms"]==3 and out[0]["samples"]==2


def test_boolean_elapsed_is_rejected():
    assert summarize([{"algorithm":"A","elapsed_ms":True}])==[]


def test_non_finite_elapsed_is_rejected():
    out=summarize([{"algorithm":"A","elapsed_ms":float("nan")},{"algorithm":"A","elapsed_ms":float("inf")}])
    assert out==[]
    assert json.dumps(out,allow_nan=False)=="[]"


def test_non_list_root_is_ignored():
    assert summarize({"algorithm":"A","elapsed_ms":1})==[]


def test_non_dict_row_is_ignored():
    assert summarize(["not-a-record"])==[]
