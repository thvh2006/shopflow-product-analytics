import json
import os
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".cache" / "matplotlib"))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "shopflow.duckdb"
REPORT_DIRECTORY = PROJECT_ROOT / "reports" / "generated"
FIGURE_DIRECTORY = PROJECT_ROOT / "reports" / "figures"


COLORS = {"navy": "#16324F", "blue": "#2A6FBB", "teal": "#2A9D8F", "coral": "#E76F51"}


def _style() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update({"figure.dpi": 140, "savefig.bbox": "tight", "font.family": "DejaVu Sans"})


def build_funnel(connection: duckdb.DuckDBPyConnection) -> None:
    qualified, cart, purchase = connection.execute(
        """
        SELECT
            count(*) FILTER (WHERE qualified_session),
            count(*) FILTER (WHERE reached_cart),
            count(*) FILTER (WHERE reached_purchase)
        FROM mart_session_funnel
        """
    ).fetchone()
    labels = ["Qualified view", "Reached cart", "Reached purchase"]
    values = [qualified, cart, purchase]
    figure, axis = plt.subplots(figsize=(10, 5.5))
    bars = axis.barh(labels[::-1], values[::-1], color=[COLORS["teal"], COLORS["blue"], COLORS["navy"]])
    axis.set_title("Most qualified sessions do not reach cart")
    axis.set_xlabel("Analytics sessions")
    axis.bar_label(bars, labels=[f"{value:,}" for value in values[::-1]], padding=8, fontsize=11)
    sns.despine(left=True, bottom=True)
    figure.savefig(FIGURE_DIRECTORY / "01_session_funnel.png")
    plt.close(figure)


def build_price_heatmap(connection: duckdb.DuckDBPyConnection) -> None:
    frame = connection.execute(
        """
        SELECT category_level_1, price_band, cart_to_purchase_rate
        FROM mart_category_price_funnel
        WHERE viewed_session_products >= 1000
            AND category_level_1 IN ('computers', 'electronics', 'stationery', 'unknown')
        """
    ).df()
    order = ["Q1 lowest price", "Q2 lower-middle price", "Q3 upper-middle price", "Q4 highest price"]
    matrix = frame.pivot(index="category_level_1", columns="price_band", values="cart_to_purchase_rate")
    matrix = matrix.reindex(columns=order)
    figure, axis = plt.subplots(figsize=(12, 5.5))
    sns.heatmap(matrix * 100, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={"label": "%"}, ax=axis)
    axis.set_title("Cart completion declines in higher price bands")
    axis.set_xlabel("Global price quartile")
    axis.set_ylabel("Category")
    axis.set_xticklabels(["Q1", "Q2", "Q3", "Q4"])
    figure.savefig(FIGURE_DIRECTORY / "02_category_price_completion.png")
    plt.close(figure)


def build_subcategory_opportunity(connection: duckdb.DuckDBPyConnection) -> None:
    frame = connection.execute(
        """
        SELECT *
        FROM mart_computer_subcategory_funnel
        WHERE viewed_session_products >= 1000
            AND ordered_cart_session_products >= 100
        """
    ).df()
    figure, axis = plt.subplots(figsize=(10, 7))
    sns.scatterplot(
        data=frame,
        x="ordered_cart_session_products",
        y="cart_to_purchase_rate",
        size="observed_purchase_item_value",
        sizes=(80, 900),
        color=COLORS["blue"],
        alpha=0.7,
        legend=False,
        ax=axis,
    )
    for row in frame.nlargest(6, "ordered_cart_session_products").itertuples():
        label = row.category_code.replace("computers.", "")
        axis.annotate(label, (row.ordered_cart_session_products, row.cart_to_purchase_rate), fontsize=9)
    axis.axhline(frame["cart_to_purchase_rate"].median(), color=COLORS["coral"], linestyle="--", linewidth=1)
    axis.set_title("Video cards combine scale, value, and low cart completion")
    axis.set_xlabel("Ordered cart session-products")
    axis.set_ylabel("Cart → purchase rate")
    axis.yaxis.set_major_formatter(lambda value, _: f"{value:.0%}")
    sns.despine()
    figure.savefig(FIGURE_DIRECTORY / "03_computer_opportunity.png")
    plt.close(figure)


def build_experiment_effect() -> None:
    results = json.loads((REPORT_DIRECTORY / "experiment_healthy_results.json").read_text())
    primary = results["primary_conversion"]
    point = primary["absolute_effect"] * 100
    lower = primary["ci_low"] * 100
    upper = primary["ci_high"] * 100
    figure, axis = plt.subplots(figsize=(9, 3.8))
    axis.errorbar(
        point,
        0,
        xerr=[[point - lower], [upper - point]],
        fmt="o",
        markersize=10,
        color=COLORS["teal"],
        capsize=7,
        linewidth=2.5,
    )
    axis.axvline(0, color="#666666", linewidth=1)
    axis.axvline(2.15, color=COLORS["coral"], linestyle="--", linewidth=1.5, label="Planning MDE")
    axis.set_yticks([])
    axis.set_xlabel("Absolute conversion effect (percentage points)")
    axis.set_title("Synthetic treatment clears zero and the planning MDE")
    axis.legend(frameon=False, loc="lower right")
    sns.despine(left=True)
    figure.savefig(FIGURE_DIRECTORY / "04_experiment_effect.png")
    plt.close(figure)


def build_session_sensitivity(connection: duckdb.DuckDBPyConnection) -> None:
    frame = connection.execute(
        "SELECT * FROM mart_session_threshold_sensitivity ORDER BY inactivity_minutes"
    ).df()
    figure, axis = plt.subplots(figsize=(9, 5.5))
    axis.plot(
        frame["inactivity_minutes"],
        frame["view_to_cart_rate"] * 100,
        marker="o",
        linewidth=2.5,
        label="View → cart",
        color=COLORS["blue"],
    )
    axis.plot(
        frame["inactivity_minutes"],
        frame["view_to_purchase_rate"] * 100,
        marker="o",
        linewidth=2.5,
        label="View → purchase",
        color=COLORS["teal"],
    )
    axis.set_title("Core rates are stable across session thresholds")
    axis.set_xlabel("Inactivity threshold (minutes)")
    axis.set_ylabel("Qualified-session conversion (%)")
    axis.set_xticks(frame["inactivity_minutes"])
    axis.legend(frameon=False)
    sns.despine()
    figure.savefig(FIGURE_DIRECTORY / "05_session_threshold_sensitivity.png")
    plt.close(figure)


def build_adjusted_odds() -> None:
    frame = pd.read_csv(REPORT_DIRECTORY / "cart_completion_model.csv")
    frame = frame.loc[frame["term"].str.contains("price_quartile")].copy()
    frame["quartile"] = frame["term"].str.extract(r"\[T\.(Q\d)\]")
    frame = frame.sort_values("quartile", ascending=False)
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.errorbar(
        frame["odds_ratio"],
        frame["quartile"],
        xerr=[frame["odds_ratio"] - frame["ci_low"], frame["ci_high"] - frame["odds_ratio"]],
        fmt="o",
        color=COLORS["blue"],
        capsize=6,
        markersize=9,
    )
    axis.axvline(1, color="#777777", linewidth=1.2, linestyle="--")
    axis.set_title("Higher price remains associated with lower cart completion")
    axis.set_xlabel("Adjusted odds ratio versus Q1 (95% CI)")
    axis.set_ylabel("Global price quartile")
    sns.despine()
    figure.savefig(FIGURE_DIRECTORY / "06_adjusted_price_odds.png")
    plt.close(figure)


def build_power_curve() -> None:
    frame = pd.read_csv(REPORT_DIRECTORY / "power_curve.csv")
    figure, axis = plt.subplots(figsize=(9, 5.5))
    axis.plot(
        frame["relative_lift"] * 100,
        frame["total_users"],
        marker="o",
        color=COLORS["coral"],
        linewidth=2.5,
    )
    target = frame.loc[frame["relative_lift"] == 0.05].iloc[0]
    axis.scatter([5], [target["total_users"]], s=130, color=COLORS["navy"], zorder=3)
    axis.annotate(
        f"Plan: {int(target['total_users']):,} users",
        (5, target["total_users"]),
        xytext=(12, 20),
        textcoords="offset points",
        fontsize=11,
    )
    axis.set_title("Small effects require disproportionately larger experiments")
    axis.set_xlabel("Relative lift to detect (%)")
    axis.set_ylabel("Total users for 80% power")
    sns.despine()
    figure.savefig(FIGURE_DIRECTORY / "07_power_curve.png")
    plt.close(figure)


def build_heterogeneity() -> None:
    results = json.loads((REPORT_DIRECTORY / "experiment_healthy_results.json").read_text())
    heterogeneity = results["heterogeneity"]
    labels = ["First-observed", "Returning", "Days 1–2", "Days 3–14"]
    keys = ["first_observed_users", "returning_users", "days_1_2", "days_3_14"]
    frame = pd.DataFrame(
        [
            {
                "label": label,
                "effect": heterogeneity[key]["absolute_effect"] * 100,
                "lower": heterogeneity[key]["ci_low"] * 100,
                "upper": heterogeneity[key]["ci_high"] * 100,
            }
            for label, key in zip(labels, keys, strict=True)
        ]
    )
    frame = frame.iloc[::-1]
    figure, axis = plt.subplots(figsize=(9, 5.5))
    axis.errorbar(
        frame["effect"],
        frame["label"],
        xerr=[frame["effect"] - frame["lower"], frame["upper"] - frame["effect"]],
        fmt="o",
        capsize=5,
        markersize=8,
        color=COLORS["teal"],
    )
    axis.axvline(0, color="#777777", linewidth=1.2)
    axis.set_title("Exploratory slices are compatible with one pooled effect")
    axis.set_xlabel("Absolute conversion effect (percentage points)")
    axis.set_ylabel("")
    sns.despine(left=True)
    figure.savefig(FIGURE_DIRECTORY / "08_experiment_heterogeneity.png")
    plt.close(figure)


def main() -> None:
    _style()
    FIGURE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
        build_funnel(connection)
        build_price_heatmap(connection)
        build_subcategory_opportunity(connection)
        build_session_sensitivity(connection)
    build_experiment_effect()
    build_adjusted_odds()
    build_power_curve()
    build_heterogeneity()
    print(f"Built portfolio figures in {FIGURE_DIRECTORY}")


if __name__ == "__main__":
    main()
