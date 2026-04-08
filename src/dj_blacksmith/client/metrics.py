from typing import Any

from blacksmith import PrometheusMetrics

_prom_metrics = None


def build_metrics(settings: dict[str, Any]) -> PrometheusMetrics:
    global _prom_metrics
    if _prom_metrics is None:
        metrics = settings.get("metrics", {})
        _prom_metrics = PrometheusMetrics(**metrics)
    return _prom_metrics
