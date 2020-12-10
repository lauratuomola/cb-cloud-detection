import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def validation(hits, misses, false_alarms):
    FAR = false_alarms/(false_alarms + hits)
    POD = hits/(hits + misses)
    BIAS = (hits + false_alarms)/(hits + misses)
    CSI = hits/(hits + false_alarms + misses)
    print("FAR: ", FAR)
    print("POD: ", POD)
    print("BIAS: ", BIAS)
    print("CSI: ", CSI)


def main():
    # print all rows:
    #    pd.set_option('display.max_rows', None)

    df_metar = pd.read_csv("havainnot_METAR.csv")
    df_radar = pd.read_csv("CB_status_EFHK.csv")

# dataframe metar with only time and clouds:
    df_metar_cloud = df_metar[["obstime", "745", "746", "747", "748"]]

# set obstime as index in metar data:
    df_cloud = df_metar_cloud.set_index("obstime")

# select metars only from year 2016-2020 (radar data has only from year 2016):
    df_cloud = df_cloud['2016-06-01T00:20:00Z':'2020-09-01T00:20:00Z']

# add month column to metar dataframe:
    months = [i.split('-')[1] for i in df_cloud.index]
    df_cloud['Month'] = months
# df radar with only 20 and 50 past the hour (since metars are taken then):
    df_radar_atfirst = df_radar[df_radar['minute'].isin(
        ['15', '20', '45', '50'])]
    df_radar_1545 = df_radar_atfirst.iloc[::2, :]
    df_radar = df_radar_atfirst[df_radar_atfirst['minute'].isin(['20', '50'])]
    df_radar['1545cb'] = df_radar_1545['cb'].values
    df_radar['1545minute'] = df_radar_1545['minute'].values


# turn time into separate column obstime (similar with METAR so the comparison is easier)
    df_radar["obstime"] = df_radar["year"].astype(str) + "-" + df_radar["month"].astype(
        str).str.zfill(2) + '-' + df_radar["day"].astype(str).str.zfill(2) + 'T' + df_radar["hour"].astype(
            str).str.zfill(2) + ':' + df_radar["minute"].astype(str).str.zfill(2) + ':00Z'

# select three months time period of different years:
# summer:
    df_metar_summers = df_cloud.loc[(df_cloud['Month'] == '06') | (
        df_cloud['Month'] == '07') | (df_cloud['Month'] == '08')]
    df_radar_summers = df_radar.loc[(df_radar['month'] == 6) | (
        df_radar['month'] == 7) | (df_radar['month'] == 8)]


# set obstime as index to easier access different timeslots:
    df_radar_summers = df_radar_summers.set_index("obstime")
    df_radar_summers['cb'] = df_radar_summers['cb'].fillna(0)
    df_radar_summers['1545cb'] = df_radar_summers['1545cb'].fillna(0)

# add column called Hour to df metar where there is only hour from obstime. This is for the later night and day time separation:
    hours_minutes = [i.split('T')[1] for i in df_metar_summers.index]
    hours = [i.split(':')[0] for i in hours_minutes]
    df_metar_summers["Hour_metar"] = hours
    df_metar_summers["Hour_metar"] = pd.to_numeric(
        df_metar_summers["Hour_metar"])

# select all the cb clouds into separate df metar:
    df_cb = df_metar_summers[((df_metar_summers['745'] == 3.0) | (df_metar_summers['746'] == 3.0) | (
        df_metar_summers['747'] == 3.0) | (df_metar_summers['748'] == 3.0))]
# put into separate df no cb clouds:
    df_not_cb = df_metar_summers.drop(df_cb.index)

# for plotting:
    df_cb_radar = df_radar_summers[((df_radar_summers['cb'] > 0) | (df_radar_summers['1545cb'] > 0))]
# plot picture of metar cb obs per hour:
    groups = df_cb.groupby(['Hour_metar'])
    groups_radar = df_cb_radar.groupby(['hour'])
    hours = []
    number_of_cb = []
    number_of_cb_radar = []
    for key, group in groups:
        hours.append(key)
        number_of_cb.append(len(group))
    for key, group in groups_radar:
        number_of_cb_radar.append(len(group))
    print(number_of_cb)
    print(number_of_cb_radar)
#    plt.scatter(hours, number_of_cb)
#    plt.bar(hours, number_of_cb, color='#86C8DF')
    df_plot = pd.DataFrame({'METAR': number_of_cb, 'Radar': number_of_cb_radar}, index=hours)
    df_plot.plot.bar(rot=0, color=['#86C8DF','#5F3BAD'])
    plt.title("Number of the Cb clouds observed in a given hour of the day")
    plt.xlabel("Hour of the day")
    plt.ylabel("Number of the Cb clouds")
    plt.show()

# cases where there _is_ cb in metar and/or not in radar:
# here we join the radar df with df_cb to get a df where cb is observed in metar:
    df_compared_cb = pd.merge(df_radar_summers,
                              df_cb, left_index=True, right_index=True)
# group by year:
    groups_year = df_compared_cb.groupby("year")
    group_year = groups_year.get_group(2020)
# group by month:
    groups_month = df_compared_cb.groupby("Month")
    group_month = groups_month.get_group('08')
#    print(group_month)

# select the cases from the df where also radar observed a cb:
#    df_cb_in_both = df_compared_cb[(df_compared_cb['cb'] > 0)]
#    df_cb_in_both = df_compared_cb[((df_compared_cb['cb'] > 0) | (df_compared_cb['1545cb'] > 0))]
    df_cb_in_both_year= group_year[((group_year['cb'] > 0) | (group_year['1545cb'] > 0))]
    print(df_cb_in_both_year)
    df_cb_in_both_month = group_month[((group_month['cb'] > 0) | (group_month['1545cb'] > 0))]
#    print(df_cb_in_both_month)
#    print(df_cb_in_both)
# select the cases from the df where radar did not observe cb but metar did:
#    df_cb_only_in_metar = df_compared_cb[(df_compared_cb['cb'] == 0)]
#    df_cb_only_in_metar = df_compared_cb[((df_compared_cb['cb'] == 0) & (df_compared_cb['1545cb'] == 0))]
    df_cb_only_in_metar_year = group_year[((group_year['cb'] == 0) & (group_year['1545cb'] == 0))]
    print(df_cb_only_in_metar_year)
    df_cb_only_in_metar_month = group_month[((group_month['cb'] == 0) & (group_month['1545cb'] == 0))]
#    print(df_cb_only_in_metar_month)
#    print(df_cb_only_in_metar)

# cases where there is _not_ cb in metar and/or not in radar:
# here we join the radar df with the df_not_cb to get a df where cb was not observed in metar:
    df_compared_not_cb = pd.merge(
        df_radar_summers, df_not_cb, left_index=True, right_index=True)
#    print(df_compared_not_cb)
# group by year:
    groups_year_not_cb = df_compared_not_cb.groupby("year")
    group_year_not_cb = groups_year_not_cb.get_group(2020)
# group by month:
    groups_not_month = df_compared_not_cb.groupby("Month")
    group_not_month = groups_not_month.get_group('08')
#    print(group_not_month)

# select cases from the df where there is not cb in radar either:
#    df_not_cb_in_both = df_compared_not_cb[(df_compared_not_cb['cb'] == 0)]
#    df_not_cb_in_both = df_compared_not_cb[(
#        (df_compared_not_cb['cb'] == 0) & (df_compared_not_cb['1545cb'] == 0))]
    print(group_year_not_cb[((group_year_not_cb['cb'] == 0) & (group_year_not_cb['1545cb'] == 0))])
    df_not_cb_in_both_month = group_not_month[((group_not_month['cb'] == 0) & (group_not_month['1545cb'] == 0))]
#    print(df_not_cb_in_both_month)
#    print(df_not_cb_in_both)
# select cases from the df where there IS cb in radar but not in metar:
#    df_cb_only_in_radar = df_compared_not_cb[(df_compared_not_cb['cb'] > 0)]
#    df_cb_only_in_radar = df_compared_not_cb[((df_compared_not_cb['cb'] > 0) | (df_compared_not_cb['1545cb'] > 0))]
    df_cb_only_in_radar_year = group_year_not_cb[((group_year_not_cb['cb'] > 0) | (group_year_not_cb['1545cb'] > 0))]
    print(df_cb_only_in_radar_year)
    df_cb_only_in_radar_month = group_not_month[((group_not_month['cb'] > 0) | (group_not_month['1545cb'] > 0))]
#    print(df_cb_only_in_radar_month)
#    print(df_cb_only_in_radar)

# validation calculations:
#    hits = len(df_cb_in_both)
#    misses = len(df_cb_only_in_metar)
#    false_alarms = len(df_cb_only_in_radar)
#    correct_negatives = len(df_not_cb_in_both)
# for the different years:
    hits = len(df_cb_in_both_year)
    misses = len(df_cb_only_in_metar_year)
    false_alarms = len(df_cb_only_in_radar_year)
#    correct_negatives = len(group_year_not_cb[(group_year_not_cb['cb'] == 0)])
# for the different months:
#    hits = len(df_cb_in_both_month)
#    misses = len(df_cb_only_in_metar_month)
#    false_alarms = len(df_cb_only_in_radar_month)
#    correct_negatives = len(df_not_cb_in_both_month)
    validation(hits, misses, false_alarms)


# -----------------------------------------------------------------------------------------
# this is for the extra day/night time data-analysis:

# DAY:

# df for day (6am-6pm utc) time cb metars:
    df_cb_day = df_cb[((df_cb['Hour_metar'] > 5) & (df_cb['Hour_metar'] < 18))]
#    print(df_cb_day)
# merge together radar data from 3 months period and metar cb day df:
    df_compared_cb_day = pd.merge(
        df_radar_summers, df_cb_day, left_index=True, right_index=True)
#    print(df_compared_cb_day)
# cb in both at day:
#    df_cb_in_both_day = df_compared_cb_day[(df_compared_cb_day['cb'] > 0)]
    df_cb_in_both_day = df_compared_cb_day[(
        (df_compared_cb_day['cb'] > 0) | (df_compared_cb_day['1545cb'] > 0))]
#    print(df_cb_in_both_day)
# cb in metar but not in radar:
    df_cb_only_in_metar_day = df_compared_cb_day[(
        (df_compared_cb_day['cb'] == 0) & (df_compared_cb_day['1545cb'] == 0))]
#    print(df_cb_only_in_metar_day)


# df for day time _no_ cb metars:
    df_not_cb_day = df_not_cb[(
        (df_not_cb['Hour_metar'] > 5) & (df_not_cb['Hour_metar'] < 18))]
#    print(df_not_cb_day)
# merge together radar data from 3 months period and metar _no_ cb day df:
    df_compared_no_cb_day = pd.merge(
        df_radar_summers, df_not_cb_day, left_index=True, right_index=True)
#    print(df_compared_no_cb_day)
# cb not in metar or radar:
    df_not_cb_in_both_day = df_compared_no_cb_day[(
        (df_compared_no_cb_day['cb'] == 0) & (df_compared_no_cb_day['1545cb'] == 0))]
#    print(df_not_cb_in_both_day)
# cb not in metar but there IS cb on radar:
    df_cb_only_in_radar_day = df_compared_no_cb_day[(
        (df_compared_no_cb_day['cb'] > 0) | (df_compared_no_cb_day['1545cb'] > 0))]
#    print(df_cb_only_in_radar_day)

# validation calculations:
    hits = len(df_cb_in_both_day)
    misses = len(df_cb_only_in_metar_day)
    false_alarms = len(df_cb_only_in_radar_day)
    correct_negatives = len(df_not_cb_in_both_day)
#    validation(hits, misses, false_alarms)


# NIGHT:

# df for night (6pm-6am utc) time cb metars:
    df_cb_night = df_cb[((df_cb['Hour_metar'] > 17) |
                         (df_cb['Hour_metar'] < 6))]
#    print(df_cb_night)
# merge together radar data from 3 months period and metar _no_ cb day df:
    df_compared_cb_night = pd.merge(
        df_radar_summers, df_cb_night, left_index=True, right_index=True)
#    print(df_compared_cb_night)
# cb in both at night:
    df_cb_in_both_night = df_compared_cb_night[(
        (df_compared_cb_night['cb'] > 0) | (df_compared_cb_night['1545cb'] > 0))]
#    print(df_cb_in_both_night)
# cb in metar but not in radar:
    df_cb_only_in_metar_night = df_compared_cb_night[(
        (df_compared_cb_night['cb'] == 0) & (df_compared_cb_night['1545cb'] == 0))]
#    print(df_cb_only_in_metar_night)

# df for night time _no_ cb metars:
    df_not_cb_night = df_not_cb[(
        (df_not_cb['Hour_metar'] > 17) | (df_not_cb['Hour_metar'] < 6))]
#    print(df_not_cb_night)
# merge together radar data from 3 months period and metar _no_ cb nigth df:
    df_compared_no_cb_night = pd.merge(
        df_radar_summers, df_not_cb_night, left_index=True, right_index=True)
#    print(df_compared_no_cb_night)
# cb not in metar or radar:
    df_not_cb_in_both_night = df_compared_no_cb_night[(
        (df_compared_no_cb_night['cb'] == 0) & (df_compared_no_cb_night['1545cb'] == 0))]
#    print(df_not_cb_in_both_night)
# cb not in metar but there IS cb on radar:
    df_cb_only_in_radar_night = df_compared_no_cb_night[(
        (df_compared_no_cb_night['cb'] > 0) | (df_compared_no_cb_night['1545cb'] > 0))]
#    print(len(df_cb_only_in_radar_night))

# validation calculations:
    hits = len(df_cb_in_both_night)
    misses = len(df_cb_only_in_metar_night)
    false_alarms = len(df_cb_only_in_radar_night)
    correct_negatives = len(df_not_cb_in_both_night)
#    validation(hits, misses, false_alarms)


main()
