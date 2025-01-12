"""Prometheus metrics for the NFL Draft Odds Tracker."""
from prometheus_client import Counter, Gauge, Histogram
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# API Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

# Scraper Metrics
ODDS_SCRAPING_DURATION = Histogram(
    "odds_scraping_duration_seconds",
    "Duration of odds scraping operations in seconds"
)

ODDS_SCRAPING_FAILURES = Counter(
    "odds_scraping_failures_total",
    "Total number of failed odds scraping attempts"
)

ODDS_SCRAPING_SUCCESS = Counter(
    "odds_scraping_success_total",
    "Total number of successful odds scraping attempts"
)

ODDS_ENTRIES_COUNT = Gauge(
    "odds_entries_current",
    "Current number of odds entries"
)

odds_scrape_total = Counter(
    "odds_scrape_total",
    "Total number of odds scraping attempts",
    ["status"]  # success or failure
)

odds_scrape_duration_seconds = Histogram(
    "odds_scrape_duration_seconds",
    "Duration of odds scraping operations in seconds"
)

odds_entries_total = Counter(
    "odds_entries_total",
    "Total number of odds entries collected",
    ["sportsbook"]
)

# Cache Metrics
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits"
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total number of cache misses"
)

CACHE_ERRORS = Counter(
    "cache_errors_total",
    "Total number of cache errors"
)

CACHE_SIZE = Gauge(
    "cache_entries_current",
    "Current number of entries in the cache"
)

CACHE_ENTRIES_CLEARED = Counter(
    "cache_entries_cleared_total",
    "Total number of cache entries cleared due to expiration"
)

cache_operations_total = Counter(
    "cache_operations_total",
    "Total number of cache operations",
    ["operation", "status"]  # get/set/delete, hit/miss/error
)

cache_size_bytes = Gauge(
    "cache_size_bytes",
    "Current size of the cache in bytes"
)

# Database Metrics
DB_QUERY_COUNT = Counter(
    "db_queries_total",
    "Total number of database queries"
)

DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Duration of database queries in seconds"
)

DB_CONNECTION_ERRORS = Counter(
    "db_connection_errors_total",
    "Total number of database connection errors"
)

# Initialize FastAPI instrumentator
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)

# Resource Metrics
memory_usage_bytes = Gauge(
    "memory_usage_bytes",
    "Current memory usage in bytes"
)

cpu_usage_percent = Gauge(
    "cpu_usage_percent",
    "Current CPU usage percentage"
)

def init_metrics(app):
    """Initialize metrics collection for the FastAPI application."""
    # Initialize FastAPI instrumentator
    instrumentator = Instrumentator()
    
    # Configure instrumentator with default metrics
    instrumentator.add(
        metrics.request_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    ).add(
        metrics.response_size(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    ).add(
        metrics.latency(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    ).add(
        metrics.requests(
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )
    
    # Instrument the app
    instrumentator.instrument(app)
    
    # Create an info metric
    INFO = Gauge(
        "odds_tracker_app_info",
        "Application information",
        labelnames=["version"]
    )
    INFO.labels(version="1.0.0").set(1)
    
    # Start collecting metrics
    instrumentator.expose(app, include_in_schema=True, should_gzip=True) 