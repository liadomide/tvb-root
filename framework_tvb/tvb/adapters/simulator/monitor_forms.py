# -*- coding: utf-8 -*-
#
#
# TheVirtualBrain-Framework Package. This package holds all Data Management, and
# Web-UI helpful to run brain-simulations. To use it, you also need do download
# TheVirtualBrain-Scientific Package (for simulators). See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2020, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

from tvb.core.entities.filters.chain import FilterChain
from tvb.datatypes.sensors import EEG_POLYMORPHIC_IDENTITY as EEG_S
from tvb.datatypes.sensors import MEG_POLYMORPHIC_IDENTITY as MEG_S
from tvb.datatypes.sensors import INTERNAL_POLYMORPHIC_IDENTITY as SEEG_S
from tvb.simulator.monitors import *
from tvb.adapters.simulator.equation_forms import get_ui_name_to_monitor_equation_dict
from tvb.adapters.datatypes.db.region_mapping import RegionMappingIndex
from tvb.adapters.datatypes.db.sensors import SensorsIndex
from tvb.adapters.datatypes.db.surface import SurfaceIndex
from tvb.core.neotraits.forms import Form, ScalarField, ArrayField, DataTypeSelectField, SimpleSelectField


def get_monitor_to_form_dict():
    monitor_class_to_form = {
        Raw: RawMonitorForm,
        SubSample: SubSampleMonitorForm,
        SpatialAverage: SpatialAverageMonitorForm,
        GlobalAverage: GlobalAverageMonitorForm,
        TemporalAverage: TemporalAverageMonitorForm,
        EEG: EEGMonitorForm,
        MEG: MEGMonitorForm,
        iEEG: iEEGMonitorForm,
        Bold: BoldMonitorForm,
        BoldRegionROI: BoldRegionROIMonitorForm
    }

    return monitor_class_to_form


def get_ui_name_to_monitor_dict(surface):
    ui_name_to_monitor = {
        'Raw recording': Raw,
        'Temporally sub-sample': SubSample,
        'Spatial average with temporal sub-sample': SpatialAverage,
        'Global average': GlobalAverage,
        'Temporal average': TemporalAverage,
        'EEG': EEG,
        'MEG': MEG,
        'Intracerebral / Stereo EEG': iEEG,
        'BOLD': Bold
    }

    if surface:
        ui_name_to_monitor['BOLD Region ROI'] = BoldRegionROI

    return ui_name_to_monitor


def get_form_for_monitor(monitor_class):
    return get_monitor_to_form_dict().get(monitor_class)


class MonitorForm(Form):

    def __init__(self, prefix='', project_id=None):
        super(MonitorForm, self).__init__(prefix)
        self.project_id = project_id
        self.period = ScalarField(Monitor.period, self)
        self.variables_of_interest = ArrayField(Monitor.variables_of_interest, self)


class RawMonitorForm(MonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(RawMonitorForm, self).__init__(prefix, project_id)
        self.period = ScalarField(Raw.period, self, disabled=False)
        self.variables_of_interest = ArrayField(Raw.variables_of_interest, self, disabled=False)


class SubSampleMonitorForm(MonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(SubSampleMonitorForm, self).__init__(prefix, project_id)


class SpatialAverageMonitorForm(MonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(SpatialAverageMonitorForm, self).__init__(prefix, project_id)
        self.spatial_mask = ArrayField(SpatialAverage.spatial_mask, self)
        self.default_mask = ScalarField(SpatialAverage.default_mask, self, disabled=True)


class GlobalAverageMonitorForm(MonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(GlobalAverageMonitorForm, self).__init__(prefix, project_id)


class TemporalAverageMonitorForm(Form):

    def __init__(self, prefix='', project_id=None):
        super(TemporalAverageMonitorForm, self).__init__(prefix, project_id)


class ProjectionMonitorForm(MonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(ProjectionMonitorForm, self).__init__(prefix, project_id)
        self.region_mapping = DataTypeSelectField(RegionMappingIndex, self, name='region_mapping', required=True,
                                                  label=Projection.region_mapping.label,
                                                  doc=Projection.region_mapping.doc)
        # self.obsnoise


class EEGMonitorForm(ProjectionMonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(EEGMonitorForm, self).__init__(prefix, project_id)

        sensor_filter = FilterChain(fields=[FilterChain.datatype + '.sensors_type'], operations=["=="],
                                    values=[EEG_S])

        self.projection = DataTypeSelectField(SurfaceIndex, self, name='projection', required=True,
                                              label=EEG.projection.label, doc=EEG.projection.label,
                                              conditions=None)
        self.reference = ScalarField(EEG.reference, self)
        self.sensors = DataTypeSelectField(SensorsIndex, self, name='sensors', required=True, label=EEG.sensors.label,
                                           doc=EEG.sensors.doc, conditions=sensor_filter)
        self.sigma = ScalarField(EEG.sigma, self)


class MEGMonitorForm(ProjectionMonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(MEGMonitorForm, self).__init__(prefix, project_id)

        sensor_filter = FilterChain(fields=[FilterChain.datatype + '.sensors_type'], operations=["=="],
                                    values=[MEG_S])

        self.projection = DataTypeSelectField(SurfaceIndex, self, name='projection', required=True,
                                              label=MEG.projection.label, doc=MEG.projection.doc,
                                              conditions=None)
        self.sensors = DataTypeSelectField(SensorsIndex, self, name='sensors', required=True, label=MEG.sensors.label,
                                           doc=MEG.sensors.doc, conditions=sensor_filter)


class iEEGMonitorForm(ProjectionMonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(iEEGMonitorForm, self).__init__(prefix, project_id)

        sensor_filter = FilterChain(fields=[FilterChain.datatype + '.sensors_type'], operations=["=="],
                                    values=[SEEG_S])

        self.projection = DataTypeSelectField(SurfaceIndex, self, name='projection', required=True,
                                              label=iEEG.projection.label, doc=iEEG.projection.doc,
                                              conditions=None)
        self.sigma = ScalarField(iEEG.sigma, self)
        self.sensors = DataTypeSelectField(SensorsIndex, self, name='sensors', required=True, label=iEEG.sensors.label,
                                           doc=iEEG.sensors.doc, conditions=sensor_filter)


class BoldMonitorForm(MonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(BoldMonitorForm, self).__init__(prefix, project_id)
        self.period = ScalarField(Bold.period, self)
        self.equation_choices = get_ui_name_to_monitor_equation_dict()
        self.equation = SimpleSelectField(self.equation_choices, self, name='equation', required=True, label='Equation')

    def fill_trait(self, datatype):
        super(BoldMonitorForm, self).fill_trait(datatype)
        datatype.period = self.period.data
        datatype.equation = self.equation.data()


class BoldRegionROIMonitorForm(BoldMonitorForm):

    def __init__(self, prefix='', project_id=None):
        super(BoldRegionROIMonitorForm, self).__init__(prefix, project_id)
