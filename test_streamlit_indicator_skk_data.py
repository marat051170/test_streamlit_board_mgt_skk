import pandas as pd
import plotly.express as px
import streamlit as st
from isoweek import Week




st.set_page_config(page_title='Запрет к эксплуатации', page_icon=':bar_chart:', layout='wide')
st.title('Данные СКК')
st.sidebar.header('Фильтры')

bans_data = pd.read_excel('test_indicator_banned_for_exploitation.xlsx')

depot = st.sidebar.multiselect('Парк:', options=bans_data['assigned_organization_name'].unique(), default=bans_data['assigned_organization_name'].unique())
months = st.sidebar.multiselect('Месяцы:', options=bans_data['month'].unique(), default=bans_data['month'].unique())
vehicle_types = st.sidebar.multiselect('Типы ТС:', options=bans_data['Тип_ТС'].unique(), default=bans_data['Тип_ТС'].unique())
bans_data_filtered = bans_data.query('assigned_organization_name == @depot & month == @months & Тип_ТС == @vehicle_types')

bans_data_filtered['number_of_vehicles'] = bans_data_filtered['number_of_vehicles'].fillna(0)
bans_data_filtered = bans_data_filtered.groupby(by=['week_name', 'number_of_vehicles']).count()[['id']].reset_index()
bans_data_filtered = bans_data_filtered[bans_data_filtered['number_of_vehicles'] != 0]
bans_data_filtered = bans_data_filtered.groupby(by=['week_name']).sum()[['number_of_vehicles', 'id']]
bans_data_filtered['indicator'] = bans_data_filtered['id'] / bans_data_filtered['number_of_vehicles'] * 100

st.subheader('Количество ТС, выявленных на выпуске с нарушениями, запрещающими эксплуатацию, ед. (на 100 проверенных ТС)')
st.bar_chart(bans_data_filtered, y='indicator')


san_violation_data = pd.read_excel('test_indicator_sanitary_condition_violations.xlsx')
san_violation_data_filtered = san_violation_data.query('assigned_organization_name == @depot & month == @months & Тип_ТС == @vehicle_types')

san_violation_data_filtered['number_of_vehicles'] = san_violation_data_filtered['number_of_vehicles'].fillna(0)
san_violation_data_filtered = san_violation_data_filtered.groupby(by=['week_name', 'number_of_vehicles']).count()[['id']].reset_index()
san_violation_data_filtered = san_violation_data_filtered[san_violation_data_filtered['number_of_vehicles'] != 0]
san_violation_data_filtered = san_violation_data_filtered.groupby(by=['week_name']).sum()[['number_of_vehicles', 'id']]
san_violation_data_filtered['indicator'] = san_violation_data_filtered['id'] / san_violation_data_filtered['number_of_vehicles'] * 100

st.subheader('Количество нарушений требований к санитарному состоянию ТС, ед. (на 100 проверенных ТС)')
st.bar_chart(san_violation_data_filtered, y='indicator')