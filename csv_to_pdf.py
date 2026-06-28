import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

df = pd.read_csv("submission.csv")

fig, ax = plt.subplots(figsize=(22, 35))
ax.axis("off")

col_widths = [0.18, 0.06, 0.08, 0.68]
headers = list(df.columns)

table_data = df.values.tolist()

table = ax.table(
    cellText=table_data,
    colLabels=headers,
    cellLoc="left",
    loc="center",
    colWidths=col_widths,
)

table.auto_set_font_size(False)
table.set_fontsize(7)
table.scale(1, 0.9)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_text_props(fontweight="bold", fontsize=8)
        cell.set_facecolor("#2c3e50")
        cell.set_text_props(color="white")
        cell.set_edgecolor("#555")
    else:
        cell.set_edgecolor("#ddd")
        if row % 2 == 0:
            cell.set_facecolor("#f5f5f5")
        else:
            cell.set_facecolor("white")

with PdfPages("submission.pdf") as pdf:
    pdf.savefig(fig, bbox_inches="tight")
    plt.close()

print("submission.pdf created successfully")
