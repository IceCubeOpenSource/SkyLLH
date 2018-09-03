# -*- coding: utf-8 -*-

"""The source_hypothesis module provides classes to define groups of source
hypotheses. The SourceHypoGroupManager manages the groups of source hypotheses.
"""

from skylab.core.py import issequenceof
from skylab.core.detsigeff import DetSigEffImplMethod
from skylab.physics.source import SourceModel
from skylab.physics.flux import FluxModel


class SourceHypoGroup(object):
    """The source hypothesis group class provides a data container to describe
    a group of sources that share the same flux model and detector signal
    efficiency implementation method.
    """
    def __init__(self, sources, fluxmodel, detsigeff_implmethod):
        """Constructs a new source hypothesis group.

        Parameters
        ----------
        sources : SourceModel | sequence of SourceModel
            The source or sequence of sources that define the source group.
        fluxmodel : instance of FluxModel
            The FluxModel instance that applies to the list of sources of the
            group.
        detsigeff_implmethod : instance of DetSigEffImplMethod
            The instance of a detector signal efficiency implementation method,
            which should be used to create the detector signal efficiency for
            the sources of the group.
        """
        self.source_list = sources
        self.fluxmodel = fluxmodel
        self.detsigeff_implmethod = detsigeff_implmethod

    @property
    def source_list(self):
        """The list of SourceModel instances for which the group is defined.
        """
        return self._source_list
    @source_list.setter
    def source_list(self, sources):
        if(isinstance(sources, SourceModel)):
            sources = [sources]
        if(not issequenceof(sources, SourceModel)):
            raise TypeError('The source_list property must be an instance of SourceModel or a sequence of SourceModel instances!')
        self._source_list = list(sources)

    @property
    def fluxmodel(self):
        """The FluxModel instance that applies to the list of sources of this
        source group.
        """
        return self._fluxmodel
    @fluxmodel.setter
    def fluxmodel(self, fluxmodel):
        if(not isinstance(fluxmodel, FluxModel)):
            raise TypeError('The fluxmodel property must be an instance of FluxModel!')
        self._fluxmodel = fluxmodel

    @property
    def detsigeff_implmethod(self):
        """The instance of DetSigEffImplMethod, the detector signal efficiency
        implementation method, which should be used to create the detector
        signal efficiency for this group of sources.
        """
        return self._detsigeff_implmethod
    @detsigeff_implmethod.setter
    def detsigeff_implmethod(self, method):
        if(not isinstance(method, DetSigEffImplMethod)):
            raise TypeError('The detsigeff_implmethod property must be an instance of DetSigEffImplMethod!')
        self._detsigeff_implmethod = method

    @property
    def n_sources(self):
        """(read-only) The number of sources within this source hypothesis
        group.
        """
        return len(self._source_list)


class SourceHypoGroupManager(object):
    """The source hypothesis group manager provides the functionality to group
    sources of the same source hypothesis, i.e. spatial model and flux model,
    with an assign detector signal efficiency implementation method.

    This helps to evaluate the log-likelihood ratio function in an efficient
    way.
    """
    def __init__(self):
        super(SourceHypoGroupManager, self).__init__()

        self._src_hypo_group_list = list()
        # Define a 2D numpy array of shape (N_sources,2) that maps the source
        # index (0 to N_sources-1) to the index of the group and the source
        # index within the group for fast access.
        self._sidx_to_gidx_gsidx_map_arr = np.empty((0,2), dtype=np.int)

    @property
    def source_list(self):
        """The list of defined SourceModel instances.
        """
        source_list = []
        for group in self._src_hypo_group_list:
            source_list += group.source_list
        return source_list

    @property
    def n_sources(self):
        """(read-only) The total number of sources defined in all source groups.
        """
        return self._sidx_to_gidx_gsidx_map_arr.shape[0]

    @property
    def N_src_groups(self):
        """The number of defined source groups.
        """
        return len(self._src_hypo_group_list)

    @property
    def src_hypo_group_list(self):
        """(read-only) The list of source hypothesis groups, i.e.
        SourceHypoGroup instances.
        """
        return self._src_hypo_group_list

    def add_source_hypo_group(self, sources, fluxmodel, detsigeffmethod):
        """Adds a source hypothesis group to the source hypothesis group
        manager. A source hypothesis group of sources share the same flux model
        and the same detector signal efficiency implementation method.

        Parameters
        ----------
        sources : SourceModel | sequence of SourceModel
            The source or sequence of sources that define the source group.
        fluxmodel : instance of FluxModel
            The FluxModel instance that applies to the list of sources of the
            group.
        detsigeffmethod : instance of DetSigEffImplMethod
            The instance of a detector signal efficiency implementation method,
            which should be used to create the detector signal efficiency for
            the sources of the group.
        """
        # Create the source group.
        group = SourceHypoGroup(sources, fluxmodel, detsigeffmethod)

        # Add the group.
        self._src_hypo_group_list.append(group)

        # Extend the source index to (group index, group source index) map
        # array.
        arr = np.empty((group.N_sources,2))
        arr[:,0] = self.N_src_groups-1 # Group index.
        arr[:,1] = np.arange(group.N_sources) # Group source index.
        self._sidx_to_gidx_gsidx_map_arr = np.vstack(
            (self._sidx_to_gidx_gsidx_map_arr, arr))

    def get_fluxmodel_by_src_idx(self, src_idx):
        """Retrieves the FluxModel instance for the source specified by its
        source index.

        Parameters
        ----------
        src_idx : int
            The index of the source, which must be in the range
            [0, N_sources-1].

        Returns
        -------
        fluxmodel : instance of FluxModel
            The FluxModel instance that applies to the specified source.
        """
        gidx = self._sidx_to_gidx_gsidx_map_arr[src_idx,0]
        return self._src_hypo_group_list[gidx]._fluxmodel

    def get_detsigeff_implmethod_by_src_idx(self, src_idx):
        """Retrieves the DetSigEffImplMethod instance for the source specified
        by its source index.

        Parameters
        ----------
        src_idx : int
            The index of the source, which must be in the range
            [0, N_sources-1].

        Returns
        -------
        detsigeff_implmethod : instance of DetSigEffImplMethod
            The DetSigEffImplMethod instance that applies to the specified
            source.
        """
        gidx = self._sidx_to_gidx_gsidx_map_arr[src_idx,0]
        return self._src_hypo_group_list[gidx]._detsigeff_implmethod