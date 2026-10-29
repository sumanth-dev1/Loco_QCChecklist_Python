"""
section_map.py

The section_id -> table name map, copied exactly from the checklist schema
(checkObservations and other services use the same list).
Table names only ever come from this fixed dictionary, never from user
input, which is what makes building SQL with the table name safe.
"""

SECTION_TABLES = {
    1: "document_verification_table",
    2: "verify_serial_numbers_of_equipment_as_per_ic",
    3: "loco_kavach",
    4: "emi_filter_box",
    5: "rib_cab_input_box",
    6: "dmi_lp_ocip",
    7: "rfid_ps_unit",
    8: "loco_antenna_and_gps_gsm_antenna",
    9: "pneumatic_fittings_and_ep_valve_cocks_fixing",
    10: "pressure_sensors_installation_in_loco",
    11: "iru_faviely_units_fixing_for_e70_type_loco",
    12: "psjb_tpm_units_fixing_for_ccb_type_loco",
    13: "sifa_valve_fixing_for_ccb_type_loco",
    14: "pgs_and_speedo_meter_units_fixing",
    15: "rfid_reader_assembly",
    16: "earthing",
    17: "radio_power",
}