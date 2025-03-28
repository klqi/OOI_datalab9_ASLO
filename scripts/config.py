## set tables
## grab central mooring for chl and nitrate (2019-2023)
pioneer_chl = 'ooi-cp04ossm-rid27-02-flortd000'
pioneer_nitrate = 'ooi-cp01cnsm-rid26-07-nutnrb000'
pioneer_light = 'ooi-cp01cnsm-sbd11-06-metbka000'
irminger_chl = 'ooi-gi01sumo-sbd12-02-flortd000'
irminger_nitrate = 'ooi-gi01sumo-sbd11-08-nutnrb000'
irminger_light = 'ooi-gi01sumo-sbd12-06-metbka000'

# time constraints
start_time = "2019-01-01"
end_time = "2023-01-01"

# variables
p_chl_vars = ['time', 'mass_concentration_of_chlorophyll_a_in_sea_water', 'sea_water_temperature']
i_chl_vars = ['time', 'mass_concentration_of_chlorophyll_a_in_sea_water', 'sea_surface_temperature']
nitrate_vars = ['time', 'mole_concentration_of_nitrate_in_sea_water_suna', 'mole_concentration_of_nitrate_in_sea_water_suna_qc_agg']
light_vars = ['time','netsirr']

# store in lists
stations = ['Pioneer', 'Irminger']
chl_ids = [pioneer_chl, irminger_chl]
chl_vars = [p_chl_vars, i_chl_vars]
nitrate_ids = [pioneer_nitrate, irminger_nitrate]
light_ids = [pioneer_light, irminger_light]

# need to clean for chl in here bc temp has different col names :(
clean_cols_chl = ['time', 'chl' , 'sst', 'station']
clean_cols_nitrate = ['time', 'no3', 'qc_flag', 'station']
clean_cols_light = ['time', 'light', 'station']