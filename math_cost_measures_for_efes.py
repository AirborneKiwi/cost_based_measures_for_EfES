import numpy as np
def calculate_total_costs(costs_import, costs_export, costs_invest):
    return costs_import - costs_export + costs_invest

def calculate_import_costs(energy_demand, energy_covered_demand, energy_additional, price_import, efficiency_import):
    return price_import / efficiency_import * (energy_demand - energy_covered_demand - energy_additional)


def calculate_total_invest_costs(costs_invest_res, costs_invest_ees):
    return costs_invest_res + costs_invest_ees


def calculate_relative_invest_price(time_invest, time_total, energy=None, costs_invest_total=None, price_invest_per_energy=None):
    assert (costs_invest_total is not None and energy is not None) or price_invest_per_energy is not None, "Either costs_invest_total and energy or price_invest_per_energy must be given"

    if price_invest_per_energy is None:
        price_invest_per_energy = costs_invest_total / energy

    return price_invest_per_energy * time_total / time_invest


def calculate_export_costs(energy_generation, energy_used_generation, energy_additional, price_export, efficiency_export, efficiency_charging, efficiency_discharging):
    return price_export * efficiency_export * (energy_generation - energy_used_generation - energy_additional / (efficiency_charging * efficiency_discharging))


def calculate_reference_costs(energy_demand, price_import, efficiency_import):
    return (price_import / efficiency_import) * energy_demand


def calculate_price_ratio(price, price_reference):
    return price / price_reference


def calculate_import_export_ratio(price_export, price_import):
    return calculate_price_ratio(price_export, price_import)


def calculate_import_export_ratio_for_efficiency(efficiency, ratio_export_to_import, efficiency_import, efficiency_export):
    """
    Calculate the ratio of import to export r_p(mu) for a given efficiency (mu)
    """
    return 1/efficiency_import - (ratio_export_to_import*efficiency_export)/efficiency


def calculate_import_export_price_for_efficiency(efficiency, price_import, efficiency_import, efficiency_export, ratio_export_to_import=None, price_export=None):
    assert price_export is not None or ratio_export_to_import is not None, "Either price_export or ratio_export_to_import must be given"
    if ratio_export_to_import is None:
        ratio_export_to_import = calculate_import_export_ratio(price_export, price_import)
    return price_import * calculate_import_export_ratio_for_efficiency(efficiency, ratio_export_to_import, efficiency_import, efficiency_export)


def calculate_initial_costs(energy_generation, price_import, ratio_export_to_import, efficiency_export, efficiency_import, efficiency_direct_usage, self_consumption_initial, ratio_invest_res):
    return price_import * (ratio_export_to_import * efficiency_export + efficiency_direct_usage * self_consumption_initial * calculate_import_export_ratio_for_efficiency(efficiency_direct_usage, ratio_export_to_import, efficiency_import, efficiency_export) - ratio_invest_res) * energy_generation


def calculate_price_for_additional_energy(price_import, ratio_export_to_import, efficiency_export, efficiency_import, efficiency_charging, efficiency_discharging):
    return calculate_import_export_price_for_efficiency(efficiency_charging * efficiency_discharging, price_import, efficiency_import, efficiency_export, ratio_export_to_import)


def calculate_additional_costs(capacity, energy_additional, price_additional, price_invest_ees):
    return price_additional * energy_additional - price_invest_ees * capacity


def calculate_export_to_import_ratio_threshold(price_import, price_invest_ees, effectiveness_local_initial, efficiency_export, efficiency_import, efficiency_charging, efficiency_discharging):
    a = efficiency_charging/efficiency_export
    b = efficiency_discharging/efficiency_import
    return a*(b-price_invest_ees/(price_import*effectiveness_local_initial))


def calculate_total_costs_with_res_and_ees(energy_generation, energy_demand, price_import, efficiency_import, efficiency_export, efficiency_direct_usage, self_consumption_initial, ratio_invest_res, capacity, energy_additional, price_additional, price_invest_ees, ratio_export_to_import=None, price_export=None):
    assert price_export is not None or ratio_export_to_import is not None, "Either price_export or ratio_export_to_import must be given"
    if ratio_export_to_import is None:
        ratio_export_to_import = calculate_import_export_ratio(price_export, price_import)

    costs_ref = calculate_reference_costs(energy_demand=energy_demand, price_import=price_import, efficiency_import=efficiency_import)
    costs_0 = calculate_initial_costs(energy_generation=energy_generation, price_import=price_import, ratio_export_to_import=ratio_export_to_import, efficiency_export=efficiency_export, efficiency_import=efficiency_import, efficiency_direct_usage=efficiency_direct_usage, self_consumption_initial=self_consumption_initial, ratio_invest_res=ratio_invest_res)
    costs_additional = calculate_additional_costs(capacity=capacity, energy_additional=energy_additional, price_additional=price_additional, price_invest_ees=price_invest_ees)
    return costs_ref - costs_0 - costs_additional


def calculate_optimal_effectiveness(price_invest_ees, price_additional, efficiency_discharging):
    if price_additional < 0:
        return np.inf
    return price_invest_ees / (price_additional * efficiency_discharging)


def calculate_ratio_export_intercept(efficiency_charging, efficiency_discharging, efficiency_export, efficiency_import):
    return efficiency_charging * efficiency_discharging / (efficiency_export * efficiency_import)


def calculate_ratio_invest_ees_intercept(efficiency_discharging, efficiency_import):
    return efficiency_discharging / efficiency_import


def calculate_optimality_ratio(effectiveness_local, effectiveness_local_initial, efficiency_discharging, efficiency_import):
    normalized_effectiveness = effectiveness_local / effectiveness_local_initial
    return calculate_ratio_invest_ees_intercept(efficiency_discharging, efficiency_import) * normalized_effectiveness


def get_capacity_for_local_effectiveness(analysis_results, effectiveness_local_target: float):
    index = np.searchsorted(-analysis_results.effectiveness_local, -effectiveness_local_target, side='left')
    if index == analysis_results.capacity.shape[0]:
        return analysis_results.capacity[-1]
    return analysis_results.capacity[index]


def get_optimal_capacity(analysis_results, price_invest_ees, price_additional, efficiency_discharging):
    effectiveness_optimal = calculate_optimal_effectiveness(price_invest_ees, price_additional, efficiency_discharging)
    return get_capacity_for_local_effectiveness(analysis_results, effectiveness_optimal)


def calculate_levelized_costs_of_storage(energy_additional, costs_additional):
    return costs_additional / energy_additional