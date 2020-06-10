"""
Collection of helping functions for NASAMeteoDataTool.
"""
import math

class helpingFunctions:

    @staticmethod
    def check_angstromAB(xA, xB):
        """
        A method that checks validity of Angstrom coefficients.
        Inputs:
            * xA - Angstrom A coefficient (float)
            * xB - Angstrom B coefficient (float)
        Outputs:
            * [A, B] - Absolute values of A and B coefficients ()
        """

        MIN_A = 0.1
        MAX_A = 0.4
        MIN_B = 0.3
        MAX_B = 0.7
        MIN_SUM_AB = 0.6
        MAX_SUM_AB = 0.9
        A = abs(xA)
        B = abs(xB)
        SUM_AB = A + B
        if A < MIN_A or A > MAX_A:
            raise ValueError ("Out of range Angstrom A value!")
        if B < MIN_B or B > MAX_B:
            raise ValueError ("Out of range Angstrom A value!")
        if SUM_AB < MIN_SUM_AB or SUM_AB > MAX_SUM_AB:
            raise ValueError ("Out of range summary of Angstrom A & B values!")

        return [A,B]

    @staticmethod
    def ea_from_tdew(tdew):
        """
        Calculates actual vapour pressure, ea [kPa] from the dewpoint temperature
        using equation (14) in the FAO paper. As the dewpoint temperature is the
        temperature to which air needs to be cooled to make it saturated, the
        actual vapour pressure is the saturation vapour pressure at the dewpoint
        temperature. This method is preferable to calculating vapour pressure from
        minimum temperature.

        Taken from fao_et0.py written by Mark Richards

        Reference:
        Allen, R.G., Pereira, L.S., Raes, D. and Smith, M. (1998) Crop
            evapotranspiration. Guidelines for computing crop water requirements,
            FAO irrigation and drainage paper 56)

        Arguments:
        tdew - dewpoint temperature [deg C]
        """
        # Raise exception:
        if (tdew < -95.0 or tdew > 65.0):
            # Are these reasonable bounds?
            msg = 'tdew=%g is not in range -95 to +60 deg C' % tdew
            raise ValueError(msg)

        tmp = (17.27 * tdew) / (tdew + 237.3)
        ea = 0.6108 * math.exp(tmp)

        return (ea)
