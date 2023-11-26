import pandas

class PowerPlan:
    def __init__(self, payload: dict):
        # Get all necessary datas and informations
        self.payload = payload
        self.load = payload['load']
        self.gas = payload['fuels']['gas(euro/MWh)']
        self.kerosine = payload['fuels']['kerosine(euro/MWh)']
        self.co2 = payload['fuels']['co2(euro/ton)']
        self.wind = payload['fuels']['wind(%)']
        self.powerplants = pandas.DataFrame(data=self.payload['powerplants'])
        self.meritorder = []

    def _manage_date(self):
        # Manage the data by recovering costs for each powerplants and by sorting them
        self._get_costs()
        self.powerplants = self.powerplants.sort_values(by='cost', ascending=True)
    
    def _get_costs(self):
        # Calculate the cost price for each powerplant (Gas/Turbojet/Wind + CO2)
        co2_ton = 0.3
        for (index, column_data) in self.powerplants.iterrows():
            if column_data['type'] == "gasfired": 
                self.powerplants.loc[index, "cost"] = (self.gas / column_data['efficiency']) + (co2_ton * self.co2)
            elif column_data['type'] == "turbojet":
                self.powerplants.loc[index, "cost"] = self.kerosine / column_data['efficiency']
            elif column_data['type'] == "windturbine":
                self.powerplants.loc[index, "cost"] = 0
                self.powerplants.loc[index, "pmax"] = (column_data['pmax'] * self.wind) / 100
            else:
                pass

    def _set_merit_order(self):
        # Set of the merit order list
        data_copied = self.powerplants
        tmp_index = 0
        while (len(data_copied.index) != 0):
            # We gonna loop in the dataframe until every powerplant has been set in the merit order list and removed from the dataframe copied
            # If the powerplant is added to the merit order, it will be deleted from the dataframe copied
            for i in data_copied.index:
                row = data_copied.loc[i]
                # If there is no more load, the powerplant will be add to the merit order
                if self.load == 0:
                    tmp_index += 1
                    self.meritorder.append({"name": row['name'], "p": float(self.load)})
                    data_copied = data_copied.drop(i)
                elif (self.load - row['pmax'] >= 0) and row['pmax'] != 0:
                    # If the load is bigger than the PMAX, we can treat a part of the load
                    tmp_index += 1
                    pwr_to_use = self._check_next_plant(data_copied, tmp_index, row['pmax'])
                    self.load -= row['pmax']
                    self.meritorder.append({"name": row['name'], "p": float(pwr_to_use)})
                    data_copied = data_copied.drop(i)
                elif (self.load < row['pmax']) and row['pmax'] != 0:
                    # If the PMAX is bigger thant the load, we can treat all the load
                    tmp_index += 1
                    pwr_to_use = self._check_next_plant(data_copied, tmp_index, row['pmax'])
                    self.meritorder.append({"name": row['name'], "p": float(self.load)})
                    self.load = 0.0
                    data_copied = data_copied.drop(i)
                else:
                    tmp_index += 1
            tmp_index = 0
        return self.meritorder
    
    def _check_next_plant(self, data_copied: pandas.DataFrame, tmp_index, power_max):
        # Check if the next powerplant has enough PMIN to manage the rest of the load
        # We calculate the potential power we will user for the current powerplant, if its positive we will have a rest of load after that
        potential_power = self.load - power_max
        if (self.load != 0) and (potential_power > 0):
            if tmp_index < len(data_copied.index):
                # We get the next powerplant in the dataframe, and check if it will have  enough PMIN to treat the rest of load
                next_index = data_copied.index[tmp_index]
                next_row = data_copied.loc[next_index]

                if next_row['pmin'] > potential_power:
                    # If the next powerplant's PMIN is bigger than the potential power, we will have to adjust the current power to consume now 
                    # Oo we will have enough load to be treated by the next powerplant according to its PMIN
                    power_missing = next_row['pmin'] - potential_power
                    power_to_use = power_max - power_missing
                    return power_to_use
                else:
                    # Else, nothing to adjust, we can use the PMAX of the current powerplant
                    return power_max
            else: 
                pass
