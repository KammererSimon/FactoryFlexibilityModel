import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

filepath = "C:\\Users\\smsikamm\\PycharmProjects\\DRI_Study\\simulations\\output_data\\DRI_Auswertung.xlsx"
x_parameter = "cost_natural_gas"
y_parameter = "avg_cost_electricity"
z_parameter = "cost_per_ton"
plants = ["CCS", "Hydrogen", "Partial"]
df = pd.read_excel(filepath)
df = df.drop(df.index[0])

# filter scenarios for a specific co2 price
df = df[df["co2_per_ton"] <= 1].copy()

matrix_dict = {}
grouped = df.groupby('Layout')


for plant in plants:
    # Filtere den DataFrame für das aktuelle Plantlayout
    plant_df = grouped.get_group(plant)

    # Berechne den Durchschnitt für jedes eindeutige Paar von x_parameter und y_parameter
    avg_matrix = plant_df.pivot_table(values=z_parameter, index=x_parameter, columns=y_parameter, aggfunc='mean')

    # Fehlende Werte (NaN) durch 0 ersetzen
    avg_matrix = avg_matrix.fillna(0)

    # Die Matrix zum Dictionary hinzufügen
    matrix_dict[plant] = avg_matrix

min_value = np.min([matrix for matrix in matrix_dict.values()])
max_value = np.max([matrix for matrix in matrix_dict.values()])

# Erstelle eine leere Matrix für die RGB-Bild-Darstellung
rgb_image = np.zeros((matrix_dict[plant].shape[0], matrix_dict[plant].shape[1], 3), dtype=np.uint8)

# Iteriere über die Werte in result_matrix und setze die Farben entsprechend
for i in range(matrix_dict[plant].shape[0]):
    for j in range(matrix_dict[plant].shape[1]):
        max_value = max(matrix_dict["CCS"].iloc[i, j], matrix_dict["Hydrogen"].iloc[i, j], matrix_dict["Partial"].iloc[i, j])
        ccs_value = (max_value - matrix_dict["CCS"].iloc[i, j])
        h2_value = (max_value - matrix_dict["Hydrogen"].iloc[i, j])
        part_value = (max_value - matrix_dict["Partial"].iloc[i, j])

        pixel_max = max(ccs_value, h2_value, part_value)
        rgb_image[i, j, :] = [ccs_value * 255 / pixel_max,
                              h2_value * 255 / pixel_max,
                              part_value * 255 / pixel_max]

plt.imshow(rgb_image)
plt.title(f"Technology with lowest {z_parameter} on average")
plt.xlabel(y_parameter)
plt.ylabel(x_parameter)
x_ticks = matrix_dict["CCS"].columns
y_ticks = matrix_dict["CCS"].index
plt.xticks(range(len(x_ticks)), x_ticks, rotation=90)
plt.yticks(range(len(y_ticks)), y_ticks)
plt.show()




