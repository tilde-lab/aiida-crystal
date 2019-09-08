"""An AiiDA node representing CRYSTAL basis set"""
import click
import tabulate
from jsonextended import edict
from click_spinner import spinner as cli_spinner
from aiida.cmdline.commands.cmd_data import verdi_data
from aiida_crystal.aiida_compatibility import get_data_class
from aiida_crystal.cli import options


@verdi_data.group('cry17-basis')
def basis_set():
    """Commandline interface for working with Crystal Basis Set Data"""


@basis_set.command()
@click.option(
    '--content', '-c', is_flag=True, help="include full basis content")
@click.argument('pk', type=int)
def show(pk, content):
    """show the contents of a basis set"""
    from aiida.orm import load_node
    node = load_node(pk)

    if not isinstance(node, get_data_class('crystal.basisset')):
        click.echo("The node was not of type 'crystal.basisset'", err=True)
    else:
        edict.pprint(node.metadata, depth=None, print_func=click.echo)
        if content:
            click.echo("---")
            click.echo(node.content)


def try_grab_description(ctx, param, value):
    """
    Try to get the description from an existing group if it's not given.

    This is a click parameter callback.
    """
    basis_data_cls = get_data_class('crystal.basisset')
    group_name = ctx.params['name']
    existing_groups = basis_data_cls.get_basis_groups()
    existing_group_names = [group.name for group in existing_groups]
    if not value:
        if group_name in existing_group_names:
            return basis_data_cls.get_basis_group(group_name).description
        else:
            raise click.MissingParameter(
                'A new group must be given a description.', param=param)
    return value


# pylint: disable=too-many-arguments
@basis_set.command()
@options.PATH(help='Path to a folder containing the Basis Set files')
@click.option('--ext', default="basis", help="the file extension to filter by")
@options.FAMILY_NAME()
@options.DESCRIPTION(
    help='A description for the family', callback=try_grab_description)
@click.option(
    '--stop-if-existing',
    is_flag=True,
    help='Abort when encountering a previously uploaded Basis Set file')
@options.DRY_RUN()
def uploadfamily(path, ext, name, description, stop_if_existing, dry_run):
    """Upload a family of CRYSTAL Basis Set files."""

    basis_data_cls = get_data_class('crystal.basisset')
    with cli_spinner():
        nfiles, num_uploaded = basis_data_cls.upload_basisset_family(
            path,
            name,
            description,
            stop_if_existing=stop_if_existing,
            extension=".{}".format(ext),
            dry_run=dry_run)

    click.echo(
        'Basis Set files found and added to family: {}, of those {} were newly uploaded'.
        format(nfiles, num_uploaded))
    if dry_run:
        click.echo('No files were uploaded due to --dry-run.')


@basis_set.command()
@click.option(
    '-e',
    '--element',
    multiple=True,
    help='Filter for families containing potentials for all given elements.')
@click.option('-d', '--with-description', is_flag=True)
@click.option('-p', '--list-pks', is_flag=True)
def listfamilies(element, with_description, list_pks):
    """List available families of CRYSTAL Basis Set files."""

    basis_data_cls = get_data_class('crystal.basisset')
    groups = basis_data_cls.get_basis_groups(filter_elements=element)

    table = [['Family', 'Num Basis Sets']]
    if with_description:
        table[0].append('Description')
    if list_pks:
        table[0].append('Pks')
    for group in groups:
        row = [group.label, len(group.nodes)]
        if with_description:
            row.append(group.description)
        if list_pks:
            row.append(",".join([str(n.pk) for n in group.nodes]))
        table.append(row)
    if len(table) > 1:
        click.echo(tabulate.tabulate(table, headers='firstrow'))
        click.echo()
    elif element:
        click.echo(
            'No Basis Set family contains all given elements and symbols.')
    else:
        click.echo('No Basis Set family available.')
