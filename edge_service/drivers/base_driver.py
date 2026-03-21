from abc import ABC, abstractmethod


class BaseCameraDriver(ABC):

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def read_frame(self):
        pass