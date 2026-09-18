import os, numpy as np, pytest
from src.common.data import load_data, slice_run, metric_mask, internal_mask
from src.common.metrics import nse, kge

def test_load():
    df = load_data()
    assert df.shape == (14610, 4) and (df[["P", "PET", "Q"]] >= 0).all().all()

def test_eval_guard():
    df = load_data(); os.environ.pop("LR_AGENT", None)
    with pytest.raises(PermissionError):
        slice_run(df, "evaluation", allow_evaluation=True)

def test_eval_window():
    os.environ["LR_AGENT"] = "a16"
    ev = slice_run(load_data(), "evaluation", allow_evaluation=True)
    os.environ.pop("LR_AGENT")
    assert len(ev) == 1095 and metric_mask(ev, "evaluation").sum() == 1003

def test_no_overlap():
    df = load_data(); cal = slice_run(df, "calibration")
    assert cal["row"].min() >= 1360
    assert internal_mask(cal, "train").sum() + internal_mask(cal, "validation").sum() == metric_mask(cal, "calibration").sum()

def test_perfect_metrics():
    o = np.random.rand(100) + 1
    assert nse(o, o) == pytest.approx(1) and kge(o, o) == pytest.approx(1)
