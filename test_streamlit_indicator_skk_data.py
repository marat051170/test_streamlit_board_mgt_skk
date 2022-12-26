import pandas as pd
import plotly.express as px
import streamlit as st
import altair as alt


# Data ----------------------------------------------------------------------------

@st.cache
def get_bans_data():
    df = pd.read_excel('test_indicator_banned_for_exploitation.xlsx')
    return df

@st.cache
def get_driver_violations_data():
    df = pd.read_excel('test_indicator_driver_violation.xlsx')
    return df

@st.cache
def get_sani_violation_data():
    df = pd.read_excel('test_indicator_sanitary_condition_violations.xlsx')
    return df

@st.cache
def get_territory_violation_data():
    df = pd.read_excel('test_indicator_territory_violations.xlsx')
    return df

# ---------------------------------------------------------------------------------


def add_empty_rows(n):
    for i in range(1, n+1):
        st.markdown('#')

# ---------------------------------------------------------------------------------

st.set_page_config(page_title='СКК', page_icon=':bar_chart:', layout='wide')
st.sidebar.header('Фильтры')


# Filters -------------------------------------------------------------------------

cols_for_filters = ['week_name']
filters_values = pd.concat([get_bans_data()[cols_for_filters], get_driver_violations_data()[cols_for_filters]], sort=False).drop_duplicates()
filters_values = pd.concat([filters_values, get_sani_violation_data()[cols_for_filters]], sort=False).drop_duplicates()
filters_values = pd.concat([filters_values, get_territory_violation_data()[cols_for_filters]], sort=False).drop_duplicates()

week = st.sidebar.selectbox('Неделя:', options=sorted(filters_values['week_name'].unique(), reverse=True))
filters_values_weeks = filters_values.query('week_name == @week')


# ---------------------------------------------------------------------------------

st.title(f"4: Соблюдение требований ГКУ ОП за {week.split('_')[1]}")
st.markdown('***ВНИМАНИЕ! Дорабатывается и дополняется для валидации, целевой дэшборд будет иметь другой вид !***')

add_empty_rows(2)

# Bans & Sanitary violations ------------------------------------------------------

bans_filtered = get_bans_data()
bans_gr = bans_filtered.pivot_table(index=['week_name', 'Филиал'], values=['проверено', 'запрет'], aggfunc='sum').reset_index()
sans_filtered = get_sani_violation_data()
sans_gr = sans_filtered.pivot_table(
    index=['week_name', 'Филиал'], values=['проверено', 'санитарное_состояние'], aggfunc='sum').reset_index()
data = pd.merge(bans_gr, sans_gr.drop('проверено', axis=1), on=['week_name', 'Филиал'], how='left')
data['всего_нарушений'] = data['запрет'] + data['санитарное_состояние']
data['запрет'] = data['запрет'] / data['проверено'] * 100
data['санитарное_состояние'] = data['санитарное_состояние'] / data['проверено'] * 100
data['week_number'] = data['week_name'].apply(lambda x: int(x.split('_')[0]))
for col in ['запрет', 'санитарное_состояние']:
    data[col] = data[col].apply(lambda x: round(x, 1))

graph_data = data.query('week_name == @week').copy()
graph_data = pd.melt(graph_data, id_vars=['week_number', 'week_name', 'Филиал', 'проверено', 'всего_нарушений'])
graph_data['variable'] = graph_data['variable'].replace('санитарное_состояние', 'сан_сост.', regex=True)
graph_data['Филиал'] = graph_data['Филиал'] + ' (' + graph_data['всего_нарушений'].astype(int).astype(str) + ')'

select_week = alt.selection_single(init={'week_number': int(week.split('_')[0])})
pink_blue = alt.Scale(domain=('запрет', 'сан_сост.'), range=["steelblue", "salmon"])
chart = alt.Chart(graph_data).mark_bar().encode(
    x=alt.X('variable:N', title=None),
    y=alt.Y('value:Q', scale=alt.Scale(domain=(0, max(graph_data['value'])))),
    color=alt.Color('variable:N', scale=pink_blue, legend=None),
    column='Филиал:O'
    ).properties(
        width=125
    ).add_selection(
        select_week
    ).transform_calculate(
        "Нарушение", alt.expr.if_(alt.datum.variable == 'запрет', "Запрет", "Сан. состояние")
    ).transform_filter(
        select_week
    ).configure_facet(
        spacing=8
    )


curr_week_number = int(week.split('_')[0])
prev_week_number = (curr_week_number - 1) if curr_week_number - 1 != 1 else 52
metric_data = data.query('week_number == @curr_week_number | week_number == @prev_week_number').copy()
metric_data['prev_curr_week'] = metric_data['week_number'].apply(lambda x: 'curr' if x == curr_week_number else 'prev')
metric_data['нарушений_100_ТС'] = metric_data['запрет'] + metric_data['санитарное_состояние']
metric_data = metric_data.pivot_table(index='Филиал', columns='prev_curr_week', values='нарушений_100_ТС', aggfunc='sum').reset_index()
metric_data['delta'] = metric_data['curr'] - metric_data['prev']
metric_data = metric_data.sort_values('curr', ascending=False)



# Driver violations ---------------------------------------------------------------

driver_violations = get_driver_violations_data()
dr_data = driver_violations.pivot_table(
    index=['week_name', 'Филиал'], values=['проверено', 'замечание_водителю_корп_форма'], aggfunc='sum').reset_index()
dr_data['week_number'] = dr_data['week_name'].apply(lambda x: int(x.split('_')[0]))
graph_dr_data = dr_data.query('week_name == @week').copy()


metric_dr_data = dr_data.query('week_number == @curr_week_number | week_number == @prev_week_number').copy()
metric_dr_data['prev_curr_week'] = metric_dr_data['week_number'].apply(lambda x: 'curr' if x == curr_week_number else 'prev')
metric_dr_data = metric_dr_data.pivot_table(
    index='Филиал', columns='prev_curr_week', values='замечание_водителю_корп_форма', aggfunc='sum').reset_index()
metric_dr_data['delta'] = metric_dr_data['curr'] - metric_dr_data['prev']
metric_dr_data = metric_dr_data.sort_values('curr', ascending=False)


# Territory violations-------------------------------------------------------------

terr_violations = get_territory_violation_data()
terr_data = terr_violations.pivot_table(
    index=['week_name', 'Филиал'], values='Количество нарушений', aggfunc='sum').reset_index()
terr_data['week_number'] = terr_data['week_name'].apply(lambda x: int(x.split('_')[0]))
graph_terr_data = terr_data.query('week_name == @week').copy()
terr_chart = alt.Chart(graph_terr_data).mark_bar(color='grey').encode(x='Филиал', y='Количество нарушений').properties(width=855)

metric_terr_data = terr_data.query('week_number == @curr_week_number | week_number == @prev_week_number').copy()
metric_terr_data['prev_curr_week'] = metric_terr_data['week_number'].apply(lambda x: 'curr' if x == curr_week_number else 'prev')
metric_terr_data = metric_terr_data.pivot_table(
    index='Филиал', columns='prev_curr_week', values='Количество нарушений', aggfunc='sum').reset_index()
metric_terr_data['delta'] = metric_terr_data['curr'] - metric_terr_data['prev']
metric_terr_data = metric_terr_data.sort_values('curr', ascending=False)


col1, col2, col3 = st.columns([4, 1, 2], gap='small')
with col1:
    st.markdown('**Количество замечаний к ТС, на проверенных 100 ТС**')
    st.altair_chart(chart, theme='streamlit')
    add_empty_rows(1)
    st.markdown('**Количество замечаний к водителям в части ношения корпорпоративной формы**')
    st.bar_chart(graph_dr_data, x='Филиал', y='замечание_водителю_корп_форма')
    add_empty_rows(1)
    st.markdown('**Количество замечаний к состоянию площадок**')
    st.altair_chart(terr_chart, theme="streamlit")

with col3:
    st.markdown('**Худшие показатели по филиалам**')
    st.write('По количеству нарушений на 100 проверенных ТС')
    st.metric(
        label=metric_data['Филиал'].iloc[0],
        value=int(round(metric_data['curr'].iloc[0], 0)),
        delta=int(round(metric_data['delta'].iloc[0], 0)),
        delta_color='inverse')
    add_empty_rows(1)
    st.metric(
        label=metric_data['Филиал'].iloc[1],
        value=int(round(metric_data['curr'].iloc[1], 0)),
        delta=int(round(metric_data['delta'].iloc[1], 0)),
        delta_color='inverse')
    add_empty_rows(1)
    st.metric(
        label=metric_data['Филиал'].iloc[2],
        value=int(round(metric_data['curr'].iloc[2], 0)),
        delta=int(round(metric_data['delta'].iloc[2], 0)),
        delta_color='inverse')
    add_empty_rows(1)
    st.write('По количеству замечаний к водителям')
    st.metric(
        label=metric_dr_data['Филиал'].iloc[0],
        value=int(round(metric_dr_data['curr'].iloc[0], 0)),
        delta=int(round(metric_dr_data['delta'].iloc[0], 0)),
        delta_color='inverse')
    add_empty_rows(1)
    st.metric(
        label=metric_dr_data['Филиал'].iloc[1],
        value=int(round(metric_dr_data['curr'].iloc[1], 0)),
        delta=int(round(metric_dr_data['delta'].iloc[1], 0)),
        delta_color='inverse')
    add_empty_rows(1)
    st.metric(
        label=metric_dr_data['Филиал'].iloc[2],
        value=int(round(metric_dr_data['curr'].iloc[2], 0)),
        delta=int(round(metric_dr_data['delta'].iloc[2], 0)),
        delta_color='inverse')
    add_empty_rows(1)
    st.write('По количеству замечаний к площадкам')
    st.metric(
        label=metric_terr_data['Филиал'].iloc[0],
        value=int(round(metric_terr_data['curr'].iloc[0], 0)),
        delta=int(round(metric_terr_data['delta'].iloc[0], 0)),
        delta_color='inverse')
    add_empty_rows(1)
    st.metric(
        label=metric_terr_data['Филиал'].iloc[1],
        value=int(round(metric_terr_data['curr'].iloc[1], 0)),
        delta=int(round(metric_terr_data['delta'].iloc[1], 0)),
        delta_color='inverse')
    add_empty_rows(1)
    st.metric(
        label=metric_terr_data['Филиал'].iloc[2],
        value=int(round(metric_terr_data['curr'].iloc[2], 0)),
        delta=int(round(metric_terr_data['delta'].iloc[2], 0)),
        delta_color='inverse')
    add_empty_rows(1)

