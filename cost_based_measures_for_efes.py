import pandas as pd
import numpy as np
import sys
sys.path.append('./effective_energy_shift')

from effective_energy_shift import effective_energy_shift as efes
from effective_energy_shift import efes_dataclasses as efes_dc
import math_cost_measures_for_efes as efes_costs

def read_example_data():
    df = pd.read_csv('effective_energy_shift/examples/example_house_with_PV_3_years.csv', sep=';')
    df['time'] = pd.to_timedelta(df['time'])
    index_start = 0
    index_end = 525600
    time = df['time']
    time_in_seconds = df['time'].dt.total_seconds().to_numpy() / 3600
    delta_time_step = time_in_seconds[1] - time_in_seconds[0]
    power_demand = df['dem'].to_numpy()
    power_generation = df['gen'].to_numpy()
    return dict(time=time[index_start:index_end], time_in_seconds=time_in_seconds[index_start:index_end],
                power_generation=power_generation[index_start:index_end],
                power_demand=power_demand[index_start:index_end], delta_time_step=delta_time_step)


def calculate_cost_optimal_capacity(
        efes_results: efes_dc.Results,
        price_import_in_currency_per_Wh: float,
        price_export_in_currency_per_Wh: float,
        costs_invest_total_res_in_currency: float,
        time_invest_res_in_hours: float,
        price_invest_total_ees_in_currency_per_Wh: float,
        time_invest_ees_in_hours: float,
        efficiency_import: float = 1.0,
        efficiency_export: float = 1.0,
        verbose: bool = False
):
    time_total = efes_results.analysis_results.time_total
    energy_generation = efes_results.analysis_results.energy_generation
    energy_demand = efes_results.analysis_results.energy_demand
    energy_used_generation = efes_results.analysis_results.energy_used_generation
    energy_covered_demand = efes_results.analysis_results.energy_covered_demand

    if verbose:
        print(f"time_total={efes.pretty_print(time_total/24, 'days')}")
        print(f"energy_generation={efes.pretty_print(energy_generation, 'Wh')}")
        print(f"energy_demand={efes.pretty_print(energy_demand, 'Wh')}")
        print(f"energy_used_generation={efes.pretty_print(energy_used_generation, 'Wh')}")
        print(f"energy_covered_demand={efes.pretty_print(energy_covered_demand, 'Wh')}")

    energy_additional = efes_results.analysis_results.energy_additional
    capacity = efes_results.analysis_results.capacity
    effectiveness_local = efes_results.analysis_results.effectiveness_local

    self_consumption_initial = efes_results.analysis_results.self_consumption_initial

    efficiency_direct_usage = efes_results.analysis_results.data_input.efficiency_direct_usage
    efficiency_charging = efes_results.analysis_results.data_input.efficiency_charging
    efficiency_discharging = efes_results.analysis_results.data_input.efficiency_discharging

    results = {}
    input_parameters = dict(
        price_import_in_currency_per_Wh=price_import_in_currency_per_Wh,
        price_export_in_currency_per_Wh=price_export_in_currency_per_Wh,
        costs_invest_total_res_in_currency=costs_invest_total_res_in_currency,
        time_invest_res_in_hours=time_invest_res_in_hours,
        price_invest_total_ees_in_currency_per_Wh=price_invest_total_ees_in_currency_per_Wh,
        time_invest_ees_in_hours=time_invest_ees_in_hours,
        efficiency_import=efficiency_import,
        efficiency_export=efficiency_export
    )
    results['input_parameters'] = input_parameters
    costs_ref = efes_costs.calculate_reference_costs(
        energy_demand=energy_demand,
        price_import=price_import_in_currency_per_Wh,
        efficiency_import=efficiency_import
    )
    results['costs_ref'] = costs_ref
    if verbose:
        print(f'{costs_ref=} €')

    ratio_export_to_import = efes_costs.calculate_import_export_ratio(price_export=price_export_in_currency_per_Wh,
                                                                      price_import=price_import_in_currency_per_Wh)
    results['ratio_export_to_import'] = ratio_export_to_import
    if verbose:
        print(f'{ratio_export_to_import=}')

    price_invest_res = efes_costs.calculate_relative_invest_price(
        energy=energy_generation,
        costs_invest_total=costs_invest_total_res_in_currency,
        time_invest=time_invest_res_in_hours,
        time_total=time_total
    )

    results['price_invest_res'] = price_invest_res
    if verbose:
        print(f'{price_invest_res=} €/Wh')

    ratio_invest_res = efes_costs.calculate_price_ratio(
        price=price_invest_res,
        price_reference=price_import_in_currency_per_Wh
    )
    results['ratio_invest_res'] = ratio_invest_res
    if verbose:
        print(f'{ratio_invest_res=}')

    price_invest_ees = efes_costs.calculate_relative_invest_price(
        price_invest_per_energy=price_invest_total_ees_in_currency_per_Wh,
        time_invest=time_invest_ees_in_hours,
        time_total=time_total
    )
    results['price_invest_ees'] = price_invest_ees

    ratio_invest_ees = efes_costs.calculate_price_ratio(
        price=price_invest_ees,
        price_reference=price_import_in_currency_per_Wh
    )
    results['ratio_invest_ees'] = ratio_invest_ees

    costs_0 = efes_costs.calculate_initial_costs(
        energy_generation=energy_generation,
        price_import=price_import_in_currency_per_Wh,
        ratio_export_to_import=ratio_export_to_import,
        efficiency_export=efficiency_export,
        efficiency_import=efficiency_import,
        efficiency_direct_usage=efficiency_direct_usage,
        self_consumption_initial=self_consumption_initial,
        ratio_invest_res=ratio_invest_res
    )
    results['costs_0'] = costs_0

    price_additional = efes_costs.calculate_price_for_additional_energy(
        price_import=price_import_in_currency_per_Wh,
        ratio_export_to_import=ratio_export_to_import,
        efficiency_export=efficiency_export,
        efficiency_import=efficiency_import,
        efficiency_charging=efficiency_charging,
        efficiency_discharging=efficiency_discharging
    )
    results['price_additional'] = price_additional
    if verbose:
        print(f'{price_additional=} €/Wh')

    ratio_additional = efes_costs.calculate_price_ratio(
        price=price_additional,
        price_reference=price_import_in_currency_per_Wh
    )
    results['ratio_additional'] = ratio_additional

    costs_additional = efes_costs.calculate_additional_costs(
        capacity=capacity,
        energy_additional=energy_additional,
        price_additional=price_additional,
        price_invest_ees=price_invest_ees
    )
    results['costs_additional'] = costs_additional
    if verbose:
        print(f'costs_additional={efes.pretty_print(costs_additional, "€")}')

    costs_total = efes_costs.calculate_total_costs_with_res_and_ees(
        energy_generation=energy_generation,
        energy_demand=energy_demand,
        price_import=price_import_in_currency_per_Wh,
        efficiency_import=efficiency_import,
        efficiency_export=efficiency_export,
        efficiency_direct_usage=efficiency_direct_usage,
        self_consumption_initial=self_consumption_initial,
        ratio_invest_res=ratio_invest_res,
        capacity=capacity,
        energy_additional=energy_additional,
        price_additional=price_additional,
        price_invest_ees=price_invest_ees,
        ratio_export_to_import=ratio_export_to_import
    )
    results['costs_total'] = costs_total

    effectiveness_optimal = efes_costs.calculate_optimal_effectiveness(price_invest_ees, price_additional, efficiency_discharging)
    results['effectiveness_optimal'] = effectiveness_optimal

    ix_costs_minimal = np.argmin(effectiveness_local >= effectiveness_optimal)
    results['ix_costs_minimal'] = ix_costs_minimal
    results['costs_minimal'] = costs_total[ix_costs_minimal]
    results['capacity_optimal'] = efes_results.analysis_results.capacity[ix_costs_minimal]
    if verbose:
        print(f'minimal costs of {efes.pretty_print(results["costs_minimal"], "€")} with C = {efes.pretty_print(results["capacity_optimal"], "Wh")}')

    return results


if __name__ == '__main__':

    efficiency_discharging = 0.95
    efficiency_charging = 0.95
    efficiency_direct_usage = 0.95

    input_data = read_example_data()
    filename = f'house_example_results_for_costs_{efficiency_discharging:.2f}_{efficiency_charging:.2f}_{efficiency_direct_usage:.2f}'

    try:
        efes_results = efes_dc.unpickle(filename=filename)
    except FileNotFoundError:
        efes_results = efes.perform_effective_energy_shift(
            power_generation=input_data['power_generation'],
            power_demand=input_data['power_demand'],
            delta_time_step=input_data['delta_time_step'],
            efficiency_direct_usage=efficiency_direct_usage,
            efficiency_discharging=efficiency_discharging,
            efficiency_charging=efficiency_charging,
        )
        efes_dc.pickle(efes_results, filename=filename)

    """Calculate the cost-optimal values"""
    price_import_ct_per_kWh = 31.46
    price_export_ct_per_kWh = 8.11

    costs_invest_total_res = 15000
    time_invest_res_years = 20

    price_invest_ees_per_kWh = 800.0
    time_invest_ees_years = 15

    efficiency_import = 1.
    efficiency_export = 0.95

    print('Input parameters:')
    print(f'  - Import price: {efes.pretty_print(price_import_ct_per_kWh, "ct/kWh")}')
    print(f'  - Export price: {efes.pretty_print(price_export_ct_per_kWh, "ct/kWh")}')
    print(f'  - Total invest costs RES: {efes.pretty_print(costs_invest_total_res, "€")}')
    print(f'  - Lifetime RES: {efes.pretty_print(time_invest_res_years, "years")}')
    print(f'  - Total invest price EES: {efes.pretty_print(price_invest_ees_per_kWh, "€/kWh")}')
    print(f'  - Lifetime EES: {efes.pretty_print(time_invest_ees_years, "years")}')
    print(f'  - Import efficiency: {efes.pretty_print(efficiency_import*100, "%")}')
    print(f'  - Export efficiency: {efes.pretty_print(efficiency_export*100, "%")}')
    print(f'  - Charging efficiency: {efes.pretty_print(efficiency_charging*100, "%")}')
    print(f'  - Discharge efficiency: {efes.pretty_print(efficiency_discharging*100, "%")}')

    cost_optimal_results = calculate_cost_optimal_capacity(
        efes_results=efes_results,
        price_import_in_currency_per_Wh=price_import_ct_per_kWh * 1e-5,
        price_export_in_currency_per_Wh=price_export_ct_per_kWh * 1e-5,
        costs_invest_total_res_in_currency=costs_invest_total_res,
        time_invest_res_in_hours=time_invest_res_years * 365 * 24,
        price_invest_total_ees_in_currency_per_Wh=price_invest_ees_per_kWh * 1e-3,
        time_invest_ees_in_hours=time_invest_ees_years * 365 * 24,
        efficiency_import=efficiency_import,
        efficiency_export=efficiency_export
    )

    print('Results:')
    print(f'  - Reference costs: {efes.pretty_print(cost_optimal_results["costs_ref"], "€")}')
    print(f'  - Export to import ratio: {efes.pretty_print(cost_optimal_results["ratio_export_to_import"], "", decimals=4)}')
    print(f'  - Invest price RES: {efes.pretty_print(cost_optimal_results["price_invest_res"]*1000000, "€/MWh")}')
    print(f'  - Invest price EES: {efes.pretty_print(cost_optimal_results["price_invest_ees"]*1000, "€/kWh")}')
    print(f'  - Initial costs: {efes.pretty_print(cost_optimal_results["costs_0"], "€")}')
    print(f'  - Additional price: {efes.pretty_print(cost_optimal_results["price_additional"]*1000, "€/kWh")}')
    print(f'  - Optimal local effectiveness: {efes.pretty_print(cost_optimal_results["effectiveness_optimal"], "")}')
    print(f'  - Optimal capacity: {efes.pretty_print(cost_optimal_results["capacity_optimal"], "Wh")}')
    print(f'  - Minimal costs: {efes.pretty_print(cost_optimal_results["costs_minimal"], "€")}')
