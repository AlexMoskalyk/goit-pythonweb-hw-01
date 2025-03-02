from abc import ABC, abstractmethod
import logging
from typing import Type

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Абстрактний клас транспортного засобу
class Vehicle(ABC):
    def __init__(self, make: str, model: str, region_spec: str):
        self.make = make
        self.model = model
        self.region_spec = region_spec

    @abstractmethod
    def start_engine(self) -> None:
        pass


# Клас автомобіля
class Car(Vehicle):
    def start_engine(self) -> None:
        logger.info(
            f"{self.make} {self.model} ({self.region_spec} Spec): Двигун запущено"
        )


# Клас мотоцикла
class Motorcycle(Vehicle):
    def start_engine(self) -> None:
        logger.info(
            f"{self.make} {self.model} ({self.region_spec} Spec): Мотор заведено"
        )


# Абстрактний клас фабрики
class VehicleFactory(ABC):
    @abstractmethod
    def create_car(self, make: str, model: str) -> Car:
        pass

    @abstractmethod
    def create_motorcycle(self, make: str, model: str) -> Motorcycle:
        pass


# Фабрика для США
class USVehicleFactory(VehicleFactory):
    def create_car(self, make: str, model: str) -> Car:
        return Car(make, model, "US")

    def create_motorcycle(self, make: str, model: str) -> Motorcycle:
        return Motorcycle(make, model, "US")


# Фабрика для ЄС
class EUVehicleFactory(VehicleFactory):
    def create_car(self, make: str, model: str) -> Car:
        return Car(make, model, "EU")

    def create_motorcycle(self, make: str, model: str) -> Motorcycle:
        return Motorcycle(make, model, "EU")


# Використання фабрик
us_factory: VehicleFactory = USVehicleFactory()
eu_factory: VehicleFactory = EUVehicleFactory()

vehicle1: Car = us_factory.create_car("Ford", "Mustang")
vehicle1.start_engine()

vehicle2: Motorcycle = eu_factory.create_motorcycle("BMW", "R1250")
vehicle2.start_engine()
