import pandas as pd
import plotly.express as px
import streamlit as st
from isoweek import Week


@st.cache
def get_bans_data():
    bans_data = pd.read_excel('test_indicator_banned_for_exploitation.xlsx')
    return bans_data


@st.cache
def get_sani_violation_data():
    sani_violation_data = pd.read_excel('test_indicator_sanitary_condition_violations.xlsx')
    return sani_violation_data


@st.cache
def get_territory_violation_data():
    territory_violation_data = pd.read_excel('test_indicator_territory_violations.xlsx')
    return territory_violation_data


st.set_page_config(page_title='Показатели из СКК', page_icon=':bar_chart:', layout='wide')
st.title('Показатели на данных СКК')
st.sidebar.header('Фильтры')


# Filters -------------------------------------------------------------------------

cols_for_filters = ['month', 'Перевозчик', 'Филиал', 'Парк']
filters_values = pd.concat([get_bans_data()[cols_for_filters], get_sani_violation_data()[cols_for_filters]], sort=False).drop_duplicates()
filters_values = pd.concat([filters_values, get_territory_violation_data()[cols_for_filters]], sort=False)

carrier = st.sidebar.multiselect('Перевозчик:', options=filters_values['Перевозчик'].unique(), default=filters_values['Перевозчик'].unique())
filters_values_carrier = filters_values.query('Перевозчик == @carrier')

months = st.sidebar.multiselect('Месяцы:', options=filters_values_carrier['month'].unique(), default=filters_values_carrier['month'].unique())
filters_values_carrier_month = filters_values_carrier.query('month == @months')

branсhes = st.sidebar.multiselect(
    'Филиал:', options=filters_values_carrier_month['Филиал'].unique(), default=filters_values_carrier_month['Филиал'].unique())
filters_values_carrier_month_branches = filters_values_carrier_month.query('Филиал == @branсhes')

depots = st.sidebar.multiselect(
    'Парк:', options=filters_values_carrier_month_branches['Парк'].unique(), default=filters_values_carrier_month_branches['Парк'].unique())
filters_values_carrier_month_branches = filters_values_carrier_month_branches.query('Парк == @depots')


# Bans ----------------------------------------------------------------------------

bans_data_filtered = get_bans_data().query('Перевозчик == @carrier & month == @months & Филиал == @branсhes & Парк == @depots').copy()
bans_data_filtered['проверено_ТС'] = 1
bans_data_filtered_unique_vehicles_gr = bans_data_filtered.groupby(by=['week_name', 'Наименование']).sum()[['Запрет', 'проверено_ТС']].reset_index()
for col in ['Запрет', 'проверено_ТС']:
    bans_data_filtered_unique_vehicles_gr[col] = bans_data_filtered_unique_vehicles_gr[col].apply(lambda x: 1 if x != 0 else x)
bans_data_filtered_unique_vehicles_gr = bans_data_filtered_unique_vehicles_gr.groupby(by=['week_name']).sum()[['Запрет', 'проверено_ТС']]
bans_data_filtered_unique_vehicles_gr['Количество запретов на 100 ТС'] = bans_data_filtered_unique_vehicles_gr[
    'Запрет'] / bans_data_filtered_unique_vehicles_gr['проверено_ТС'] * 100

st.subheader('Количество ТС, выявленных на выпуске с нарушениями, запрещающими эксплуатацию, ед. (на 100 проверенных ТС)')
st.bar_chart(bans_data_filtered_unique_vehicles_gr, y='Количество запретов на 100 ТС')


# Sanitury violations ---------------------------------------------------------------

sani_violation_data_filtered = get_sani_violation_data().query('Перевозчик == @carrier & month == @months & Филиал == @branсhes & Парк == @depots').copy()
sani_violation_data_filtered['проверено_ТС'] = 1
sani_violation_data_filtered_unique_vehicles_gr = sani_violation_data_filtered.groupby(by=[
    'week_name', 'Наименование']).sum()[['Неудовлетворительное санитарное состояние ТС', 'проверено_ТС']].reset_index()
for col in ['Неудовлетворительное санитарное состояние ТС', 'проверено_ТС']:
    sani_violation_data_filtered_unique_vehicles_gr[col] = sani_violation_data_filtered_unique_vehicles_gr[col].apply(lambda x: 1 if x != 0 else x)
sani_violation_data_filtered_unique_vehicles_gr = sani_violation_data_filtered_unique_vehicles_gr.groupby(by=[
    'week_name']).sum()[['Неудовлетворительное санитарное состояние ТС', 'проверено_ТС']]
sani_violation_data_filtered_unique_vehicles_gr['Количество нарушений на 100 ТС'] = sani_violation_data_filtered_unique_vehicles_gr[
    'Неудовлетворительное санитарное состояние ТС'] / sani_violation_data_filtered_unique_vehicles_gr['проверено_ТС'] * 100

st.subheader('Количество нарушений требований к санитарному состоянию ТС, ед. (на 100 проверенных ТС)')
st.bar_chart(sani_violation_data_filtered_unique_vehicles_gr, y='Количество нарушений на 100 ТС')


# Territory -------------------------------------------------------------------------

terr_violation_data_filtered = get_territory_violation_data().query(
    'Перевозчик == @carrier & month == @months & Филиал == @branсhes & Парк == @depots').copy()
terr_violation_data_filtered = terr_violation_data_filtered.groupby(by=['week_name']).sum()[['Количество нарушений']]

st.subheader('Количество нарушений на территории и чрезвычайные происшествия, ед.')
st.bar_chart(terr_violation_data_filtered, y='Количество нарушений')
