import random
from datetime import datetime, timedelta

from sqlalchemy import text

from db.connection import engine


def generate_metric(service, metric, ts, environment):
    """Generate a metric record."""

    metric_ranges = {
        "DEV": {
            "CPU_UTILIZATION": (20, 50),
            "MEMORY_UTILIZATION": (20, 60),
            "STORAGE_GB": (100, 400),
            "INVOCATIONS": (500, 5000),
            "ACTIVE_CONNECTIONS": (20, 100)
        },
        "QA": {
            "CPU_UTILIZATION": (40, 75),
            "MEMORY_UTILIZATION": (40, 80),
            "STORAGE_GB": (300, 700),
            "INVOCATIONS": (5000, 15000),
            "ACTIVE_CONNECTIONS": (75, 250)
        },
        "PROD": {
            "CPU_UTILIZATION": (60, 95),
            "MEMORY_UTILIZATION": (70, 95),
            "STORAGE_GB": (600, 1200),
            "INVOCATIONS": (15000, 50000),
            "ACTIVE_CONNECTIONS": (200, 500)
        }
    }

    min_val, max_val = metric_ranges[environment][metric]

    if metric in ["CPU_UTILIZATION", "MEMORY_UTILIZATION", "STORAGE_GB"]:
        value = round(random.uniform(min_val, max_val), 2)
    else:
        value = random.randint(min_val, max_val)

    return {
        "timestamp": ts,
        "service": service,
        "metric": metric,
        "value": value,
        "environment": environment,
    }

def calculate_cost(service, value):
    """Calculate estimated cost."""

    cost_factors = {
        "EC2": 0.01,
        "S3": 0.0005,
        "Lambda": 0.00001,
        "RDS": 0.005,
    }

    return round(value * cost_factors.get(service, 0), 4)


def generate_snapshot(ts,environment):
    """Generate a complete infrastructure snapshot."""

    metrics = [
        ("EC2", "CPU_UTILIZATION"),
        ("EC2", "MEMORY_UTILIZATION"),
        ("S3", "STORAGE_GB"),
        ("Lambda", "INVOCATIONS"),
        ("RDS", "ACTIVE_CONNECTIONS"),
    ]


    records = []

    for service, metric in metrics:
        record = generate_metric(
            service,
            metric,
            ts,
            environment
        )
        record["cost"] = calculate_cost(
            record["service"],
            record["value"]
        )
        records.append(record)
    return records


def insert_metrics(records, chunk_size=100):
    """
    Batch insert records into TimescaleDB in chunks.
    """

    query = """
    INSERT INTO cloud_metrics (
        ts,
        service_name,
        metric_name,
        metric_value,
        estimated_cost,
        environment
    )
    VALUES (
        :ts,
        :service,
        :metric,
        :value,
        :cost,
        :environment
    )
    """

    total_inserted = 0
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        params = [
            {
                "ts": record["timestamp"],
                "service": record["service"],
                "metric": record["metric"],
                "value": record["value"],
                "cost": record["cost"],
                "environment": record["environment"],
            }
            for record in chunk
        ]

        with engine.begin() as conn:
            conn.execute(text(query), params)

        total_inserted += len(chunk)

        print(
            f"Inserted chunk "
            f"{i//chunk_size + 1} "
            f"({len(chunk)} records)"
        )

    print(f"Total records inserted: {total_inserted}")



def load_snapshots(num_snapshots):

    all_records = []
    base_time = datetime.utcnow()
    environments = (
        ["DEV"] * int(num_snapshots * 0.2)
        + ["QA"] * int(num_snapshots * 0.2)
        + ["PROD"] * int(num_snapshots * 0.6)
    )
    random.shuffle(environments)
    for i in range(num_snapshots):
        snapshot_time = (
            base_time
            - timedelta(minutes=num_snapshots - i)
        )
        environment = environments[i]
        all_records.extend(
            generate_snapshot(
                snapshot_time,
                environment
            )
        )
    insert_metrics(
        all_records,
        chunk_size=100
    )
    print(
        f"Generated {len(all_records)} records "
        f"from {num_snapshots} snapshots"
    )

if __name__ == "__main__":
    load_snapshots(100)