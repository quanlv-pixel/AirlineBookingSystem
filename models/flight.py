class Flight:
    def __init__(self, flight_id, flight_number, origin, destination,
                 departure_time, arrival_time,
                 price_eco, price_business,        
                 seats_available=0, status="scheduled"):
        self.flight_id       = flight_id
        self.flight_number   = flight_number
        self.origin          = origin
        self.destination     = destination
        self.departure_time  = departure_time
        self.arrival_time    = arrival_time
        self.price_eco       = price_eco
        self.price_business  = price_business
        self.seats_available = seats_available
        self.status          = status

    @property
    def price(self) -> float:
        return self.price_eco