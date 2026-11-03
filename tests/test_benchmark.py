from cipherbench.benchmark import summarize


def test_median_and_invalid_rows():
    out=summarize([{"algorithm":"A","elapsed_ms":2},{"algorithm":"A","elapsed_ms":4},{"algorithm":"A","elapsed_ms":-1}])
    assert out[0]["median_ms"]==3 and out[0]["samples"]==2
