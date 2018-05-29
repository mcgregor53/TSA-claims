import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
import seaborn as sns
sns.set(color_codes=True)

dtypes = {'Claim Number':str,
	'Date Received':str,
	'Incident Date':str,
	'Airport Code':str,
	'Airport Name':str,
	'Airline Name':str,
	'Claim Type':str,
	'Claim Site':str,
	'Item Category':str,
	'Claim Amount':float,
	'Status':str,
	'Close Amount':float,
	'Disposition':str}

data = pd.read_csv("../csv/all_claims.csv", dtype = dtypes, na_values = '-')
data['Incident Date'] = pd.to_datetime(data['Incident Date'], errors = 'coerce')
data['Date Received'] = pd.to_datetime(data['Date Received'], errors = 'coerce')




all_claims = data.copy()
all_claims = all_claims[all_claims['Incident Date'] > '2001-12-31']
all_claims = all_claims.groupby('Incident Date')['Claim Number'].count()
all_claims = all_claims.resample('4M').sum()
all_claims = pd.DataFrame(all_claims)
all_claims.rename(columns={'Claim Number':'Claims'}, inplace = True)

fig = all_claims.plot()
plt.title('All Claims Over Time')
plt.ylabel('Claims')
fig.legend_.remove()
plt.savefig('../plots/all_claims.png', dpi = 400, bbox_inches = 'tight')
plt.close()






times = data[['Date Received', 'Incident Date']].copy()
times['Time Elapsed'] = times['Date Received'] - times['Incident Date']

time_deltas = times['Time Elapsed']/np.timedelta64(1, 'D')
time_deltas = time_deltas[~ time_deltas.isnull()]
time_deltas = time_deltas[(0 <= time_deltas) & (time_deltas <= 150)]

fig = sns.distplot(time_deltas, kde = False, fit = stats.gamma)
plt.title('Time Elapsed Between Incident and Claim')
plt.xlabel('Days')
plt.ylabel('Density')


(a, loc, scale) = stats.gamma.fit(time_deltas)
plt.legend(['Gamma dist. fit (a={0:.2f}, loc={1:.2f}, scale={2:.2f})'.format(a, loc, scale), 'Time Elapsed'])
plt.savefig('../plots/wait_time.png', dpi = 400, bbox_inches = 'tight')
plt.close()

(D, p) = stats.kstest(time_deltas, 'gamma', args=(a, loc, scale))




payments = data[['Claim Number', 'Claim Amount', 'Close Amount', 'Status']].copy()
payments['Fraction'] = data['Close Amount'] / data['Claim Amount']
payments['Status'] = payments['Status'].str.replace('^Closed[\d\D]*', 'Closed')
payments['Status'] = payments['Status'].str.replace('^Insufficient[\d\D]*$', 'Insufficient')
payments['Status'] = payments['Status'].str.replace('[\d\D]*assigned[\d\D]*', 'Assigned')
payments['Status'] = payments['Status'].str.replace('^Pending[\d\D]*$', 'Pending')

fig = sns.countplot(y='Status', data=payments)
plt.title('Status of Claims')
plt.xlabel('Count')
plt.savefig('../plots/status.png', dpi = 400, bbox_inches = 'tight')
plt.close()

fig = sns.countplot(y='Status', data=payments)
plt.title('Status of Claims')
plt.xlabel('Count (Logarithmic Scale)')
fig.set_xscale('log')
plt.savefig('../plots/log_status.png', dpi = 400, bbox_inches = 'tight')
plt.close()




settled = payments[payments['Status'] == 'Settled']['Fraction']
settled = settled[settled < 1.1]

sns.distplot(settled, kde=False)
plt.title('Fraction of Claim Returned When Settling')
plt.xlabel('Fraction')
plt.ylabel('Count')
plt.savefig('../plots/settled.png', dpi = 400, bbox_inches = 'tight')
plt.close()





airlines = data[['Claim Number', 'Airline Name', 'Incident Date']].copy()
airlines = airlines.loc[airlines['Airline Name'].isin(['DELTAAIRLINES', 'AMERICANAIRLINES', 'UAL', 'SOUTHWESTAIRLINES'])]
airlines = airlines[airlines['Incident Date'] > '2001-12-31']
airlines = airlines[airlines['Incident Date'] < '2018-01-01']
airlines['Airline Name'] = airlines['Airline Name'].str.replace('DELTAAIRLINES', 'Delta')
airlines['Airline Name'] = airlines['Airline Name'].str.replace('AMERICANAIRLINES', 'American')
airlines['Airline Name'] = airlines['Airline Name'].str.replace('UAL', 'United')
airlines['Airline Name'] = airlines['Airline Name'].str.replace('SOUTHWESTAIRLINES', 'Southwest')

airlines = airlines.groupby([pd.Grouper(key='Incident Date', freq='4M'), 'Airline Name'])
airlines = airlines['Claim Number'].count()
airlines = pd.DataFrame(airlines)

(date_index, airline_index) = airlines.index.levels
new_index = pd.MultiIndex.from_product([date_index, airline_index])
airlines = airlines.reindex(new_index)
airlines = airlines.fillna(0).astype(int)
airlines.reset_index(inplace = True)
airlines.rename(columns = {"level_0":"Incident Date", "level_1":"Airline", "Claim Number":"Claims"}, inplace = True)

fig = sns.tsplot(data=airlines, time = 'Incident Date', value = 'Claims', condition = 'Airline', unit='Airline')
plt.xticks(fig.get_xticks(), pd.to_datetime(fig.get_xticks()).year)
plt.title('Claims Over Time for Major Airlines')
plt.savefig('../plots/by_airline.png', dpi = 400, bbox_inches = 'tight')
plt.close()



airports = data[['Claim Number', 'Airport Code', 'Incident Date']].copy()
airports = airports.loc[airports['Airport Code'].isin(['LAX', 'JFK', 'EWR', 'ORD', 'MCO', 'MIA', 'CMH'])]
airports = airports[airports['Incident Date'] > '2001-12-31']
# airports['Airline Name'] = airports['Airport Code'].str.replace('DELTAAIRLINES', 'Delta')
# airports['Airline Name'] = airports['Airport Code'].str.replace('AMERICANAIRLINES', 'American')
# airports['Airport Code'] = airports['Airport Code'].str.replace('UAL', 'United')
# airports['Airport Code'] = airports['Airport Code'].str.replace('SOUTHWESTAIRLINES', 'Southwest')

airports = airports.groupby([pd.Grouper(key='Incident Date', freq='8M'), 'Airport Code'])
airports = airports['Claim Number'].count()
airports = pd.DataFrame(airports)

(date_index, airport_index) = airports.index.levels
new_index = pd.MultiIndex.from_product([date_index, airport_index])
airports = airports.reindex(new_index)
airports = airports.fillna(0).astype(int)
airports.reset_index(inplace = True)
airports.rename(columns = {"level_0":"Incident Date", "level_1":"Airport", "Claim Number":"Claims"}, inplace = True)

fig = sns.tsplot(data=airports, time = 'Incident Date', value = 'Claims', condition = 'Airport', unit='Airport')
plt.xticks(fig.get_xticks(), pd.to_datetime(fig.get_xticks()).year)
plt.title('Claims Over Time for Major Airports')
plt.savefig('../plots/by_airport.png', dpi = 400, bbox_inches = 'tight')
plt.close()







weeks = data[['Claim Number', 'Incident Date']].copy()
weeks['Year'] = weeks['Incident Date'].dt.year
weeks = weeks[(2003 <= weeks['Year']) & (weeks["Year"] <= 2017)]
weeks['Week'] = weeks['Incident Date'].dt.week
weeks = weeks.groupby(['Year', 'Week'])['Claim Number'].count()
weeks = pd.DataFrame(weeks)

weeks.reset_index(inplace = True)
weeks.rename(columns = {"Claim Number":"Claims"}, inplace = True)

fig = sns.tsplot(data=weeks, time = 'Week', value = 'Claims', unit='Year')
plt.title('Claims Over a Year')
plt.savefig('../plots/avg_year.png', dpi = 400, bbox_inches = 'tight')
plt.close()





days = data[['Claim Number', 'Incident Date']].copy()
days['Year'] = days['Incident Date'].dt.year
days = days[(2003 <= days['Year']) & (days["Year"] <= 2017)]
days['Day'] = days['Incident Date'].dt.dayofyear
days = days.groupby(['Year', 'Day'])['Claim Number'].count()
days = pd.DataFrame(days)

days.reset_index(inplace = True)
days.rename(columns = {"Claim Number":"Claims"}, inplace = True)

fig = sns.tsplot(data=days, time = 'Day', value = 'Claims', unit='Year')
plt.title('Claims Over a Year')
plt.savefig('../plots/avg_year_day.png', dpi = 400, bbox_inches = 'tight')
plt.close()





items = data['Item Category'].str.split(';', expand = True)
items = pd.Series(items.values.ravel())
items = items[~ items.isnull()]
keeping = ['Other', 'Luggage(alltypesincludingfootlockers)', 'Clothing-Shoes,belts,accessories,etc.', 'Cameras-Digital', 'Jewelry-Fine', 'Baggage/Cases/Purses', 'Locks', 'Clothing', 'Computer-Laptop', 'Computer&Accessories', 'Jewelry&Watches']
items = items[items.isin(keeping)]
items = items.str.replace('Luggage[\d\D]*', 'Luggage')
items = items.str.replace('Clothing-[\d\D]*', 'Clothing Accessories')
items = items.str.replace('&', ' & ')
items = pd.DataFrame(items, columns=['Item Category'])


sns.countplot(y='Item Category', data=items)
plt.title('Category of Items Lost/Damaged (Top 11)')
plt.xlabel('Count')
plt.savefig('../plots/items.png', dpi = 400, bbox_inches = 'tight')
plt.close()





computers = data[['Claim Number', 'Incident Date', 'Item Category']].copy()
computers = computers[computers['Item Category'].str.contains('mputer', na = False)]
computers = computers[computers['Incident Date'] > '2001-12-31']
computers = computers.groupby('Incident Date')['Claim Number'].count()
computers = computers.resample('4M').sum()
computers = pd.concat([all_claims, computers], axis = 1)
computers.rename(columns={'Claims':'All Claims', 'Claim Number':'Computer Claims'}, inplace = True)

plt.xlabel('Incident Date')
fig1 = computers['All Claims'].plot(label = 'All Claims')
fig2 = computers['Computer Claims'].plot(label = 'Computer Claims', secondary_y = True)
plt.title('All Computer-Related Claims Over Time')
fig1.set_ylabel('All Claims')
fig2.set_ylabel('Computer Claims')
h1, l1 = fig1.get_legend_handles_labels()
h2, l2 = fig2.get_legend_handles_labels()
plt.legend(h1+h2, l1+l2)
plt.savefig('../plots/computers.png', dpi = 400, bbox_inches = 'tight')
plt.close()




place = data[['Claim Number', 'Claim Site']].copy()
place['Claim Site'] = place['Claim Site'].str.replace('[\s]', '')

fig = sns.countplot(y='Claim Site', data=place)
plt.title('Site of Claims (Top 7)')
plt.xlabel('Count')
plt.savefig('../plots/sites.png', dpi = 400, bbox_inches = 'tight')
plt.close()

fig = sns.countplot(y='Claim Site', data=place)
plt.title('Site of Claims (Top 7)')
plt.xlabel('Count (Logarithmic Scale)')
fig.set_xscale('log')
plt.savefig('../plots/log_sites.png', dpi = 400, bbox_inches = 'tight')
plt.close()


types = data['Claim Type'].str.split('/', expand = True)
types = pd.Series(types.values.ravel())
types = types[~ types.isnull()]
keeping2 = ['PassengerPropertyLoss', 'PropertyDamage', 'PersonalInjury', 'EmployeeLoss(MPCECA)', 'PassengerTheft', 'MotorVehicle']
types = types[types.isin(keeping2)]
types = types.str.replace('(?<=[a-z])(?=[A-Z\(])', ' ')
types = pd.DataFrame(types, columns=['Claim Type'])


fig = sns.countplot(y='Claim Type', data=types)
plt.title('Types of Claims Made (Top 6)')
plt.xlabel('Count')
plt.savefig('../plots/type.png', dpi = 400, bbox_inches = 'tight')
plt.close()


fig = sns.countplot(y='Claim Type', data=types)
plt.title('Types of Claims Made (Top 6)')
plt.xlabel('Count (Logarithmic Scale)')
fig.set_xscale('log')
plt.savefig('../plots/log_type.png', dpi = 400, bbox_inches = 'tight')
plt.close()
