import numpy as np
import pandas as pd

import core_func
import matplotlib.pyplot as plt


if __name__=="main":
    pass

params=pd.read_excel('Parameter.xlsx', index_col=0, header=0)
initial_conditions=pd.read_excel('Initial_Conditions.xlsx', index_col=0, header=0)
data=pd.read_excel('Data.xlsx')
basin_property=pd.read_excel('Basin.xlsx', index_col=0, header=0)

precip=data['Precip']
evapor=data['Evapor']

result=core_func.ini_soil_moisture(params, initial_conditions, precip, evapor)



r = result['r']
diff_source = core_func.different_sources(params, initial_conditions, precip, evapor, r)
rs = diff_source['rs']
ri = diff_source['ri']
rg = diff_source['rg']
flow_network=core_func.route_linear_resourvior(params, basin_property, initial_conditions, rs, ri, rg)
qt = flow_network['qt'].values.tolist()

plt.figure()
plt.plot(range(1,len(qt)+1),qt,label='Calculated Value')
plt.legend()
plt.show()
plt.savefig("D:/1.eps")


