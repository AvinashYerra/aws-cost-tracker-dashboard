import random
from datetime import datetime, timedelta

from sqlalchemy import text

from db.connection import engine


def generate_metric(service, metric, ts):
    """Generate a metric record."""

    metric_ranges = {
        "CPU_UTILIZATION": lambda: round(random.uniform(20, 95), 2),
        "MEMORY_UTILIZATION": lambda: round(random.uniform(30, 90), 2),
        "STORAGE_GB": lambda: round(random.uniform(100, 1000), 2),
        "INVOCATIONS": lambda: random.randint(1000, 50000),
        "ACTIVE_CONNECTIONS": lambda: random.randint(20, 500),
    }

    value = metric_ranges[metric]()

    environment = random.choices(
        ["DEV", "QA", "PROD"],
        weights=[20, 20, 60],
    )[0]

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


def generate_snapshot(ts):
    """Generate a complete infrastructure snapshot."""

    # ts = datetime.utcnow()

    metrics = [
        ("EC2", "CPU_UTILIZATION"),
        ("EC2", "MEMORY_UTILIZATION"),
        ("S3", "STORAGE_GB"),
        ("Lambda", "INVOCATIONS"),
        ("RDS", "ACTIVE_CONNECTIONS"),
    ]

    records = []

    for service, metric in metrics:
        record = generate_metric(service, metric, ts)
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



def load_snapshots(num_snapshots=100):

    all_records = []

    base_time = datetime.utcnow()

    for i in range(num_snapshots):

        snapshot_time = (
            base_time
            - timedelta(minutes=num_snapshots - i)
        )

        all_records.extend(
            generate_snapshot(snapshot_time)
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