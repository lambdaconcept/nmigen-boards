import os
import subprocess

from nmigen.build import *
from nmigen.vendor.lattice_ecp5 import *
from nmigen_boards.resources import *


__all__ = ["ECPIX5Platform"]


class ECPIX5Platform(LatticeECP5Platform):
    device      = "LFE5UM5G-85F"
    package     = "BG554"
    speed       = "8"
    default_clk = "clk100"
    default_rst = "rst"

    resources   = [
        Resource("rst", 0, PinsN("AB1", dir="i"), Attrs(IO_TYPE="LVCMOS33")),
        Resource("clk100", 0, Pins("K23", dir="i"), Clock(100e6), Attrs(IO_TYPE="LVCMOS33")),

        RGBLEDResource(0, r="U21", g="W21", b="T24", attrs=Attrs(IO_TYPE="LVCMOS33")),
        RGBLEDResource(1, r="T23", g="R21", b="T22", attrs=Attrs(IO_TYPE="LVCMOS33")),
        RGBLEDResource(2, r="P21", g="R23", b="P22", attrs=Attrs(IO_TYPE="LVCMOS33")),
        RGBLEDResource(3, r="K21", g="K24", b="M21", attrs=Attrs(IO_TYPE="LVCMOS33")),

        UARTResource(0,
            rx="R26", tx="R24",
            attrs=Attrs(IO_TYPE="LVCMOS33", PULLMODE="UP")
        ),

        *SPIFlashResources(0,
            cs="AA2", clk="AE3", miso="AE2", mosi="AD2", wp="AF2", hold="AE1",
            attrs=Attrs(IO_TYPE="LVCMOS33")
        ),

        Resource("eth_rgmii", 0,
            Subsignal("rst",     PinsN("C13", dir="o")),
            Subsignal("mdio",    Pins("A13", dir="io")),
            Subsignal("mdc",     Pins("C11", dir="o")),
            Subsignal("tx_clk",  Pins("A12", dir="o")),
            Subsignal("tx_ctrl", Pins("C9", dir="o")),
            Subsignal("tx_data", Pins("D8 C8 B8 A8", dir="o")),
            Subsignal("rx_clk",  Pins("E11", dir="i")),
            Subsignal("rx_ctrl", Pins("A11", dir="i")),
            Subsignal("rx_data", Pins("B11 A10 B10 A9", dir="i")),
            Attrs(IO_TYPE="LVCMOS33")
        ),
        Resource("eth_int", 0, PinsN("B13", dir="i"), Attrs(IO_TYPE="LVCMOS33")),

        *SDCardResources(0,
            clk="P24", cmd="M24", dat0="N26", dat1="N25", dat2="N23", dat3="N21", cd="L22",
            # TODO
            # clk_fb="P25", cmd_dir="M23", dat0_dir="N24", dat123_dir="P26",
            attrs=Attrs(IO_TYPE="LVCMOS33"),
        ),

        # TODO
        # ddr3
        # sata
        # ulpi
    ]

    connectors  = [
        Connector("pmod", 0, "T25 U25 U24 V24 - - T26 U26 V26 W26 - -"),
        Connector("pmod", 4, "E26 D25 F26 F25 - - A25 A24 C26 C25 - -"),
    ]

    @property
    def file_templates(self):
        return {
            **super().file_templates,
            "{{name}}-openocd.cfg": r"""
            interface ftdi
            ftdi_vid_pid 0x0403 0x6010
            ftdi_channel 0
            ftdi_layout_init 0xfff8 0xfffb
            reset_config none
            adapter_khz 25000

            jtag newtap ecp5 tap -irlen 8 -expected-id 0x81113043
            """
        }

    def toolchain_program(self, products, name):
        openocd = os.environ.get("OPENOCD", "openocd")
        with products.extract("{}-openocd.cfg".format(name), "{}.svf".format(name)) \
                as (config_filename, vector_filename):
            subprocess.check_call([openocd,
                "-f", config_filename,
                "-c", "transport select jtag; init; svf -quiet {}; exit".format(vector_filename)
            ])


# if __name__ == "__main__":
#     from .test.blinky import Blinky
#     ECPIX5Platform().build(Blinky(), do_program=True)
