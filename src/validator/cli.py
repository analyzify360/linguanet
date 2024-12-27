import typer 
import getpass
from typing import Annotated

from communex._common import get_node_url  # type: ignore
from communex.client import CommuneClient  # type: ignore
from communex.compat.key import classic_load_key  # type: ignore

from ._config import ValidatorSettings
from .validator import Validator

app = typer.Typer()


@app.command("serve-subnet")
def serve(
    commune_key: Annotated[str, typer.Argument(help="Name of the key present in `~/.commune/key`")],
    netuid: int = typer.Option(35, help="Netuid of the subnet"),
    use_testnet: bool = typer.Option(Flase, help="Use testnet"),
    call_timeout: int = 65,
):
    password = getpass.getpass(prompt = "Enter the password to decrypt your key:")
    keypair = classic_load_key(commune_key, password=password)  # type: ignore
    settings = ValidatorSettings()  # type: ignore
    c_client = CommuneClient(get_node_url(use_testnet=use_testnet))
    validator = Validator(
        keypair,
        netuid,
        c_client,
        call_timeout,
    )
    validator.validation_loop(settings)


if __name__ == "__main__":
    typer.run(serve)
