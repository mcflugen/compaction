import click
import yaml

from .compaction import load_config, run_compaction


@click.command()
@click.option(
    "-v", "--verbose", is_flag=True, help="Also emit status messages to stderr."
)
@click.option("--dry-run", is_flag=True, help="do not actually run the model")
@click.option("--config", default=None, type=click.File(mode="r"), help="Configuration file")
@click.argument("input", type=click.File(mode="r"))
@click.argument("output", default="-", type=click.File(mode="w"))
def main(input, output, config, dry_run, verbose):
    params = load_config(config)
    if verbose:
        click.secho(yaml.dump(params, default_flow_style=False), err=True)

    if dry_run:
        click.secho("Nothing to do. 😴", err=True, fg="green")
    else:
        run_compaction(input, output, **params)

        click.secho("💥 Finished! 💥", err=True, fg="green")
        click.secho("Output written to {0}".format(output.name), fg="green")
