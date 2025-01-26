import boto3
from datetime import datetime, timedelta
import pandas as pd
import dotenv
import os


def get_route53_storage_data(start_date: str, end_date: str, resource_name: str):
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    ce_client = boto3.client(
        "ce",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_access_key,
        region_name="ap-southeast-1",
    )

    response = ce_client.get_cost_and_usage(
        TimePeriod={"Start": start_date, "End": end_date},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        Filter={"Dimensions": {"Key": "SERVICE", "Values": [resource_name]}},
        GroupBy=[
            {"Type": "DIMENSION", "Key": "USAGE_TYPE"},
        ],
    )
    print(response)

    storage_data = []

    for time_period in response["ResultsByTime"]:
        for group in time_period["Groups"]:
            usage_type = group["Keys"][0]
            cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
            # if usage_type in [
            #     "HostedZone",
            #     "DNS-Queries",
            # ]:
            storage_data.append(
                {
                    "start_date": time_period["TimePeriod"]["Start"],
                    "end_date": time_period["TimePeriod"]["End"],
                    "resource_name": resource_name,
                    "service": usage_type,
                    "unblended_cost": cost,
                }
            )

    return storage_data


def main():
    print("running...")
    dotenv.load_dotenv()

    end_date = "2025-01-20"
    start_date = "2024-12-28"

    route53_storage_data = get_route53_storage_data(
        start_date, end_date, "Amazon Route 53"
    )
    storage_df = pd.DataFrame(route53_storage_data)

    print("Route 53 Storage Usage:")
    print(storage_df)


if __name__ == "__main__":
    main()
