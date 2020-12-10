# import needed packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# to calculate validation scores:
def validation(hits, misses, false_alarms):
    FAR = false_alarms/(false_alarms + hits)
    POD = hits/(hits + misses)
    BIAS = (hits + false_alarms)/(hits + misses)
    CSI = hits/(hits + false_alarms + misses)
    print("FAR: ", FAR)
    print("POD: ", POD)
    print("BIAS: ", BIAS)
    print("CSI: ", CSI)

# to fix the METAR data to proper form:
def metar(df):
# metar df with only time and clouds:
    df_metar_cloud = df[["obstime", "745", "746", "747", "748"]]
# set obstime as index in metar data:
    df_metar_cloud = df_metar_cloud.set_index("obstime")
# select metars only from years 2016-2020 (radar data has only these years):
    df_metar_cloud = df_metar_cloud['2016-06-01T00:20:00Z':'2020-09-01T00:20:00Z']
# add month column to metar dataframe to make the month comparison easier:
    months = [i.split('-')[1] for i in df_metar_cloud.index]
    df_metar_cloud['Month'] = months

# select only summer months:
    df_metar_summers = df_metar_cloud.loc[(df_metar_cloud['Month'] == '06') | (
        df_metar_cloud['Month'] == '07') | (df_metar_cloud['Month'] == '08')]

# add column called Hour to df where there is only hour from obstime. This is for the later night and day time separation:
    hours_minutes = [i.split('T')[1] for i in df_metar_summers.index]
    hours = [i.split(':')[0] for i in hours_minutes]
    df_metar_summers["Hour_metar"] = hours
    df_metar_summers["Hour_metar"] = pd.to_numeric(df_metar_summers["Hour_metar"])

    return df_metar_summers

# to fix radar data to proper form:
def radar(df):
# df radar with only 15,20,45,50 past the hour (since metars are taken then):
    df_radar = df[df['minute'].isin(['15', '20', '45', '50'])]
# comment the next lines if only 20 and 50 past the hour are wanted into calculations:
    df_radar_1545 = df_radar.iloc[::2, :]
    df = df_radar[df_radar['minute'].isin(['20', '50'])]
    df['1545cb'] = df_radar_1545['cb'].values
    df['1545minute'] = df_radar_1545['minute'].values

# turn time into separate column obstime (similar with METAR so the comparison is easier)
    df["obstime"] = df["year"].astype(str) + "-" + df["month"].astype(
        str).str.zfill(2) + '-' + df["day"].astype(str).str.zfill(2) + 'T' + df["hour"].astype(
            str).str.zfill(2) + ':' + df["minute"].astype(str).str.zfill(2) + ':00Z'

# select only summer months:
    df_radar_summers = df.loc[(df['month'] == 6) | ( df['month'] == 7) | (df['month'] == 8)]

# set obstime as index to easier access different timeslots:
    df_radar_summers = df_radar_summers.set_index("obstime")
# nan values into 0:
    df_radar_summers['cb'] = df_radar_summers['cb'].fillna(0)
    df_radar_summers['1545cb'] = df_radar_summers['1545cb'].fillna(0)

    return df_radar_summers


def plotting(metars, radar):
# if only metars want to be plotted, comment lines where radar is mentioned!

# plot picture of metar cb obs per hour:
    groups = metars.groupby(['Hour_metar'])
    groups_radar = radar.groupby(['hour'])

    hours = []
    number_of_cb = []
    number_of_cb_radar = []
    for key, group in groups:
        hours.append(key)
        number_of_cb.append(len(group))
    for key, group in groups_radar:
        number_of_cb_radar.append(len(group))

    df_plot = pd.DataFrame({'METAR': number_of_cb, 'Radar': number_of_cb_radar}, index=hours)
    df_plot.plot.bar(rot=0, color=['#86C8DF','#5F3BAD'])
    plt.title("Number of the Cb clouds observed in a given hour of the day")
    plt.xlabel("Hour of the day")
    plt.ylabel("Number of the Cb clouds")
    plt.show()


def whole(df_compared_cb, df_compared_not_cb):
# select the cases from the df where also radar observed a cb:
# if only 20 and 50 past the hour are considered:
#    df_cb_in_both = df_compared_cb[(df_compared_cb['cb'] > 0)]
    df_cb_in_both = df_compared_cb[((df_compared_cb['cb'] > 0) | (df_compared_cb['1545cb'] > 0))]

# select the cases from the df where radar did not observe cb but metar did:
#    df_cb_only_in_metar = df_compared_cb[(df_compared_cb['cb'] == 0)]
    df_cb_only_in_metar = df_compared_cb[((df_compared_cb['cb'] == 0) & (df_compared_cb['1545cb'] == 0))]


# select cases from the df where there is not cb in radar either:
# if only 20 and 50 past the hour are considered:
#    df_not_cb_in_both = df_compared_not_cb[(df_compared_not_cb['cb'] == 0)]
    df_not_cb_in_both = df_compared_not_cb[(
        (df_compared_not_cb['cb'] == 0) & (df_compared_not_cb['1545cb'] == 0))]

# select cases from the df where there IS cb in radar but not in metar:
# if only 20 and 50 past the hour are considered:
#    df_cb_only_in_radar = df_compared_not_cb[(df_compared_not_cb['cb'] > 0)]
    df_cb_only_in_radar = df_compared_not_cb[((df_compared_not_cb['cb'] > 0) | (df_compared_not_cb['1545cb'] > 0))]

# for validation:
    hits = len(df_cb_in_both)
    misses = len(df_cb_only_in_metar)
    false_alarms = len(df_cb_only_in_radar)
    correct_negatives = len(df_not_cb_in_both)

    print("hits: ", hits)
    print("misses: ", misses)
    print("false alarms: ", false_alarms)
    print("correct negatives: ", correct_negatives)

    return validation(hits, misses, false_alarms)


def year(df_compared_cb, df_compared_not_cb):
# group by year (year can be 2016, 2017, 2018, 2019 or 2020):
    groups_year = df_compared_cb.groupby("year")
    group_year = groups_year.get_group(2020)
    groups_year_not_cb = df_compared_not_cb.groupby("year")
    group_year_not_cb = groups_year_not_cb.get_group(2020)

# select rows where radar also detected cb
    df_cb_in_both_year= group_year[((group_year['cb'] > 0) | (group_year['1545cb'] > 0))]

# select rows where radar did not detect cb:
    df_cb_only_in_metar_year = group_year[((group_year['cb'] == 0) & (group_year['1545cb'] == 0))]

# select rows where there is not cb in both:
    df_not_cb_in_both_year = group_year_not_cb[((group_year_not_cb['cb'] == 0) & (group_year_not_cb['1545cb'] == 0))]

# select rows where cb only in radar:
    df_cb_only_in_radar_year = group_year_not_cb[((group_year_not_cb['cb'] > 0) | (group_year_not_cb['1545cb'] > 0))]

# validation:
    hits = len(df_cb_in_both_year)
    misses = len(df_cb_only_in_metar_year)
    false_alarms = len(df_cb_only_in_radar_year)
    correct_negatives = len(df_not_cb_in_both_year)

    print("hits: ", hits)
    print("misses: ", misses)
    print("false alarms: ", false_alarms)
    print("correct negatives: ", correct_negatives)

    return validation(hits, misses, false_alarms)


def month(df_compared_cb, df_compared_not_cb):
# group by month (the value of month needs to be changed 06, 07 or 08):
    groups_month = df_compared_cb.groupby("Month")
    group_month = groups_month.get_group('08')
    groups_not_month = df_compared_not_cb.groupby("Month")
    group_not_month = groups_not_month.get_group('08')

# select rows where radar also detected cb:
    df_cb_in_both_month = group_month[((group_month['cb'] > 0) | (group_month['1545cb'] > 0))]

# select rows where radar did not detect cb:
    df_cb_only_in_metar_month = group_month[((group_month['cb'] == 0) & (group_month['1545cb'] == 0))]

# select rows where there is not cb in both:
    df_not_cb_in_both_month = group_not_month[((group_not_month['cb'] == 0) & (group_not_month['1545cb'] == 0))]

# select rows where cb only in radar:
    df_cb_only_in_radar_month = group_not_month[((group_not_month['cb'] > 0) | (group_not_month['1545cb'] > 0))]

# for validation:
    hits = len(df_cb_in_both_month)
    misses = len(df_cb_only_in_metar_month)
    false_alarms = len(df_cb_only_in_radar_month)
    correct_negatives = len(df_not_cb_in_both_month)

    print("hits: ", hits)
    print("misses: ", misses)
    print("false alarms: ", false_alarms)
    print("correct negatives: ", correct_negatives)

    return validation(hits, misses, false_alarms)


def daynight(df_cb_day, df_not_cb_day, df_cb_night, df_not_cb_night):
# DAYTIME:
# cb in both at day:
# if only 20 and 50 past the hour are considered:
#    df_cb_in_both_day = df_compared_cb_day[(df_compared_cb_day['cb'] > 0)]
    df_cb_in_both_day = df_cb_day[(
        (df_cb_day['cb'] > 0) | (df_cb_day['1545cb'] > 0))]

# cb in metar but not in radar:
    df_cb_only_in_metar_day = df_cb_day[(
        (df_cb_day['cb'] == 0) & (df_cb_day['1545cb'] == 0))]

# cb not in metar or radar:
    df_not_cb_in_both_day = df_not_cb_day[(
        (df_not_cb_day['cb'] == 0) & (df_not_cb_day['1545cb'] == 0))]

# cb not in metar but there IS cb on radar:
    df_cb_only_in_radar_day = df_not_cb_day[(
        (df_not_cb_day['cb'] > 0) | (df_not_cb_day['1545cb'] > 0))]

# for validation:
    hits_d = len(df_cb_in_both_day)
    misses_d = len(df_cb_only_in_metar_day)
    false_alarms_d = len(df_cb_only_in_radar_day)
    correct_negatives_d = len(df_not_cb_in_both_day)

    print("DAY:")
    print("hits: ", hits_d)
    print("misses: ", misses_d)
    print("false alarms: ", false_alarms_d)
    print("correct negatives: ", correct_negatives_d)

# NIGHTTIME:
# cb in both at night:
    df_cb_in_both_night = df_cb_night[(
        (df_cb_night['cb'] > 0) | (df_cb_night['1545cb'] > 0))]
#    print(df_cb_in_both_night)
# cb in metar but not in radar:
    df_cb_only_in_metar_night = df_cb_night[(
        (df_cb_night['cb'] == 0) & (df_cb_night['1545cb'] == 0))]

# cb not in metar or radar:
    df_not_cb_in_both_night = df_not_cb_night[(
        (df_not_cb_night['cb'] == 0) & (df_not_cb_night['1545cb'] == 0))]
#    print(df_not_cb_in_both_night)
# cb not in metar but there IS cb on radar:
    df_cb_only_in_radar_night = df_not_cb_night[(
        (df_not_cb_night['cb'] > 0) | (df_not_cb_night['1545cb'] > 0))]

# for validation:
    hits_n = len(df_cb_in_both_night)
    misses_n = len(df_cb_only_in_metar_night)
    false_alarms_n = len(df_cb_only_in_radar_night)
    correct_negatives_n = len(df_not_cb_in_both_night)

    print("NIGHT:")
    print("hits: ", hits_n)
    print("misses: ", misses_n)
    print("false alarms: ", false_alarms_n)
    print("correct negatives: ", correct_negatives_n)


    return validation(hits_d, misses_d, false_alarms_d), validation(hits_n, misses_n, false_alarms_n)



def main():
# print all rows:
#    pd.set_option('display.max_rows', None)

    df_metar = pd.read_csv("havainnot_METAR.csv")
    df_radar = pd.read_csv("CB_status_EFHK.csv")

    df_metar_fixed = metar(df_metar)
    df_radar_fixed = radar(df_radar)
#    print(df_metar_fixed)
#    print(df_radar_fixed)


# select all the cb clouds from metars into separate df :
    df_cb = df_metar_fixed[((df_metar_fixed['745'] == 3.0) | (df_metar_fixed['746'] == 3.0) | (
        df_metar_fixed['747'] == 3.0) | (df_metar_fixed['748'] == 3.0))]
# put into separate df no cb clouds:
    df_not_cb = df_metar_fixed.drop(df_cb.index)

# for plotting:
    df_cb_radar = df_radar_fixed[((df_radar_fixed['cb'] > 0) | (df_radar_fixed['1545cb'] > 0))]
#    plotting(df_cb, df_cb_radar)

# cases where there _is_ cb in metar and/or not in radar:
# here we join the radar df with df_cb to get a df where cb is observed in metar:
    df_compared_cb = pd.merge(df_radar_fixed,
                              df_cb, left_index=True, right_index=True)
# cases where there is _not_ cb in metar and/or not in radar:
# here we join the radar df with the df_not_cb to get a df where cb was not observed in metar:
    df_compared_not_cb = pd.merge(
        df_radar_fixed, df_not_cb, left_index=True, right_index=True)

# whole data:
    whole(df_compared_cb, df_compared_not_cb)

# different years:
    year(df_compared_cb, df_compared_not_cb)

# different months:
    month(df_compared_cb, df_compared_not_cb)


# day/night:
    df_cb_day = df_cb[((df_cb['Hour_metar'] > 5) & (df_cb['Hour_metar'] < 18))]
# merge together radar data from 3 months period and metar cb day df:
    df_compared_cb_day = pd.merge(
        df_radar_fixed, df_cb_day, left_index=True, right_index=True)
# df for day time _no_ cb metars:
    df_not_cb_day = df_not_cb[(
        (df_not_cb['Hour_metar'] > 5) & (df_not_cb['Hour_metar'] < 18))]
    df_compared_no_cb_day = pd.merge(
        df_radar_fixed, df_not_cb_day, left_index=True, right_index=True)

# df for night (6pm-6am utc) time cb metars:
    df_cb_night = df_cb[((df_cb['Hour_metar'] > 17) |
                         (df_cb['Hour_metar'] < 6))]
# merge together radar data from 3 months period and metar cb night df:
    df_compared_cb_night = pd.merge(
        df_radar_fixed, df_cb_night, left_index=True, right_index=True)
# df for night time _no_ cb metars:
    df_not_cb_night = df_not_cb[(
        (df_not_cb['Hour_metar'] > 17) | (df_not_cb['Hour_metar'] < 6))]
    df_compared_no_cb_night = pd.merge(
        df_radar_fixed, df_not_cb_night, left_index=True, right_index=True)

    daynight(df_compared_cb_day, df_compared_no_cb_day, df_compared_cb_night, df_compared_no_cb_night)


main()
