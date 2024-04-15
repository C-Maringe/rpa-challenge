import os

from robocorp.tasks import task

from src.main import main


@task
def rpa_challenge():
    current_dir = os.path.dirname(__file__)
    main(current_dir)