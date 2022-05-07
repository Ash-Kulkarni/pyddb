from dataclasses import dataclass
import arupcomputepy
import json
import ipywidgets as widgets
import pandas as pd


@dataclass
class FCU_input:
    """FCU calc input dataclass"""

    # global
    fresh_air_temperature: int
    fresh_air_relative_humidity: int
    minimum_temperature_of_cooling_coil: int
    cooling_coil_contact_factor: int
    supply_fan_temperature_rise: int
    altitude: int
    lthw_flow: int
    lthw_return: int
    chw_flow: int
    chw_return: int
    chw_glycol_concentration: int
    chw_glycol_type: str
    # space flow rates
    supply_air_flow_rate: int
    fresh_air_volume_flow_rate: int
    # summer space conditions
    sensible_heat_gain: int
    latent_heat_gain: int
    return_room_air_temperature: int
    # winter space conditions
    sensible_heat_gain: int
    latent_heat_gain: int
    return_room_air_temperature: int


@dataclass
class FCU:
    """FCU calc output dataclass"""

    supply_air_temperature: int
    supply_air_relative_humidity: int
    return_room_air_temperature: int
    relative_humidity: int
    cooling_coil_duty: int
    heating_coil_duty: int
    rate_of_condensate_production: int


def designcheck_calc(inputs):

    token = arupcomputepy.AcquireNewAccessTokenDeviceFlow()
    response = arupcomputepy.MakeCalculationRequest(
        inputs["calc_id"],
        inputs["job_number"],
        token,
        isBatch=False,
        variables=inputs["variables"],
    )
    result = json.loads(response["output"])
    output = []

    if "errors" in result:
        for error in result["errors"]:
            print(error)
            raise Exception
        entry = []
        for value in result["arupComputeResultItems"]:

            entry.append(value["value"])

        output.append(entry)

    return output


def designcheck_batchcalc(inputs):

    token = arupcomputepy.AcquireNewAccessTokenDeviceFlow()
    response = arupcomputepy.MakeCalculationRequest(
        inputs["calc_id"],
        inputs["job_number"],
        token,
        isBatch=True,
        variables=inputs["variables"],
    )
    results = json.loads(response["output"])
    output = []

    for result in results:
        if "errors" in result:
            for error in result["errors"]:
                print(error)
                raise Exception
        entry = []
        for value in result["arupComputeResultItems"]:

            entry.append(value["value"])

        output.append(entry)

    return output


def FCU_batchcalc(job_number, input_df):

    # input_df = pd.read_excel(file_name)
    sum_fcu = len(input_df["FCU ID"].tolist())

    # first calc
    inputs = {
        "calc_id": 3603604,
        "job_number": job_number,
        "variables": {
            "ID": input_df["FCU ID"].tolist(),
            "FR_S": input_df["Supply Air Flow Rate"].tolist(),
            "FR_F": input_df["Fresh Air Volume Flow Rate"].tolist(),
            "Q": input_df["Sensible Heat Gain"].tolist(),
            "Q_l": input_df["Latent Heat Gain"].tolist(),
            "T_R": input_df["Room Summer Setpoint"].tolist(),
            "T_F": input_df["Summer Fresh Air Temperature"].tolist(),
            "rh_F": input_df["Summer Fresh Air Relative Humidity"].tolist(),
            "T_coil": input_df["Minimum Temperature of Cooling Coil"].tolist(),
            "CF": input_df["Cooling Coil Contact Factor"].tolist(),
            "T_SFan_Rise": input_df["Supply Fan Temperature Rise"].tolist(),
            "Z": input_df["Altitude"].tolist(),
        },
    }

    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_summer = pd.DataFrame(input_df["FCU ID"].copy())
    output_df_summer["Supply Air Temperature"] = a[0]
    output_df_summer["Supply Air Relative Humidity"] = a[1]
    # output_df_summer["Return/Room Air Temperature"] = a[2]
    output_df_summer["Room Relative Humidity"] = a[3]
    output_df_summer["Cooling Coil Duty"] = a[4]
    output_df_summer["Heating Coil Duty"] = a[5]
    output_df_summer["Rate of Condensate Production"] = a[6]

    # second calc
    inputs = {
        "calc_id": 3776225,
        "job_number": job_number,
        "variables": {
            "ID": input_df["FCU ID"].tolist(),
            "Phi": output_df_summer["Heating Coil Duty"].tolist(),
            "T_flow": input_df["LTHW Flow Temp"].tolist(),
            "T_return": input_df["LTHW Return Temp"].tolist(),
            "glycol_c": [0] * sum_fcu,  # glycol_concentration,
            "glycol_type": ["none"] * sum_fcu,  # glycol_type,
        },
    }
    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_summer["LTHW Mass Flow Rate"] = a[0]

    # third calc
    inputs = {
        "calc_id": 3776225,
        "job_number": job_number,
        "variables": {
            "ID": input_df["FCU ID"].tolist(),
            "Phi": output_df_summer["Cooling Coil Duty"].tolist(),
            "T_flow": input_df["CHW Flow Temp"].tolist(),
            "T_return": input_df["CHW Return Temp"].tolist(),
            "glycol_c": input_df["CHW Glycol Concentration"].tolist(),
            "glycol_type": input_df["CHW Glycol Type"].tolist(),
        },
    }
    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_summer["CHW Mass Flow Rate"] = a[0]

    # fourth calc
    inputs = {
        "calc_id": 3603604,
        "job_number": job_number,
        "variables": {
            "ID": input_df["FCU ID"].tolist(),
            "FR_S": input_df["Supply Air Flow Rate"].tolist(),
            "FR_F": input_df["Fresh Air Volume Flow Rate"].tolist(),
            "Q": input_df["Winter Sensible Heat Gain"].tolist(),
            "Q_l": input_df["Winter Latent Heat Gain"].tolist(),
            "T_R": input_df["Room Winter Setpoint"].tolist(),
            "T_F": input_df["Winter Fresh Air Temperature"].tolist(),
            "rh_F": input_df["Winter Fresh Air Relative Humidity"].tolist(),
            "T_coil": input_df["Minimum Temperature of Cooling Coil"].tolist(),
            "CF": input_df["Cooling Coil Contact Factor"].tolist(),
            "T_SFan_Rise": input_df["Supply Fan Temperature Rise"].tolist(),
            "Z": input_df["Altitude"].tolist(),
        },
    }

    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_winter = pd.DataFrame(input_df["FCU ID"].copy())
    output_df_winter["Supply Air Temperature"] = a[0]
    output_df_winter["Supply Air Relative Humidity"] = a[1]
    # output_df_winter["Return/Room Air Temperature"] = a[2]
    output_df_winter["Room Relative Humidity"] = a[3]
    output_df_winter["Cooling Coil Duty"] = a[4]
    output_df_winter["Heating Coil Duty"] = a[5]
    output_df_winter["Rate of Condensate Production"] = a[6]

    # fifth calc
    inputs = {
        "calc_id": 3776225,
        "job_number": job_number,
        "variables": {
            "ID": input_df["FCU ID"].tolist(),
            "Phi": [
                -x for x in output_df_winter["Heating Coil Duty"].tolist()
            ],  # convert all to -ve counterparts
            "T_flow": input_df["LTHW Flow Temp"].tolist(),
            "T_return": input_df["LTHW Return Temp"].tolist(),
            "glycol_c": [0] * sum_fcu,  # glycol_concentration,
            "glycol_type": ["none"] * sum_fcu,  # glycol_type,
        },
    }
    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_winter["LTHW Mass Flow Rate"] = a[0]

    # sixth calc
    inputs = {
        "calc_id": 3776225,
        "job_number": job_number,
        "variables": {
            "ID": input_df["FCU ID"].tolist(),
            "Phi": output_df_winter["Cooling Coil Duty"].tolist(),
            "T_flow": input_df["CHW Flow Temp"].tolist(),
            "T_return": input_df["CHW Return Temp"].tolist(),
            "glycol_c": input_df["CHW Glycol Concentration"].tolist(),
            "glycol_type": input_df["CHW Glycol Type"].tolist(),
        },
    }
    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_winter["CHW Mass Flow Rate"] = a[0]

    return output_df_summer, output_df_winter


def fcu_calc(
    job_number: str,
    fcu_id: str,
    summer_fresh_air_temperature: int,
    summer_fresh_air_relative_humidity: int,
    winter_fresh_air_temperature: int,
    winter_fresh_air_relative_humidity: int,
    minimum_temperature_of_cooling_coil: int,
    cooling_coil_contact_factor: int,
    supply_fan_temperature_rise: int,
    altitude: int,
    lthw_flow_temp: int,
    lthw_return_temp: int,
    chw_flow_temp: int,
    chw_return_temp: int,
    chw_glycol_concentration: int,
    chw_glycol_type: str,
    supply_air_flow_rate: int,
    fresh_air_volume_flow_rate: int,
    sensible_heat_gain: int,
    latent_heat_gain: int,
    room_summer_setpoint: int,
    winter_sensible_heat_gain: int,
    winter_latent_heat_gain: int,
    room_winter_setpoint: int,
):

    input_df = pd.DataFrame(
        [
            {
                "FCU ID": fcu_id,
                "Fresh Air Temperature": summer_fresh_air_temperature,
                "Fresh Air Relative Humidity": summer_fresh_air_relative_humidity,
                "Winter Fresh Air Temperature": winter_fresh_air_temperature,
                "Winter Fresh Air Relative Humidity": winter_fresh_air_relative_humidity,
                "Minimum Temperature of Cooling Coil": minimum_temperature_of_cooling_coil,
                "Cooling Coil Contact Factor": cooling_coil_contact_factor,
                "Supply Fan Temperature Rise": supply_fan_temperature_rise,
                "Altitude": altitude,
                "LTHW Flow Temp": lthw_flow_temp,
                "LTHW Return Temp": lthw_return_temp,
                "CHW Flow Temp": chw_flow_temp,
                "CHW Return Temp": chw_return_temp,
                "CHW Glycol Concentration": chw_glycol_concentration,
                "CHW Glycol Type": chw_glycol_type,
                "Supply Air Flow Rate": supply_air_flow_rate,
                "Fresh Air Volume Flow Rate": fresh_air_volume_flow_rate,
                "Sensible Heat Gain": sensible_heat_gain,
                "Latent Heat Gain": latent_heat_gain,
                "Room Summer Setpoint": room_summer_setpoint,
                "Winter Sensible Heat Gain": winter_sensible_heat_gain,
                "Winter Latent Heat Gain": winter_latent_heat_gain,
                "Room Winter Setpoint": room_winter_setpoint,
            }
        ]
    )

    # Summer Fan Coil Duty
    inputs = {
        "calc_id": 3603604,
        "job_number": job_number,
        "variables": {
            "ID": [fcu_id],
            "FR_S": [supply_air_flow_rate],
            "FR_F": [fresh_air_volume_flow_rate],
            "Q": [sensible_heat_gain],
            "Q_l": [latent_heat_gain],
            "T_R": [room_summer_setpoint],
            "T_F": [summer_fresh_air_temperature],
            "rh_F": [summer_fresh_air_relative_humidity],
            "T_coil": [minimum_temperature_of_cooling_coil],
            "CF": [cooling_coil_contact_factor],
            "T_SFan_Rise": [supply_fan_temperature_rise],
            "Z": [altitude],
        },
    }

    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_summer = pd.DataFrame(input_df["FCU ID"].copy())
    output_df_summer["Supply Air Temperature"] = a[0]
    output_df_summer["Supply Air Relative Humidity"] = a[1]
    # output_df_summer["Return/Room Air Temperature"] = a[2]
    output_df_summer["Room Relative Humidity"] = a[3]
    output_df_summer["Cooling Coil Duty"] = a[4]
    output_df_summer["Heating Coil Duty"] = a[5]
    output_df_summer["Rate of Condensate Production"] = a[6]

    # Summer LTHW Flow Rate
    inputs = {
        "calc_id": 3776225,
        "job_number": job_number,
        "variables": {
            "ID": [fcu_id],
            "Phi": output_df_summer["Heating Coil Duty"].tolist(),
            "T_flow": [lthw_flow_temp],
            "T_return": [lthw_return_temp],
            "glycol_c": [0],  # glycol_concentration,
            "glycol_type": ["none"],  # glycol_type,
        },
    }
    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_summer["LTHW Mass Flow Rate"] = a[0]

    # Summer CHW Flow Rate
    inputs = {
        "calc_id": 3776225,
        "job_number": job_number,
        "variables": {
            "ID": [fcu_id],
            "Phi": output_df_summer["Cooling Coil Duty"].tolist(),
            "T_flow": input_df["CHW Flow Temp"].tolist(),
            "T_return": input_df["CHW Return Temp"].tolist(),
            "glycol_c": input_df["CHW Glycol Concentration"].tolist(),
            "glycol_type": input_df["CHW Glycol Type"].tolist(),
        },
    }
    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_summer["CHW Mass Flow Rate"] = a[0]

    # Winter Fan Coil Duty
    inputs = {
        "calc_id": 3603604,
        "job_number": job_number,
        "variables": {
            "ID": [fcu_id],
            "FR_S": input_df["Supply Air Flow Rate"].tolist(),
            "FR_F": input_df["Fresh Air Volume Flow Rate"].tolist(),
            "Q": input_df["Winter Sensible Heat Gain"].tolist(),
            "Q_l": input_df["Winter Latent Heat Gain"].tolist(),
            "T_R": input_df["Room Winter Setpoint"].tolist(),
            "T_F": input_df["Winter Fresh Air Temperature"].tolist(),
            "rh_F": input_df["Winter Fresh Air Relative Humidity"].tolist(),
            "T_coil": input_df["Minimum Temperature of Cooling Coil"].tolist(),
            "CF": input_df["Cooling Coil Contact Factor"].tolist(),
            "T_SFan_Rise": input_df["Supply Fan Temperature Rise"].tolist(),
            "Z": input_df["Altitude"].tolist(),
        },
    }

    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_winter = pd.DataFrame(input_df["FCU ID"].copy())
    output_df_winter["Supply Air Temperature"] = a[0]
    output_df_winter["Supply Air Relative Humidity"] = a[1]
    # output_df_winter["Room Air Temperature"] = a[2]
    output_df_winter["Room Relative Humidity"] = a[3]
    output_df_winter["Cooling Coil Duty"] = a[4]
    output_df_winter["Heating Coil Duty"] = a[5]
    output_df_winter["Rate of Condensate Production"] = a[6]

    # Winter LTHW Flow Rate
    inputs = {
        "calc_id": 3776225,
        "job_number": job_number,
        "variables": {
            "ID": [fcu_id],
            "Phi": [
                -x for x in output_df_winter["Heating Coil Duty"].tolist()
            ],  # convert all to -ve counterparts
            "T_flow": input_df["LTHW Flow Temp"].tolist(),
            "T_return": input_df["LTHW Return Temp"].tolist(),
            "glycol_c": [0],  # glycol_concentration,
            "glycol_type": ["none"],  # glycol_type,
        },
    }
    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_winter["LTHW Mass Flow Rate"] = a[0]

    # Winter CHW Flow Rate
    inputs = {
        "calc_id": 3776225,
        "job_number": job_number,
        "variables": {
            "ID": [fcu_id],
            "Phi": output_df_winter["Cooling Coil Duty"].tolist(),
            "T_flow": input_df["CHW Flow Temp"].tolist(),
            "T_return": input_df["CHW Return Temp"].tolist(),
            "glycol_c": input_df["CHW Glycol Concentration"].tolist(),
            "glycol_type": input_df["CHW Glycol Type"].tolist(),
        },
    }
    a = list(map(list, zip(*designcheck_batchcalc(inputs))))
    output_df_winter["CHW Mass Flow Rate"] = a[0]

    return input_df, output_df_summer, output_df_winter
