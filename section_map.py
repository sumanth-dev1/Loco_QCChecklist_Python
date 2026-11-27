"""
section_map.py

The section_id -> table name map, copied exactly from the checklist schema
(checkObservations and other services use the same list).
Table names only ever come from this fixed dictionary, never from user
input, which is what makes building SQL with the table name safe.
"""

import datetime
import zoneinfo

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


def sync_loco_metadata(
    cursor,
    loco_id,
    loco_type,
    brake_type,
    railway_division,
    shed_name,
    inspection_date,
    table_names=None,
    exclude_table=None,
    update_inspection_date=False,
):
    """Ensure master loco table and sibling section tables reflect updated header metadata."""
    cursor.execute(
        "SELECT Loco_type, Brake_type, Railway_Division, Shed_name, inspection_Date FROM loco WHERE Loco_Id = %s LIMIT 1",
        (loco_id,),
    )
    loco_row = cursor.fetchone()

    if loco_row:
        if isinstance(loco_row, dict):
            old_loco_type = (loco_row.get("Loco_type") or "").strip()
            old_brake_type = (loco_row.get("Brake_type") or "").strip()
            old_division = (loco_row.get("Railway_Division") or "").strip()
            old_shed = (loco_row.get("Shed_name") or "").strip()
            old_date_raw = loco_row.get("inspection_Date")
        else:
            old_loco_type = (loco_row[0] or "").strip()
            old_brake_type = (loco_row[1] or "").strip()
            old_division = (loco_row[2] or "").strip()
            old_shed = (loco_row[3] or "").strip()
            old_date_raw = loco_row[4]

        old_date = str(old_date_raw) if old_date_raw else ""

        loco_type = (loco_type or "").strip() or old_loco_type
        brake_type = (brake_type or "").strip() or old_brake_type
        railway_division = (railway_division or "").strip() or old_division
        shed_name = (shed_name or "").strip() or old_shed
        inspection_date = (inspection_date or "").strip() or old_date

        core_changed = (
            loco_type != old_loco_type
            or brake_type != old_brake_type
            or railway_division != old_division
            or shed_name != old_shed
        )
        date_changed = bool(update_inspection_date and inspection_date and inspection_date != old_date)

        if core_changed or date_changed:
            if update_inspection_date and inspection_date:
                cursor.execute(
                    """UPDATE loco
                       SET Loco_type = %s, Brake_type = %s, Railway_Division = %s, Shed_name = %s, inspection_Date = %s
                       WHERE Loco_Id = %s""",
                    (loco_type, brake_type, railway_division, shed_name, inspection_date, loco_id),
                )
            else:
                cursor.execute(
                    """UPDATE loco
                       SET Loco_type = %s, Brake_type = %s, Railway_Division = %s, Shed_name = %s
                       WHERE Loco_Id = %s""",
                    (loco_type, brake_type, railway_division, shed_name, loco_id),
                )

        if core_changed:
            targets = table_names if table_names is not None else SECTION_TABLES.values()
            for tbl in targets:
                if tbl == exclude_table:
                    continue
                try:
                    cursor.execute(
                        f"""UPDATE `{tbl}`
                            SET loco_type = %s, brake_type = %s, railway_division = %s, shed_name = %s
                            WHERE loco_id = %s
                              AND NOT (loco_type <=> %s AND brake_type <=> %s AND railway_division <=> %s AND shed_name <=> %s)""",
                        (
                            loco_type,
                            brake_type,
                            railway_division,
                            shed_name,
                            loco_id,
                            loco_type,
                            brake_type,
                            railway_division,
                            shed_name,
                        ),
                    )
                except Exception:
                    pass
    else:
        inspection_date = (inspection_date or "").strip()
        if not inspection_date:
            inspection_date = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
        loco_type = (loco_type or "").strip()
        brake_type = (brake_type or "").strip()
        railway_division = (railway_division or "").strip()
        shed_name = (shed_name or "").strip()
        if loco_type and brake_type and railway_division and shed_name:
            now_ist = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """INSERT IGNORE INTO loco
                   (Loco_Id, Loco_type, Brake_type, Railway_Division, Shed_name, inspection_Date, start_time, completed_time)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (loco_id, loco_type, brake_type, railway_division, shed_name, inspection_date, now_ist, now_ist),
            )

    if not inspection_date:
        inspection_date = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")

    return loco_type, brake_type, railway_division, shed_name, inspection_date