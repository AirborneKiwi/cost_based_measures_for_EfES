## Analytical solution for the cost optimal Electric Energy Storage (EES) size based on the Effective Energy Shift (EfES) algorithm

This repository contains the code for calculating the cost-optimal storage capacity of EES systems based on the Effective Energy Shift (EfES) algorithm. 
The algorithm is described in "Analytical solution for the cost optimal Electric Energy Storage size based on the Effective Energy Shift (EfES) algorithm" by J. Fellerer and R. German, accepted for the 4th Energy Informatics Academy Conference (EI.A 2024).
The publication will be available in the Springer Lecture Notes in Computer Science (LNCS).

## Installation and usage example

Clone the repository and execute

`python cost_based_measures_for_efes.py`

This will run the example from the publication and will produce the following output:

```
Input parameters:
  - Import price: 31.46 ct/kWh
  - Export price: 8.11 ct/kWh
  - Total invest costs RES: 15.00 k€
  - Lifetime RES: 20.00 years
  - Total invest price EES: 800.00 €/kWh
  - Lifetime EES: 15.00 years
  - Import efficiency: 100.00 %
  - Export efficiency: 95.00 %
  - Charging efficiency: 95.00 %
  - Discharge efficiency: 95.00 %
Results:
  - Reference costs: 1.26 k€
  - Export to import ratio: 0.2578 
  - Invest price RES: 75.23 €/MWh
  - Invest price EES: 53.33 €/kWh
  - Initial costs: 391.71 €
  - Additional price: 0.23 €/kWh
  - Optimal local effectiveness: 244.91 
  - Optimal capacity: 3.76 kWh
  - Minimal costs: 811.33 €
```

## License

The code is provided under the MIT license. If you use the code in your research, please cite the paper above.

## Contact

If you have any questions, please contact the authors of the paper via <jonathan.fellerer@fau.de>.

