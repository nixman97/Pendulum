from math import sin, radians


class Calculations:
    def getAngle(self, lat, hours):
        print(((sin(radians(lat)) * 360) / 24) * hours)
        return (((sin(radians(lat)) * 360) / 24) * hours)
