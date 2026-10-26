"""Read-only RX Performance audit; output location is an explicit argument."""
from pathlib import Path
import argparse
import json
import math
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('export_root', type=Path, help='Extracted WSPRadar export root containing config/ and performance/')
parser.add_argument('output_dir', type=Path, help='Directory for computed audit CSV and JSON files')
parser.add_argument('--baseline-export-root', type=Path, help='Optional earlier export for exact retained-row comparison')
parser.add_argument('--figure-distance-bin-km', type=int, default=2500, help='Current figure bin width, explicitly checked against the figure footer')
args = parser.parse_args()
HERE = args.output_dir.resolve()
HERE.mkdir(parents=True, exist_ok=True)
SRC = args.export_root.resolve() / 'performance'
CONFIG = json.loads((args.export_root.resolve()/'config/wspradar_config.config').read_text())
QTH = CONFIG['settings']['core_parameters']['qth']
CORE = CONFIG['settings']['core_parameters']
ADV = CONFIG['settings']['advanced_parameters']
CAP = ADV['max_peer_distance_km']
MIN_OPPS = ADV['min_confirmed_opportunities_per_peer']
START = pd.Timestamp(CORE['time_selection']['start_utc'])
END = pd.Timestamp(CORE['time_selection']['end_utc'])
TIME_BIN = CONFIG['settings']['results_view']['performance']['segment_evidence_time_bin']
SELECTED_TIME_BIN = CONFIG['settings']['results_view']['performance']['station_evidence_time_bin']
assert TIME_BIN == SELECTED_TIME_BIN == '12h', 'This audit currently supports the saved 12 h case.'
T, E, S = 'Target (T)', 'Elsewhere (E)', 'Target SNR (dB @ 30 dBm)'
IDS = ['TX Station', 'Locator']
d = pd.read_csv(SRC / 'table_drilldown_all_stations_current_segment.csv')
d['time'] = pd.to_datetime(d['Date/Time (UTC)'], format='%d-%b-%Y %H:%M:%S', utc=True)
d['opps'] = d[T] + d[E]
d['hour'] = d.time.dt.hour
d['date'] = d.time.dt.strftime('%Y-%m-%d')
d['bin'] = START + ((d.time - START) // pd.Timedelta(TIME_BIN)) * pd.Timedelta(TIME_BIN)
d['id'] = d[IDS[0]] + ' (' + d[IDS[1]] + ')'

def grid_center(s):
    s = s.upper()
    lon, lat = -180., -90.
    wl, wh = 20., 10.
    for i in range(0, len(s), 2):
        if i == 0:
            a,b = ord(s[i])-65, ord(s[i+1])-65
        elif i % 4 == 2:
            wl, wh = wl/10., wh/10.
            a,b = int(s[i]), int(s[i+1])
        else:
            wl, wh = wl/24., wh/24.
            a,b = ord(s[i])-65, ord(s[i+1])-65
        lon += a*wl
        lat += b*wh
    return lat + wh/2., lon + wl/2.

def geo(grid):
    a,b = grid_center(QTH)
    c,e = grid_center(grid)
    a,b,c,e = map(math.radians,(a,b,c,e))
    dl = e-b
    hav = math.sin((c-a)/2)**2 + math.cos(a)*math.cos(c)*math.sin(dl/2)**2
    dist = 6371*2*math.asin(min(1,math.sqrt(hav)))
    az = math.degrees(math.atan2(math.sin(dl)*math.cos(c), math.cos(a)*math.sin(c)-math.sin(a)*math.cos(c)*math.cos(dl)))%360
    return dist,az

st = d.groupby('id').agg(sign=('TX Station','first'),grid=('Locator','first'),km=('km','first'),az=('Azimuth','first'),T=(T,'sum'),E=(E,'sum'),opps=('opps','sum'),snr=(S,'median'),first=('time','min'),last=('time','max'))
st['rate'] = 100*st['T']/st.opps
st['heard'] = st['T'] > 0
st[['distance_exact','azimuth_exact']] = pd.DataFrame([geo(x) for x in st.grid], index=st.index)
DIRS = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
st['direction'] = [DIRS[int((v+11.25)%360//22.5)] for v in st.azimuth_exact]
st['distance_bin'] = (st.distance_exact//args.figure_distance_bin_km).astype(int)*args.figure_distance_bin_km
st['distance_bin_1000'] = (st.distance_exact//1000).astype(int)*1000
RING_EDGES = [0] + [x for x in [2500,5000,10000,15000,20000,22000] if x < CAP] + [CAP]
RING_LABELS = [f'{int(a)}–{int(b)}' for a,b in zip(RING_EDGES[:-1], RING_EDGES[1:])]
st['ring'] = pd.cut(st.distance_exact, RING_EDGES, labels=RING_LABELS, include_lowest=True, right=False)

def summary(x):
    return pd.Series({'stations':len(x),'heard_stations':int(x.heard.sum()),'reach':100*x.heard.mean(),'successes':int(x['T'].sum()),'misses':int(x['E'].sum()),'opportunities':int(x.opps.sum()),'station_balanced_rate':x.rate.mean(),'opportunity_level_rate':100*x['T'].sum()/x.opps.sum(),'station_median_success_snr':x.snr.median() if x.snr.notna().any() else np.nan,'snr_station_count':int(x.snr.notna().sum())})

distance = st.groupby('distance_bin',observed=True).apply(summary,include_groups=False)
distance_1000 = st.groupby('distance_bin_1000',observed=True).apply(summary,include_groups=False)
ring_totals = st.groupby('ring',observed=True).apply(summary,include_groups=False)
count_cols = ['stations','heard_stations','successes','misses','opportunities','snr_station_count']
distance = distance.reindex(range(0, int(CAP), args.figure_distance_bin_km))
distance[count_cols] = distance[count_cols].fillna(0)
distance['distance_bin_end'] = [min(v+args.figure_distance_bin_km,CAP) for v in distance.index]
ring_totals = ring_totals.reindex(RING_LABELS)
ring_totals[count_cols] = ring_totals[count_cols].fillna(0)
maps = st.groupby(['ring','direction'],observed=True).apply(summary,include_groups=False)
overview = summary(st).to_dict()
overview.update({'outcomes':d.Outcome.value_counts().to_dict(),'min_station_opportunities':int(st.opps.min()),'min_timestamp':str(d.time.min()),'max_timestamp':str(d.time.max()),'unique_active_cycles_in_scope':int(d.time.nunique()),'cycles_with_scoped_qualified_success':int(d.loc[d[T].eq(1),'time'].nunique()),'duplicate_id_cycles':int(d.duplicated(['id','time']).sum()),'non_onehot_outcomes':int(d.opps.ne(1).sum()),'misses_with_snr':int((d[E].eq(1)&d[S].notna()).sum()),'successes_without_snr':int((d[T].eq(1)&d[S].isna()).sum()),'max_km_rounding_difference':float((st.km-st.distance_exact).abs().max()),'max_az_rounding_difference':float((st.az-st.azimuth_exact).abs().max()),'zero_snr_successes':int((d[T].eq(1)&d[S].eq(0)).sum())})
overview.update({'configured_distance_cap_km':CAP,'configured_minimum_opportunities':MIN_OPPS,'figure_distance_bin_km':args.figure_distance_bin_km,'missing_identity_rows':int(d[IDS].isna().any(axis=1).sum()),'malformed_locators':int((~st.grid.str.fullmatch(r'[A-R]{2}[0-9]{2}(?:[A-X]{2})?')).sum()),'below_minimum_opportunity_identities':int(st.opps.lt(MIN_OPPS).sum()),'cycles_off_two_minute_grid':int(((d.time.astype('int64')//10**9)%120).ne(0).sum()),'max_distance_km':float(st.distance_exact.max()),'identities_at_or_beyond_distance_cap':int(st.distance_exact.ge(CAP).sum()),'outside_requested_window_rows':int((d.time.lt(START)|d.time.ge(END)).sum())})

def rate_time(frame, by):
    z=frame.groupby(by).agg(successes=(T,'sum'),misses=(E,'sum'),opportunities=('opps','sum'),stations=('id','nunique'))
    sr=frame.groupby(['id',by]).agg(T=(T,'sum'),opps=('opps','sum'))
    sr['rate']=100*sr['T']/sr.opps
    z['station_balanced_rate']=sr['rate'].groupby(by).mean()
    z['opportunity_level_rate']=100*z.successes/z.opportunities
    return z

hourly = rate_time(d,'hour')
chronological = rate_time(d,'bin')
datehour = d.groupby(['date','hour']).agg(opportunities=('opps','sum'),stations=('id','nunique'))
hourly['mean_daily_station_presence']=datehour.stations.groupby('hour').sum()/d.date.nunique()
hourly['mean_daily_opportunities']=hourly.opportunities/d.date.nunique()
success = d[d[T].eq(1)].copy()
eligible = st.index[st['T'].ge(3)]
success_dev = success[success.id.isin(eligible)].copy()
success_dev['deviation'] = success_dev[S]-success_dev.id.map(st.snr)
dev_hour = success_dev.groupby(['id','date','hour']).deviation.median().reset_index()
dev_chrono = success_dev.groupby(['id','bin']).deviation.median().reset_index()
for key, tab, dat in [('hour',hourly,dev_hour),('bin',chronological,dev_chrono)]:
    p=dat.groupby(key).deviation.agg(['median','count','min','max'])
    p.columns=['snr_deviation_'+x for x in p.columns]
    tab[p.columns]=p
overview['stations_eligible_snr_deviation']=len(eligible)
overview['successes_eligible_snr_deviation']=len(success_dev)

hb = d[d.id.eq('HB0QRP (JN47)')].copy()
hb_hour = rate_time(hb,'hour')
hb_chrono = rate_time(hb,'bin')
hb_success = hb[hb[T].eq(1)]
hb_dh = hb_success.groupby(['date','hour'])[S].median().reset_index()
hb_hour['successful_datehour_median_snr']=hb_dh.groupby('hour')[S].median()
hb_hour['successful_dates']=hb_dh.groupby('hour')[S].count()
hb_hour['opportunity_dates']=hb.groupby('hour').date.nunique()
HB_DATES = hb.date.nunique()
hb_hour['mean_daily_successes']=hb_hour.successes/HB_DATES
hb_hour['mean_daily_misses']=hb_hour.misses/HB_DATES
hb_hour['mean_daily_station_presence']=hb_hour.opportunity_dates/HB_DATES
hb_chrono['successful_median_snr']=hb_success.groupby('bin')[S].median()
hb_chrono['successful_snr_count']=hb_success.groupby('bin')[S].count()
hb_chrono['successful_min_snr']=hb_success.groupby('bin')[S].min()
hb_chrono['successful_max_snr']=hb_success.groupby('bin')[S].max()
hb_overview=summary(st.loc[['HB0QRP (JN47)']]).to_dict()
hb_overview.update({'outcomes':hb.Outcome.value_counts().to_dict(),'first':str(hb.time.min()),'last':str(hb.time.max())})

for name,tab in [('stations',st),('distance',distance),('distance_1000km_audit_only',distance_1000),('ring_totals',ring_totals),('map_segments',maps),('global_hourly',hourly),('global_12h',chronological),('HB0QRP_hourly',hb_hour),('HB0QRP_12h',hb_chrono)]:
    tab.to_csv(HERE/(name+'.csv'))
hb[hb.Outcome.eq('Target-only')].to_csv(HERE/'HB0QRP_target_only_rows.csv',index=False)
hb[hb[S].eq(0)].to_csv(HERE/'HB0QRP_zero_snr_rows.csv',index=False)
hb.to_csv(HERE/'HB0QRP_all_processed_rows.csv',index=False)
examples=hb[hb['Date/Time (UTC)'].isin(['09-Apr-2017 18:08:00','09-Apr-2017 18:12:00','09-Apr-2017 18:16:00','09-Apr-2017 18:20:00'])]
examples.iloc[:,:9].to_csv(HERE/'recommended_drilldown_rows.csv',index=False)
witnesses=d[d.time.eq(pd.Timestamp('2017-04-09 18:20:00',tz='UTC'))&d[T].eq(1)]
witnesses.iloc[:,:9].to_csv(HERE/'2017-04-09_1820_Target_activity_witnesses.csv',index=False)
overview['example_miss_cycle_target_witness_rows']=len(witnesses)
selected=pd.read_csv(SRC/'table_drilldown_selected_stations.csv')
overview['selected_csv_matches_full_scope_subset']=bool(selected.equals(hb.iloc[:,:9].reset_index(drop=True)))
farthest = st[st.heard].sort_values('distance_exact',ascending=False).head(1)
farthest.to_csv(HERE/'farthest_heard_station.csv')
d[d.id.eq(farthest.index[0])&d[T].eq(1)].iloc[:,:9].to_csv(HERE/'farthest_heard_success_rows.csv',index=False)
if args.baseline_export_root:
    oldroot=args.baseline_export_root.resolve()
    oldconfig=json.loads((oldroot/'config/wspradar_config.config').read_text())
    oldcap=oldconfig['settings']['advanced_parameters']['max_peer_distance_km']
    old=pd.read_csv(oldroot/'performance/table_drilldown_all_stations_current_segment.csv')
    oldselected=pd.read_csv(oldroot/'performance/table_drilldown_selected_stations.csv')
    oldids=old[IDS[0]]+' ('+old[IDS[1]]+')'
    new_in_old_scope=d[d.id.isin(st.index[st.distance_exact.lt(oldcap)])].iloc[:,:9].reset_index(drop=True)
    baseline={
        'old_distance_cap':oldcap,
        'old_rows':len(old),
        'new_rows_below_old_cap':len(new_in_old_scope),
        'old_scope_rows_exactly_equal_ordered':bool(old.equals(new_in_old_scope)),
        'old_scope_rows_exactly_equal_sorted':bool(old.sort_values(list(old.columns),na_position='last').reset_index(drop=True).equals(new_in_old_scope.sort_values(list(old.columns),na_position='last').reset_index(drop=True))),
        'selected_csv_bytes_identical':(oldroot/'performance/table_drilldown_selected_stations.csv').read_bytes()==(SRC/'table_drilldown_selected_stations.csv').read_bytes(),
        'selected_csv_values_identical':bool(oldselected.equals(selected)),
        'old_identity_count':int(oldids.nunique()),
        'old_identities_missing_new':len(set(oldids)-set(st.index)),
        'new_identities':len(set(st.index)-set(oldids)),
        'added_scope':summary(st[st.distance_exact.ge(oldcap)]).to_dict(),
    }
    old_st=old.groupby(IDS).agg(T=(T,'sum'),E=(E,'sum'))
    old_st['opps']=old_st['T']+old_st['E']
    oldvalues={'stations':len(old_st),'heard_stations':int(old_st['T'].gt(0).sum()),'successes':int(old_st['T'].sum()),'misses':int(old_st['E'].sum()),'opportunities':int(old_st.opps.sum()),'reach':100*old_st['T'].gt(0).mean(),'station_balanced_rate':(100*old_st['T']/old_st.opps).mean(),'opportunity_level_rate':100*old_st['T'].sum()/old_st.opps.sum(),'stations_eligible_snr_deviation':int(old_st['T'].ge(3).sum()),'successes_eligible_snr_deviation':int(old_st.loc[old_st['T'].ge(3),'T'].sum())}
    ledger=pd.DataFrame([{'claim':k,'old':v,'new':overview[k],'difference':overview[k]-v} for k,v in oldvalues.items()])
    ledger.to_csv(HERE/'claim_change_ledger.csv',index=False)
    oldtable=pd.read_csv(oldroot/'performance/table_station_insights_current_segment.csv')
    newtable=pd.read_csv(SRC/'table_station_insights_current_segment.csv')
    baseline['old_visible_station_table_rows']=len(oldtable)
    baseline['new_visible_station_table_rows']=len(newtable)
    baseline['new_visible_station_table_successes']=int(newtable[T].sum())
    baseline['new_visible_station_table_misses']=int(newtable[E].sum())
    oldtable_indexed=oldtable.set_index(IDS).sort_index()
    newtable_indexed=newtable.set_index(IDS).sort_index()
    baseline['old_station_table_values_preserved']=bool(newtable_indexed.loc[oldtable_indexed.index].equals(oldtable_indexed))
    (HERE/'baseline_comparison.json').write_text(json.dumps(baseline,indent=2,default=str)+'\n')
(HERE/'overview.json').write_text(json.dumps({'all':overview,'HB0QRP':hb_overview},indent=2,default=str)+'\n')
print(json.dumps({'all':overview,'HB0QRP':hb_overview},indent=2,default=str))
print('\nDISTANCE\n',distance.to_string())
print('\nMAPS\n',maps.to_string())
print('\nHB HOURS\n',hb_hour.to_string())
print('\nGLOBAL HOURS\n',hourly.to_string())
print('\nHB CHRONOLOGICAL\n',hb_chrono.to_string())
print('\nHB TARGET ONLY FIRST\n',hb[hb.Outcome.eq('Target-only')].head(8).to_string(index=False))
print('\nHB GENUINE ZERO\n',hb[hb[S].eq(0)].to_string(index=False))
