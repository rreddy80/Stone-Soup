from abc import abstractmethod, ABC
from typing import Set, Union, Sequence

import numpy as np

from ..base import Property
from ..sensor.base import PlatformMountable
from ..types.detection import TrueDetection
from ..types.groundtruth import GroundTruthState


class Sensor(PlatformMountable, ABC):
    """Sensor Base class for general use.

    Most properties and methods are inherited from :class:`~.PlatformMountable`.

    Sensors must have a measure function.
    """

    @abstractmethod
    def measure(self, ground_truths: Set[GroundTruthState], noise: Union[np.ndarray, bool] = True,
                **kwargs) -> Set[TrueDetection]:
        """Generate a measurement for a given state

        Parameters
        ----------
        ground_truths : Set[:class:`~.GroundTruthState`]
            A set of :class:`~.GroundTruthState`
        noise: :class:`numpy.ndarray` or bool
            An externally generated random process noise sample (the default is `True`, in which
            case :meth:`~.Model.rvs` is used; if `False`, no noise will be added)

        Returns
        -------
        Set[:class:`~.TrueDetection`]
            A set of measurements generated from the given states. The timestamps of the
            measurements are set equal to that of the corresponding states that they were
            calculated from. Each measurement stores the ground truth path that it was produced
            from.
        """
        raise NotImplementedError


class SensorSuite(Sensor):
    """Sensor composition type

    Models a suite of sensors all returning detections at the same 'time'. Returns all detections
    in one go.
    Can append information of the sensors to the metadata of their corresponding detections.
    """

    sensors: Sequence[Sensor] = Property(doc="Suite of sensors to get detections from.")

    attributes_inform: Set[str] = Property(
        doc="Names of attributes to store the value of at time of detection."
    )

    def measure(self, ground_truths: Set[GroundTruthState], noise: Union[bool, np.ndarray] = True,
                **kwargs) -> Set[TrueDetection]:
        """Call each sub-sensor's measure method in turn. Key word arguments are passed to the
        measure method of each sensor.

        Append additional metadata to each sensor's set of detections. Which keys are appended is
        dictated by :attr:`attributes_inform`."""

        all_detections = set()

        for sensor in self.sensors:

            detections = sensor.measure(ground_truths, noise, **kwargs)

            attributes_dict = {attribute_name: sensor.__getattribute__(attribute_name)
                               for attribute_name in self.attributes_inform}

            for detection in detections:
                detection.metadata.update(attributes_dict)

            all_detections.update(detections)

        return all_detections
