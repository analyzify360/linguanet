# Commune Subnet Templeate

Subnet template built on top of [CommuneX](https://github.com/agicommies/communex).

Lern how to structure, build and deploy a subnet on [Commune AI](https://communeai.org/)!

## Dependencies

The whole subnet template is built on top of the [CommuneX library / SDK](https://github.com/agicommies/communex).
Which is truly the only essential dependency.

Although in order to make the template more explict we also provide additional libraries.
You can find the whole dependency list we used in the [requirements.txt](./requirements.txt) file.

```txt
communex
typer
uvicorn
keylimiter
pydantic-settings
```

## Miner

```sh
python3 -m src.miner.cli <name-of-your-com-key> [--netuid <number>] [--ip <text>] [--port <number>] [--use-testnet]
```

## Validator

```sh
python3 -m src.validator.cli <name-of-your-com-key> [--netuid <number>] [--call_timeout <number>] [--use-testnet] 
```

## Further reading

For full documentation of the Commune AI ecosystem, please visit the [Official Commune Page](https://communeai.org/), and it's developer documentation. There you can learn about all subnet details, deployment, and more!
