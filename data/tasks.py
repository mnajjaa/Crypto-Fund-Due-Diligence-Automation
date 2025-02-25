
from celery import shared_task
from data.data_pipeline.mobula_pipeline import run_pipeline_to_csv

@shared_task
def fetch_and_process_cryptos():
    run_pipeline_to_csv()
