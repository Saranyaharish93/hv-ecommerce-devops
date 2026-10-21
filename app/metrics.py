
import time

from flask import Response, request
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    CONTENT_TYPE_LATEST,
    generate_latest,
    multiprocess,
)

REQUEST_COUNT = Counter(
    "flask_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "flask_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

APP_UP = Gauge(
    "flask_app_up",
    "Flask application availability",
    multiprocess_mode="max",
)


def register_metrics(app):

    @app.before_request
    def start_timer():
        request.environ["metrics_start_time"] = time.perf_counter()

    @app.after_request
    def record_metrics(response):
        if request.path == "/metrics":
            return response

        endpoint = request.url_rule.rule if request.url_rule else "unmatched"
        method = request.method

        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status=str(response.status_code),
        ).inc()

        start = request.environ.get("metrics_start_time")
        if start is not None:
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=endpoint,
            ).observe(time.perf_counter() - start)

        return response

    @app.route("/metrics")
    def metrics():
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        APP_UP.set(1)

        return Response(
            generate_latest(registry),
            mimetype=CONTENT_TYPE_LATEST,
        )
