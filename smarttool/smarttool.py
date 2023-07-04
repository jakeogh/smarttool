#!/usr/bin/env python3
# -*- coding: utf8 -*-
# tab-width:4

# pylint: disable=useless-suppression             # [I0021]
# pylint: disable=missing-docstring               # [C0111] docstrings are always outdated and wrong
# pylint: disable=missing-param-doc               # [W9015]
# pylint: disable=missing-module-docstring        # [C0114]
# pylint: disable=fixme                           # [W0511] todo encouraged
# pylint: disable=line-too-long                   # [C0301]
# pylint: disable=too-many-instance-attributes    # [R0902]
# pylint: disable=too-many-lines                  # [C0302] too many lines in module
# pylint: disable=invalid-name                    # [C0103] single letter var names, name too descriptive
# pylint: disable=too-many-return-statements      # [R0911]
# pylint: disable=too-many-branches               # [R0912]
# pylint: disable=too-many-statements             # [R0915]
# pylint: disable=too-many-arguments              # [R0913]
# pylint: disable=too-many-nested-blocks          # [R1702]
# pylint: disable=too-many-locals                 # [R0914]
# pylint: disable=too-many-public-methods         # [R0904]
# pylint: disable=too-few-public-methods          # [R0903]
# pylint: disable=no-member                       # [E1101] no member for base
# pylint: disable=attribute-defined-outside-init  # [W0201]
# pylint: disable=too-many-boolean-expressions    # [R0916] in if statement

from __future__ import annotations

import os
import sys
from pathlib import Path
from signal import SIG_DFL
from signal import SIGPIPE
from signal import signal

import click
import sh
from asserttool import gvd
from asserttool import ic
from asserttool import icp
from click_auto_help import AHGroup
from clicktool import click_add_options
from clicktool import click_global_options
from clicktool import tv
from devicetool import block_devices
from unmp import unmp

sh.mv = None  # use sh.busybox('mv'), coreutils ignores stdin read errors

# this should be earlier in the imports, but isort stops working
signal(SIGPIPE, SIG_DFL)


class NotSmartDeviceError(ValueError):
    pass


def check_device(device: Path) -> bool:
    # smartctl -x "${1}" | /bin/grep -E "(^SMART overall-health self-assessment test result: PASSED|^SMART Health Status: OK|Probable ATA device behind a SAT layer)" || { /home/cfg/sound/beep 10 ; exit 1 ; }
    try:
        _result = sh.smartctl("-x", device).strip()
    except sh.ErrorReturnCode_1 as e:
        icp(e)
        icp(e.args[0])
        if f"{device}: Unable to detect device type" in e.args[0]:
            raise NotSmartDeviceError(device)

    icp(_result)
    if _result.startswith("SMART overall-health self-assessment test result: PASSED"):
        return True
    if _result.startswith("SMART Health Status: OK"):
        return True
    if _result.startswith("Probable ATA device behind a SAT layer"):
        return True
    sys.stdout.write("\a")
    return False


@click.group(no_args_is_help=True, cls=AHGroup)
@click_add_options(click_global_options)
@click.pass_context
def cli(
    ctx,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )
    if not verbose:
        ic.disable()

    if verbose_inf:
        gvd.enable()


@cli.command()
@click.argument("devices", type=str, nargs=-1)
@click_add_options(click_global_options)
@click.pass_context
def check(
    ctx,
    devices: tuple[str, ...],
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )
    if not verbose:
        ic.disable()

    if verbose_inf:
        gvd.enable()

    if not devices:
        iterator = unmp(
            valid_types=(bytes,),
        )
    else:
        iterator = devices

    index = 0
    _k = None
    for index, _mpobject in enumerate(iterator):
        # if isinstance(_mpobject, dict):
        #    for _k, _v in _mpobject.items():
        #        break  # assume single k:v dict
        # else:
        _v = Path(os.fsdecode(_mpobject)).resolve()
        ic(index, _v)
        check_device(_v)


@cli.command()
@click_add_options(click_global_options)
@click.pass_context
def check_all(
    ctx,
    verbose_inf: bool,
    dict_output: bool,
    verbose: bool | int | float = False,
) -> None:
    tty, verbose = tv(
        ctx=ctx,
        verbose=verbose,
        verbose_inf=verbose_inf,
    )
    if not verbose:
        ic.disable()

    if verbose_inf:
        gvd.enable()

    for device in block_devices():
        check_device(device)
