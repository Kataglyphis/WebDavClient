# Copyright (c) 2024 Jonas Heinle

"""Integration test for the dummy ML preprocessing pipeline."""

import numpy as np
import pytest

from kataglyphis_webdavclient.dummy import SimpleMLPreprocessor


def test_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify pipeline output structure and deterministic labels."""

    def _mock_random_normal(*_args: object, **_kwargs: object) -> np.ndarray:
        return np.array(
            [
                [5.5, 5.5, 5.5],
                [1.0, 1.0, 1.0],
                [7.0, 5.0, 4.0],
                [6.0, 4.0, 6.0],
            ]
        )

    class _FixedGenerator:
        """Stands in for a numpy Generator, returning the fixture above."""

        normal = staticmethod(_mock_random_normal)

    def _mock_default_rng(*_args: object, **_kwargs: object) -> _FixedGenerator:
        return _FixedGenerator()

    # SimpleMLPreprocessor calls np.random.default_rng().normal(...), the
    # Generator API. Patching the LEGACY numpy.random.normal here intercepted
    # nothing, so the pipeline ran on real random data and the label assertion
    # below was a coin flip: each row is a sum of three N(5, 2) draws tested
    # against 15, so [1, 0, 1, 1] came up about one run in sixteen.
    monkeypatch.setattr(
        "numpy.random.default_rng",
        _mock_default_rng,
    )

    ml = SimpleMLPreprocessor(4)
    result = ml.run_pipeline()

    assert result["features"].shape == (4, 3)
    assert result["labels"].tolist() == [1, 0, 1, 1]
    assert "mean" in result
    assert "std" in result
    assert result["joke_labels"].tolist() == [
        "Definitely ML",
        "Possibly Not",
        "Definitely ML",
        "Definitely ML",
    ]
