"""In paradise, EVE and python work together.

This module contains interfaces to read EVE CSS h5 measurement files. There are three different interfaces:
* If the scan consists of the standard sequence of
  1. Save motor positions
  2. Save detector values
  3. Scan
  4. Save detector values
  use the StandardMeasurement class. It provides a high-level interface to the most-commonly used information and data,
  e.g.:
  > m = StandardMeasurement(filename)
  > m.plot()
  > m.data
  > m.start
  Full documentation is in the docstring of StandardMeasurement.

* If the scan is in a different format (multiple chains, snapshots at different positions, etc.), you can use the class
  EVEMeasurement, which provides a more flexible interface, which is less convenient:
  > m = EVEMeasurement(filename)
  > m.plot()
  > m.selected_chain = 2
  > m.plot()
  > m.standard_data
  Full documentation is in the docstring of EVEMeasurement.

* If parsing with EVEMeasurement fails or you want direct access, you can also use the function parse_eve_hdf5 directly.
  It returns the EVE h5 hierarchy as a dict with different keys, for documentation see the docstring of parse_eve_hdf5.

If possible, always use StandardMeasurement, or, for non-standard scans, EVEMeasurement. Use parse_eve_hdf5 only if you
have to.
"""

__author__ = "Mika Pflüger <mika.pflueger@ptb.de>"
__version__ = "2018-01-31"

import datetime
import logging
import os
import os.path

import h5py
import numpy as np
import pandas as pd


# TODO: parsing failes with oom if index (PosCounter) contains lots of NaNs, which result in a very large join


def _attrs_to_dict(attrs):
    ret = dict()
    for key, val in attrs.items():
        if len(val) == 1:
            ret[key] = val[0].decode("latin-1")
        else:
            ret[key] = [x.decode("latin-1") for x in val]
    return ret


def _process_group(group: h5py.Group):
    logging.debug("Processing group %r", group.name)
    children = {}
    data_dfs = {}
    metadata = {}
    joindata = True
    for name, child in group.items():
        logging.debug("Processing child %r", name)
        if isinstance(child, h5py.Dataset) or "XML-ID" in child.attrs:
            # we process leaf Datasets directly
            info = _attrs_to_dict(child.attrs)
            # if an EVE channel is a H5 group, we need to parse it as a series of arrays
            if isinstance(child, h5py.Group):
                index = []
                data = []
                for pos_counter, val in child.items():
                    index.append(int(pos_counter))
                    data.append(val[...])
                df = pd.DataFrame(
                    pd.Series(index=index, data=data, name=name)
                )
            else:  # simple channel, can be directly parsed as DataFrame
                df = pd.DataFrame(child[...])
                if "PosCounter" in df.columns:
                    df.set_index("PosCounter", inplace=True)
                else:
                    df.set_index(df.columns[0], inplace=True)
                    joindata = False
                # convert from bytes to python strings
                for col in df.columns:
                    if df[col].dtype == np.object_:
                        df[col] = df[col].str.decode("utf-8")

            if group.name.endswith("/averagemeta") or group.name.endswith(
                "/standarddev"
            ):  # special metadata group
                # we need to rename the columns to be unique in the group
                if "Channel" in info:
                    channel = info["Channel"]
                else:
                    channel = name.rsplit("__", 1)[0]
                df.rename(
                    columns={col: channel + "_" + col for col in df.columns},
                    inplace=True,
                )

                try:
                    if name.rsplit("__", 1)[1] == "Count":
                        # in count datasets in /standdarddev groups sometimes hides a column called like the channel
                        # which is the actual standard deviation
                        df.rename(
                            columns={
                                channel
                                + "_"
                                + channel: channel
                                + "_StandardDeviation"
                            },
                            inplace=True,
                        )
                except ValueError:
                    pass

            if "Name" in info:
                if (
                    len(df.columns) == 1
                ):  # single column, rename it unconditionally
                    df.rename(
                        columns={df.columns[0]: info["Name"]}, inplace=True
                    )
                else:  # multiple columns, rename only columns with matching names.
                    df.rename(columns={name: info["Name"]}, inplace=True)
                    if "XML-ID" in info:
                        df.rename(
                            columns={info["XML-ID"]: info["Name"]},
                            inplace=True,
                        )
                name = info["Name"]
            data_dfs[name] = df
            metadata[name] = info

        elif isinstance(child, h5py.Group):
            # subgroups are parsed recursively
            children[name] = _process_group(child)

        else:  # ??
            logging.warning("Unknown H5 node: {!r}, skipping.".format(name))

    logging.debug("Finishing group %r", group.name)
    ret = dict()
    if children:
        ret["children"] = children
    ret["info"] = _attrs_to_dict(group.attrs)
    if data_dfs:
        if joindata:
            # we use df.join instead of pd.concat because pd.concat refuses to work on indices containing PosCounter
            # multiple times, but those happen in real files in the wild.
            data_dfs = list(data_dfs.values())
            df = data_dfs[0]
            df = df.join(data_dfs[1:], how="outer")
            ret["data"] = df
            ret["metadata"] = metadata
        else:
            ret["data"] = data_dfs
            ret["metadata"] = metadata
    return ret


def parse_eve_hdf5(filename):
    """Low-level interface to parse an EVE h5 file into native python datatypes. Useful if you need the exact structure
    of the underlying EVE h5 file or higher-level interfaces don't work for your h5 file.

    Returns a tree structure closely following the h5 file with each group node represented as a dict:
    {'data': leaves-DataFrame OR {leaf: leaf-DataFrame},
     'metadata': {leaf: attributes-dict},
     'info': hdf-attributes-dict,
     'children': {subgroup-name: subgroup}}
    with the following fields:
      'data': included only if the group contains h5 Datasets. If all Datasets share PosCountTimer as index, the data
              is joined (but not filled) in a single pandas DataFrame with PosCountTimer as index and the individual
              Datasets as columns. Otherwise, the data is a dict of DataFrames, with the key being the name of the h5
              leaf.
      'metadata': included only if the group contains h5 Datasets. Is a dict with the leaf names as keys and their
              parsed h5 attributes (represented as dict) as values.
      'info': the parsed h5 attributes of the group itself.
      'children': included only if the group contains other h5 Groups. Is a dict with the group names as keys and the
              group node dict as value.
    group names are always the last-level h5 names, while leafs use their 'Name' h5 attr if it available and h5 names
    otherwise.
    """
    with h5py.File(filename, "r") as h5:
        # strategy: we recursively walk all groups and leafs, joining all leafs in a group into a single DataFrame
        # if possible
        return _process_group(h5["/"])


def _parse_datetime(info):
    if "StartDate" in info and "StartTime" in info:
        return datetime.datetime.strptime(
            " ".join((info.pop("StartDate"), info.pop("StartTime"))),
            "%d.%m.%Y %H:%M:%S",
        )
    else:
        return None


class EVEMeasurement:
    """Class to read EVE Measurements. Can be used to read any measurement produced by EVECSS.
    Usage:
    read in file:
    > m = EVEMeasurement(filename)

    access to data:
    the three different types of time-based measurements (standard, snapshot, timestamp) can be accessed directly:
    > m.standard_data
    > m.snapshot_data
    > m.timestamp_data
    units for the measured data are available in
    > m.units
    by default, access to the first chain (usually, c1) is provided, but you can also change which chain is accessed:
    > m.selected_chain = 2
    or, you can access all chains in a list via m.chains.
    All data are in pandas DataFrames.

    Some information is collected and can be accessed directly:
    > m.comment: The comment as set in the scan, plus the live comment in braces, if a live comment was provided.
    > m.evedataviewer
    > m.start
    > m.preferred_axis: preferred motor axis (e.g. for plotting)
    > m.preferred_channel: preferred measurement channel (e.g. for plotting)
    > m.preferred_normalization_channel: preferred normalization for preferred channel
    > m.eve_h5_version
    > m.eve_version
    > m.eve_xml_version

    If the scan containes monitored devices, the measurements are available via
    > m.monitor
    as a dict with the CA names as keys and the measurements as values or via
    > m.monitor_joined
    as a joined pandas DataFrame.

    All further information that is collected from the EVE file is accessible via
    > m.info: file-wide information
    > m.chain.info: chain-specific information
    > m.standard_metadata: metadata about the columns
    > m.snapshot_metadata
    > m.timestamp_metadata
    > m.standard_motors: list of motors in m.standard_data
    > m.standard_sensors: list of sensors in m.standard_data
    > m.snapshot_motors
    > m.snapshot_sensors

    Plotting is available (via pandas) directly:
    > m.plot()
    for documentation see pandas.DataFrame.plot, with the exception that if there are preferred axis and/or channels
    (m.preferred_axis, m.preferred_channel, m.preferred_normalization_channel), they are selected for plotting
    if x and/or y are not specified.
    """

    def __init__(self, filename):
        self.filename = filename
        h5 = parse_eve_hdf5(filename)
        # Parse the most useful/important attributes for direct access
        # access via info dict for the less important attributes
        self.info = h5["info"]

        # The attributes of the file itself
        self.eve_h5_version = float(self.info.pop("EVEH5Version", 1.0))
        # using None or sensible defaults as default for non-vital attributes
        self.eve_version = self.info.pop("Version", None)
        self.eve_xml_version = self.info.pop("XMLversion", None)
        self.evedataviewer = self.info.pop("evedataviewer", None)
        self.comment = self.info.pop("Comment", os.path.basename(filename))

        self.location = self.info.pop("Location", None)

        if "Live-Comment" in self.info:
            self.comment = "{} (live: {})".format(
                self.comment, self.info.pop("Live-Comment")
            )

        self.start = _parse_datetime(self.info)

        # put chains into structure for direct access
        self.chains = []
        chain_names = sorted(
            [
                x
                for x in h5["children"]
                if x.startswith("c") and x[1:].isdigit()
            ]
        )
        for cname in chain_names:
            self.chains.append(
                Chain(
                    h5["children"][cname], eve_h5_version=self.eve_h5_version
                )
            )

        # if we have monitored devices, put them into a structure for direct access
        self.monitor = {}
        if "device" in h5["children"]:
            for name, df in h5["children"]["device"]["data"].items():
                if (
                    self.start is not None
                    and df.index.name == "mSecsSinceStart"
                ):
                    df.index = pd.to_datetime(
                        df.index + self.start.timestamp() * 1000, unit="ms"
                    )
                    df.index.name = "datetime"
                self.monitor[name] = df

        if not self.monitor:
            self.monitor_joined = None
        else:
            dfs = iter(self.monitor.values())
            df = next(dfs)
            self.monitor_joined = df.join(dfs, how="outer")

        if len(self.chains):
            self.selected_chain = 1
        else:
            self.selected_chain = None

    @property
    def chain(self):
        return self.chains[self.selected_chain - 1]

    # delegate access to selected chain.
    def __getattr__(self, item):
        return getattr(self.chain, item)

    def __dir__(self):
        return list(self.__dict__.keys()) + dir(self.chain)

    def __str__(self):
        ret = "<EVEMeasurement file: {!r}, comment: {}, start: {}, evedataviewer: {}, chains: [{}]".format(
            self.filename,
            self.comment,
            self.start,
            self.evedataviewer,
            ", ".join((str(chain) for chain in self.chains)),
        )
        if self.monitor:
            ret += ", monitor: {}".format(list(self.monitor.keys()))
        return ret + ">"


class Chain:
    """Represents a single chain. Documentation see EVEMeasurement."""

    def __init__(self, chain, eve_h5_version: float):
        # parse the most useful/important attributes for direct access, info dict for the rest.
        self.info = chain["info"]
        self.start = _parse_datetime(self.info)
        # these are raw, XML-names
        self._preferred_axis = self.info.pop("preferredAxis", None)
        self._preferred_channel = self.info.pop("preferredChannel", None)
        self._preferred_normalization_channel = self.info.pop(
            "preferredNormalizationChannel", None
        )

        # parse the measurements into the sections standard, snapshot, and timestamp
        # add timestamp information to standard and snapshot data, keep timestamp for reference

        # eve version 1 directly contains all measurements in the chain node and doesn't know the snapshot section
        if eve_h5_version < 2.0:
            standard_group = chain
            snapshot_group = None

        else:
            # for versions >= 2, the standard section is named either 'default' or 'main'
            standard_group = (
                chain["children"]["default"]
                if "default" in chain["children"]
                else chain["children"]["main"]
            )
            # and the snapshot section is named either 'alternate' or 'snapshot'
            snapshot_group = (
                chain["children"]["alternate"]
                if "alternate" in chain["children"]
                else chain["children"]["snapshot"]
            )
        if "data" in standard_group:
            self.standard_data = standard_group["data"]
        else:
            self.standard_data = pd.DataFrame()
        if "metadata" in standard_group:
            self.standard_metadata = standard_group["metadata"]
        else:
            self.standard_metadata = {}
        if snapshot_group is None:
            self.snapshot_data = None
            self.snapshot_metadata = None
        else:
            self.snapshot_data = snapshot_group["data"]
            self.snapshot_metadata = snapshot_group["metadata"]
        try:
            self.timestamp_data = chain["children"]["meta"]["data"]
            self.timestamp_metadata = chain["children"]["meta"]["metadata"]
            self.timestamp_data["PosCountTimer"] = pd.to_timedelta(
                self.timestamp_data["PosCountTimer"], unit="ms"
            )
            self.standard_data = self.standard_data.join(
                self.timestamp_data, how="left"
            )
            self.standard_metadata.update(self.timestamp_metadata)
            if self.snapshot_data is not None:
                self.snapshot_data = self.snapshot_data.join(
                    self.timestamp_data, how="left"
                )
                self.snapshot_metadata.update(self.timestamp_metadata)
        except KeyError:
            self.timestamp_data = None
            self.timestamp_metadata = None

        # if we have normalized channels, add them to the standard data with the suffix '_norm'
        if (
            "children" in standard_group
            and "normalized" in standard_group["children"]
            and "data" in standard_group["children"]["normalized"]
        ):
            norm = standard_group["children"]["normalized"]
            norm["data"].rename(
                columns={col: col + "_norm" for col in norm["data"].columns},
                inplace=True,
            )
            self.standard_data = self.standard_data.join(
                norm["data"], how="outer"
            )
            for key, val in norm["metadata"].items():
                self.standard_metadata[key + "_norm"] = val

        # build translation from raw, XML-names to human-readable names
        # and map of units
        self._name_translation = dict()
        self.units = dict()
        # we need to collect all units first, then correct wrong ones
        norm_unit_needs_correction = []
        for metadata in (
            self.standard_metadata,
            self.snapshot_metadata,
            self.timestamp_metadata,
        ):
            if metadata is None:
                continue
            for name, meta in metadata.items():
                if "XML-ID" in meta:
                    self._name_translation[meta["XML-ID"]] = name

                unitname = "unit" if "unit" in meta else "Unit"
                if unitname in meta:
                    self.units[name] = meta[unitname]

                    if name.endswith("_norm"):
                        norm_unit_needs_correction.append((name, meta))

        # need to correct units of normalized channels
        for name, meta in norm_unit_needs_correction:
            nid = (
                "NormalizeChannelID"
                if "NormalizeChannelID" in meta
                else "normalizeId"
            )
            try:
                normalize_unit = self.units[self._name_translation[meta[nid]]]
                self.units[name] = " / ".join(
                    (self.units[name], normalize_unit)
                )
            except KeyError:
                self.units[name] = " / ".join((self.units[name], "1"))

        # if we have stddev channels, add them to the standard data with the respective suffix
        if (
            "children" in standard_group
            and "standarddev" in standard_group["children"]
        ):
            logging.debug("Adding standarddev information")
            stddev = standard_group["children"]["standarddev"]
            stddev_meta = stddev["metadata"]
            df = stddev["data"]
            typ_trans = {
                "Count": "_stddev_count",
                "StandardDeviation": "_stddev",
                "TriggerIntv": "_stddev_trigger_interval",
            }
            renames = {}
            for col in df.columns:
                cachannel, typ = col.rsplit("_", 1)
                typ = typ_trans[typ]
                # if cachannel contains '__', the channel is likely normalized and we have to look in stddev_meta for
                # the normalization channel
                channel = None
                if "__" in cachannel:
                    cachannel_part, canorm_part = cachannel.rsplit("__", 1)
                    try:
                        channel_part = self._name_translation[cachannel_part]
                        channel_meta = stddev_meta[channel_part]
                        nid = (
                            "NormalizeChannelID"
                            if "NormalizeChannelID" in channel_meta
                            else "normalizeId"
                        )
                        if (
                            nid in channel_meta
                        ):  # channel is actually normalized
                            norm_part = self._name_translation[canorm_part]
                            channel = "/".join((channel_part, norm_part))
                    except KeyError:
                        pass

                if channel is None:
                    channel = self._name_translation[cachannel]

                renames[col] = channel + typ

            df.rename(columns=renames, inplace=True)
            self.standard_data = self.standard_data.join(df, how="left")

        # if we have averagemeta channels, add them to the standard data with the suffix _av_*
        if (
            "children" in standard_group
            and "averagemeta" in standard_group["children"]
        ):
            logging.debug("Adding averagemeta information")
            avmeta = standard_group["children"]["averagemeta"]
            avmeta_meta = avmeta["metadata"]
            df = avmeta["data"]
            typ_trans = {
                "AverageCount": "_av_count",
                "Attempts": "_av_attempts",
                "Limit": "_av_limit",
                "maxDeviation": "_av_max_deviation",
                "MaxAttempts": "_av_max_attempts",
                "Preset": "_av_preset",
            }
            renames = {}
            for col in df.columns:
                cachannel, typ = col.rsplit("_", 1)
                typ = typ_trans[typ]
                # if cachannel contains '__', the channel is likely normalized and we have to look in avmeta_meta for
                # the normalization channel
                channel = None
                if "__" in cachannel:
                    cachannel_part, canorm_part = cachannel.rsplit("__", 1)
                    try:
                        channel_part = self._name_translation[cachannel_part]
                        channel_meta = avmeta_meta[channel_part]
                        nid = (
                            "NormalizeChannelID"
                            if "NormalizeChannelID" in channel_meta
                            else "normalizeId"
                        )
                        if (
                            nid in channel_meta
                        ):  # channel is actually normalized
                            norm_part = self._name_translation[canorm_part]
                            channel = "/".join((channel_part, norm_part))
                    except KeyError:
                        pass

                if channel is None:
                    channel = self._name_translation[cachannel]

                renames[col] = channel + typ

            df.rename(columns=renames, inplace=True)

            self.standard_data = self.standard_data.join(df, how="left")

        # generate a list of motors and sensors for snapshots as well as standard data
        self.standard_motors = [
            k
            for (k, v) in self.standard_metadata.items()
            if v.get("DeviceType") == "Axis"
        ]
        self.standard_sensors = [
            k
            for (k, v) in self.standard_metadata.items()
            if v.get("DeviceType") == "Channel"
        ]
        self.snapshot_motors = [
            k
            for (k, v) in self.snapshot_metadata.items()
            if v.get("DeviceType") == "Axis"
        ]
        self.snapshot_sensors = [
            k
            for (k, v) in self.snapshot_metadata.items()
            if v.get("DeviceType") == "Channel"
        ]

        self.preferred_axis = self._name_translation.get(
            self._preferred_axis, self._preferred_axis
        )
        self.preferred_channel = self._name_translation.get(
            self._preferred_channel, self._preferred_channel
        )
        self.preferred_normalization_channel = self._name_translation.get(
            self._preferred_normalization_channel,
            self._preferred_normalization_channel,
        )

    def plot(self, x=None, y=None, **kwargs):
        """Plotting standard data, documentation see pandas.DataFrame.plot, the only difference is that if x and/or
        y are not given, the preferred_axis and preferred_channel are used."""
        if x is None and self.preferred_axis is not None:
            x = self.preferred_axis
        if y is None and self.preferred_channel is not None:
            if self.preferred_channel + "_norm" in self.standard_data.columns:
                y = self.preferred_channel + "_norm"
            else:
                y = self.preferred_channel

        ax = self.standard_data.plot(x=x, y=y, **kwargs)

        if isinstance(x, str) and x in self.units:
            ax.set_xlabel("{} / {}".format(x, self.units[x]))

        if isinstance(y, str) and y in self.units:
            ax.set_ylabel("{} / {}".format(y, self.units[y]))
            ax.legend_.remove()

        return ax

    def __str__(self):
        ret = "<Chain start: {start}, channels: {channels}".format(
            start=self.start, channels=list(self.standard_data.columns)
        )
        if self.preferred_axis is not None:
            ret += ", preferred_axis: {!r}".format(self.preferred_axis)
        if self.preferred_channel is not None:
            ret += ", preferred_channel: {!r}".format(self.preferred_channel)
        if self.preferred_normalization_channel is not None:
            ret += ", preferred_normalization_channel: {!r}".format(
                self.preferred_normalization_channel
            )
        ret += ">"
        return ret


class MotorsSensorsScanSensorsMeasurement(EVEMeasurement):
    """Class to read "standard" scans which consist of:
    1. Save motor positions
    2. Save detector values
    3. The scan itself (with one or more scan modules)
    4. Save detector values again.

    Read file:
    > m = StandardMeasurement(filename)

    The saved motor/detector positions are available as a dict:
    > m.snapshot_before
    > m.snapshot_after

    The scan data is available as a pandas DataFrame, already filled in the motor axes and joined:
    > m.data
    the units of the columns are available as well:
    > m.units

    Some information is collected and can be accessed directly:
    > m.comment: The comment as set in the scan, plus the live comment in braces, if a live comment was provided.
    > m.evedataviewer
    > m.start
    > m.preferred_axis: preferred motor axis (e.g. for plotting)
    > m.preferred_channel: preferred measurement channel (e.g. for plotting)
    > m.preferred_normalization_channel: preferred normalization for preferred channel
    > m.eve_h5_version
    > m.eve_version
    > m.eve_xml_version

    If the scan contains monitored devices, the measurements are available via
    > m.monitor
    as a dict with the CA names as keys and the measurements as values or via
    > m.monitor_joined
    as a joined pandas DataFrame.

    All further information that is collected from the EVE file is accessible via
    > m.info: file-wide information
    > m.metadata
    > m.snapshot_metadata

    Plotting is available (via pandas) directly:
    > m.plot()
    for documentation see pandas.DataFrame.plot, with the exception that if there are preferred axis and/or channels
    (m.preferred_axis, m.preferred_channel, m.preferred_normalization_channel), they are selected for plotting
    if x and/or y are not specified.

    If ignore_too_many_snapshots is True (default: False), no error will be raised if there are more than 2 measurements
    in a snapshot section.

    """

    def __init__(self, filename, ignore_too_many_snapshots=False):
        EVEMeasurement.__init__(self, filename)

        if len(self.chains) > 1:
            logging.warning(
                "Loading {!r} using StandardMeasurement class, but file contains more than one chain. "
                "Maybe you want to use the more generic EVEMeasurement class?".format(
                    filename
                )
            )

        # put the values right before the measurement in snapshot_before and those right after in snapshot_after.
        self.snapshot_before = {}
        self.snapshot_after = {}
        for col in self.snapshot_data.columns:
            if col == "PosCountTimer":
                continue
            nadropped = self.snapshot_data.loc[:, col].dropna()
            if len(nadropped) == 1:
                self.snapshot_before[col] = nadropped.iloc[0]
            elif len(nadropped) == 2 or (
                ignore_too_many_snapshots and len(nadropped) > 2
            ):
                self.snapshot_before[col] = nadropped.iloc[0]
                self.snapshot_after[col] = nadropped.iloc[1]
            else:
                raise ValueError(
                    "Snapshot of sensor/motor {!r} has {} data points, we expected 1 or 2. Maybe you want"
                    " to use the more generic EVEMeasurement class?".format(
                        col, len(nadropped)
                    )
                )

        self.data = self.standard_data
        for motor in self.standard_motors:
            self.data.loc[:, motor].ffill()  # fillna(method='ffill',
            # inplace=True)
        self.data = self.data[~self.data.index.duplicated(keep="first")]
        self.metadata = self.standard_metadata

    def __str__(self):
        ret = (
            "<StandardMeasurement file: {filename!r}, comment: {comment}, start: {start}, evedataviewer: {evedataviewer}, "
            "channels: {channels}".format(
                filename=self.filename,
                comment=self.comment,
                start=self.start,
                evedataviewer=self.evedataviewer,
                channels=list(self.data.columns),
            )
        )
        if self.preferred_axis is not None:
            ret += ", preferred_axis: {!r}".format(self.preferred_axis)
        if self.preferred_channel is not None:
            ret += ", preferred_channel: {!r}".format(self.preferred_channel)
        if self.preferred_normalization_channel is not None:
            ret += ", preferred_normalization_channel: {!r}".format(
                self.preferred_normalization_channel
            )
        if self.monitor:
            ret += ", monitor: {}".format(list(self.monitor.keys()))
        return ret + ">"


StandardMeasurement = MotorsSensorsScanSensorsMeasurement


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import sys

    # print(parse_eve_hdf5(sys.argv[1]))
    print(StandardMeasurement(sys.argv[1]).data.columns)
