import os
import pandas as pd
import numpy as np
# Required for basic python plotting functionality,
import matplotlib.pyplot as plt
# Required for formatting dates later in the case,
import datetime
import matplotlib.dates as mdates
# Required to display image inline,
from IPython.display import Image
# Advanced plotting functionality with seaborn
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


SECOP_I = pd.read_csv("SECOP_I_Contratos.csv")
SECOP_I.head()
SECOP_I.columns
SECOP_I.shape


main_var = SECOP_I.groupby(["Anno Cargue SECOP", 'Municipio Obtencion', "Tipo de Contrato"]).agg(
        {"Numero del Contrato":"nunique", "NIT de la Entidad":"nunique",
         "Cuantia Contrato":"sum", "Cuantia Proceso":"sum", "Valor Contrato con Adiciones":"sum"}).reset_index()
main_var["ratio"] = 100*((main_var["Valor Contrato con Adiciones"]/main_var["Cuantia Contrato"]) -1)

contrato_anio = SECOP_I.groupby(["Anno Cargue SECOP"]).agg(
        {"Numero del Contrato":"nunique", "Cuantia Proceso":"sum"}).reset_index()


estado_proc = SECOP_I.groupby(["Estado del Proceso"]).agg(
        {"Numero del Contrato":"nunique"}).reset_index().sort_values('Numero del Contrato')

tipo_contrato = SECOP_I.groupby(["Tipo de Contrato"]).agg(
        {"Numero del Contrato":"nunique", "Cuantia Proceso":"sum"
         }).reset_index().sort_values('Numero del Contrato')

departamento = SECOP_I.groupby(["Departamento Entidad"]).agg(
        {"Numero del Contrato":"nunique", "Cuantia Proceso":"sum"
         }).reset_index().sort_values('Numero del Contrato')





x = contrato_anio['Anno Cargue SECOP']
x_pos = [i for i, _ in enumerate(x)]
fig = plt.figure(figsize = (10,5))
plt.bar(x_pos, contrato_anio['Numero del Contrato'])
plt.xlabel("Year")
plt.ylabel("# of contracts")
plt.title("Contracts per year")
plt.xticks(x_pos, x)
plt.setp(plt.gca().get_xticklabels(), rotation=90, horizontalalignment='right')
fig.savefig("Yearly_number_of_contracts.png", paper = 'letter')
plt.show()


#x1 = estado_proc['Estado del Proceso'].apply(lambda x: x.split(' ')[0:3]).apply(lambda y: ' '.join(y))
x1 = estado_proc['Estado del Proceso']
x_pos = [i for i, _ in enumerate(x1)]
fig = plt.figure(figsize = (10,4))
plt.barh(x_pos, estado_proc['Numero del Contrato'], height = 0.9)
plt.ylabel("Status")
plt.xlabel("# of contracts")
plt.title("Contracts by Status of the contract")
plt.yticks(x_pos, x1)
plt.tight_layout()
fig.savefig("Contracts_by_status.png", paper = 'letter')
plt.show()


x = tipo_contrato['Tipo de Contrato']
x_pos = [i for i, _ in enumerate(x)]
fig = plt.figure(figsize = (10,4))
plt.barh(x_pos, tipo_contrato['Numero del Contrato'], height = 0.9)
plt.ylabel("Class")
plt.xlabel("# of contracts")
plt.title("Contracts by Class of the contract")
plt.yticks(x_pos, x)
plt.tight_layout()
fig.savefig("Contracts_by_class.png", paper = 'letter')
plt.show()




dataDepTail = departamento.head(18).copy()
dataDepTail['Departamento Entidad'] = ["Otros Departamentos"]*18
dataDepTail = dataDepTail.groupby('Departamento Entidad').agg(
        {"Numero del Contrato":"sum", "Cuantia Proceso":"sum"
         }).reset_index().sort_values('Numero del Contrato')
dataDepHead = departamento.tail(16).copy()
dataDep = pd.concat([dataDepTail, dataDepHead])
sizes = dataDep["Numero del Contrato"]
x = dataDep["Departamento Entidad"]

def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = int(round((pct*total/100.0))/1000)
        return '{v:,} K'.format(v=val)
    return my_format
fig1, ax1 = plt.subplots(figsize = (6,6))
ax1.pie(sizes, labels=x,
        shadow=True, startangle=90, autopct = autopct_format(sizes))
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
fig1.savefig("Contracts_by_departmen.png", paper = 'letter')
plt.show()



contract_Dept = SECOP_I.groupby(["Anno Cargue SECOP", "Departamento Entidad"]).agg(
        {"Numero del Contrato":"nunique"}).reset_index()

pivot_YD = contract_Dept.pivot("Anno Cargue SECOP", "Departamento Entidad", "Numero del Contrato")
# Heat map of energy consumption by month and year
fig, ax = plt.subplots(figsize=(15, 10))
sns.heatmap(pivot_YD, cmap="coolwarm", ax=ax)
ax.set_title("Contracts by Year and Department")
fig.savefig("Contracts_by_department and year.png", paper = 'letter')


# boxplots by year ------------------------------------------------------------

unique_years = main_var["Anno Cargue SECOP"].unique()
indicator = main_var["Tipo de Contrato"].unique()
for ind in indicator:
    df_list = []
    for year_cnt in unique_years:
        temp_df = main_var[
                (main_var["Anno Cargue SECOP"] == year_cnt) &
                (main_var["Tipo de Contrato"]==ind)]["Cuantia Contrato"].reset_index(
                drop=True
                )
        temp_df = temp_df.rename(
                columns={"Anno Cargue SECOP": "Año " + str(year_cnt)}
                )
        df_list.append(temp_df)
        plot_df = pd.concat(df_list, axis=1)
    # Box plots
    fig, ax = plt.subplots(figsize=(15, 5))
    cajasC = plot_df.boxplot(ax=ax, showfliers=False)
    cajasC.set_xticklabels(labels = unique_years, rotation=45)
    ax.set_xlabel("Year")
    ax.set_title('Loading year on SECOP I - Value of ' + str(ind) +' contracts per year')
    fig.savefig("contract_" + str(ind).replace(" ", "_") + ".png")

pd.options.display.width=20

unique_years = main_var["Anno Cargue SECOP"].unique()
df_list = []
for year_cnt in unique_years:
    temp_df = main_var[
            (main_var["Anno Cargue SECOP"] == year_cnt)][
                    "ratio"].reset_index(
            drop=True
            )
    temp_df = temp_df.rename(
            columns={"Anno Cargue SECOP": "Año " + str(year_cnt)}
            )
    df_list.append(temp_df)
    plot_df = pd.concat(df_list, axis=1)
# Box plots
fig, ax = plt.subplots(figsize=(15, 5))
cajasC = plot_df.boxplot(ax=ax, showfliers=False)
cajasC.set_xticklabels(labels = unique_years, rotation=45)
ax.set_xlabel("Year")
ax.set_title('Yearly Comparisson between inital and final contract value (Percent difference)')
fig.savefig("Yearly_Variation_ini_final.png")


mpa_plot_db = SECOP_I.groupby("Departamento Entidad").agg(
        {"Numero del Contrato":"nunique", "NIT de la Entidad":"nunique",
         "Identificacion del Contratista":"nunique",
         "Cuantia Contrato":"sum", "Cuantia Proceso":"sum", "Valor Contrato con Adiciones":"sum"}).reset_index()

