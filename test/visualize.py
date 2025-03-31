# visualize.py
import matplotlib.pyplot as plt

def generate_visuals(funnel_data):
    try:
        if not funnel_data or "stages" not in funnel_data or "counts" not in funnel_data:
            raise ValueError("Invalid funnel data for visualization")
        
        plt.figure(figsize=(10, 6))
        plt.bar(funnel_data["stages"], funnel_data["counts"], color="skyblue")
        plt.title("Funnel Drop-off Analysis")
        plt.xlabel("Stages")
        plt.ylabel("User Count")
        plt.xticks(rotation=45)
        chart_path = "funnel_chart.png"
        plt.savefig(chart_path, bbox_inches="tight")
        plt.close()
        print(f"Saved bar chart to {chart_path}")
        
        table_data = [["Stage", "Count", "Drop-off %"]] + [
            [stage, count, f"{dropoff:.1f}" if i < len(funnel_data["dropoffs"]) else "N/A"]
            for i, (stage, count, dropoff) in enumerate(zip(funnel_data["stages"], funnel_data["counts"], funnel_data["dropoffs"] + [0]))
        ]
        with open("funnel_table.json", "w") as f:
            json.dump(table_data, f, indent=4)
        print("Saved table data to funnel_table.json")
        
        return {"chart": chart_path, "table": table_data}
    except Exception as e:
        print(f"Failed to generate visuals: {str(e)}")
        return None