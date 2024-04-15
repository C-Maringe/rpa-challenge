from robocorp.tasks import task

from src.main import main


@task
def rpa_challenge():
    main()
